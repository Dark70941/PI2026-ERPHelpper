"""
test_api.py - Script de Teste Automatizado do ERP Helpper
Permite validar o funcionamento das rotas /health e /search (Local ou AWS) e do Webhook do n8n.
"""
import sys
import json
import urllib.request
import urllib.error

DEFAULT_LOCAL_BASE = "http://127.0.0.1:5000"
DEFAULT_AWS_BASE = "http://SEU_IP_AWS:5000"
DEFAULT_N8N_URL = "https://seu-n8n.exemplo.com/webhook/seu-webhook-id"

def testar_health(base_url, nome="Health Check"):
    url = f"{base_url.rstrip('/')}/health"
    print(f"\n" + "=" * 60)
    print(f"Testando {nome}: {url}")
    print("=" * 60)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            print(f"✅ Status HTTP: {status}")
            print(f"Status da Aplicação: {data.get('status')}")
            print(f"Versão: {data.get('version')}")
            print(f"Ambiente: {data.get('environment')}")
            print(f"Uptime: {data.get('uptime_seconds')}s")
            print(f"Database: {json.dumps(data.get('database', {}), ensure_ascii=False)}")
            assert data.get("status") == "UP", "Health Check retornou status diferente de UP"
            return True
    except Exception as e:
        print(f"❌ Falha no Health Check: {str(e)}")
        return False

def testar_endpoint(url, payload, nome="Endpoint"):
    print(f"\n" + "=" * 60)
    print(f"Testando {nome}: {url}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False)}")
    print("=" * 60)
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            body = resp.read().decode("utf-8")
            print(f"✅ Status HTTP: {status}")
            try:
                parsed = json.loads(body)
                print(f"Retorno recebido com sucesso! ({len(parsed)} registros ou campos)")
                print(json.dumps(parsed, indent=2, ensure_ascii=False)[:500] + "\n...")
            except json.JSONDecodeError:
                print(f"Retorno bruto: {body[:300]}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ Erro HTTP {e.code}: {e.reason}")
        print(e.read().decode("utf-8", errors="ignore")[:300])
        return False
    except urllib.error.URLError as e:
        print(f"⚠️ Falha de Conexão: {e.reason}")
        return False
    except Exception as e:
        print(f"⚠️ Erro inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    query_teste = {"pergunta": "Como tratar a rejeição 201?"}
    
    alvo = sys.argv[1].lower() if len(sys.argv) > 1 else "local"
    
    if alvo == "aws":
        testar_health(DEFAULT_AWS_BASE, "Health Check AWS")
        testar_endpoint(f"{DEFAULT_AWS_BASE}/search", query_teste, "Search API na AWS")
    elif alvo == "n8n":
        testar_endpoint(DEFAULT_N8N_URL, query_teste, "Webhook do n8n")
    elif alvo == "health":
        sucesso = testar_health(DEFAULT_LOCAL_BASE, "Health Check Local")
        sys.exit(0 if sucesso else 1)
    else:
        print("Executando validação local (Health Check + Search)...")
        h_ok = testar_health(DEFAULT_LOCAL_BASE, "Health Check Local")
        s_ok = testar_endpoint(f"{DEFAULT_LOCAL_BASE}/search", query_teste, "Search API Local")
        if not (h_ok and s_ok):
            print("\n💡 Dica: Verifique se 'python main.py' está rodando na porta 5000.")
            print("Para testar apenas o health check: python test_api.py health")
            print("Para testar a AWS diretamente: python test_api.py aws")
            print("Para testar o n8n diretamente: python test_api.py n8n")
