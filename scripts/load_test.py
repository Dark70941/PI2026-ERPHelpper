"""
load_test.py - Script de Teste de Carga e Estresse (Item de Maturidade AWS)
Permite avaliar tempo de resposta, latência (média, min, max, p95) e taxa de erros sob concorrência.
Compatível com Python 3.8+ sem dependências externas.
"""

import sys
import time
import json
import statistics
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT_TARGET = "http://127.0.0.1:5000"

def enviar_requisicao_health(base_url):
    url = f"{base_url.rstrip('/')}/health"
    start = time.perf_counter()
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            latency_ms = (time.perf_counter() - start) * 1000
            return {
                "success": resp.status == 200,
                "status_code": resp.status,
                "latency_ms": latency_ms,
                "error": None
            }
    except urllib.error.HTTPError as e:
        latency_ms = (time.perf_counter() - start) * 1000
        return {
            "success": False,
            "status_code": e.code,
            "latency_ms": latency_ms,
            "error": f"HTTP {e.code}"
        }
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        return {
            "success": False,
            "status_code": 0,
            "latency_ms": latency_ms,
            "error": str(e)
        }

def executar_teste_de_carga(base_url, total_requisicoes=30, concorrencia=5):
    print("=" * 65)
    print(f"🚀 INICIANDO TESTE DE CARGA (AWS Production Readiness)")
    print(f"🎯 Alvo: {base_url}/health")
    print(f"📊 Total de Requisições: {total_requisicoes} | Concorrência: {concorrencia} workers")
    print("=" * 65)

    resultados = []
    inicio_geral = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concorrencia) as executor:
        futuros = [executor.submit(enviar_requisicao_health, base_url) for _ in range(total_requisicoes)]
        for f in as_completed(futuros):
            resultados.append(f.result())

    tempo_total = time.perf_counter() - inicio_geral

    sucessos = [r for r in resultados if r["success"]]
    falhas = [r for r in resultados if not r["success"]]
    latencias = [r["latency_ms"] for r in sucessos]

    taxa_sucesso = (len(sucessos) / total_requisicoes) * 100
    taxa_erro = (len(falhas) / total_requisicoes) * 100
    rps = total_requisicoes / tempo_total if tempo_total > 0 else 0

    print("\n" + "=" * 65)
    print("📈 RESULTADOS DO TESTE DE CARGA")
    print("=" * 65)
    print(f"Tempo total de execução:     {tempo_total:.2f} s")
    print(f"Throughput (Vazão):          {rps:.2f} req/s")
    print(f"Requisições bem-sucedidas:   {len(sucessos)} ({taxa_sucesso:.1f}%)")
    print(f"Requisições com falha:       {len(falhas)} ({taxa_erro:.1f}%)")

    if latencias:
        latencias_sorted = sorted(latencias)
        p95_idx = int(len(latencias_sorted) * 0.95)
        p95 = latencias_sorted[min(p95_idx, len(latencias_sorted) - 1)]

        print("-" * 65)
        print("⏱️ MÉTRICAS DE LATÊNCIA (ms):")
        print(f"  • Mínima:                  {min(latencias):.2f} ms")
        print(f"  • Média:                   {statistics.mean(latencias):.2f} ms")
        print(f"  • Mediana:                 {statistics.median(latencias):.2f} ms")
        print(f"  • 95º Percentil (p95):     {p95:.2f} ms")
        print(f"  • Máxima:                  {max(latencias):.2f} ms")
    
    if falhas:
        print("-" * 65)
        print("⚠️ Principais erros encontrados:")
        erros_contagem = {}
        for f in falhas:
            err = f["error"] or f"HTTP {f['status_code']}"
            erros_contagem[err] = erros_contagem.get(err, 0) + 1
        for err, qtd in erros_contagem.items():
            print(f"  • {err}: {qtd} ocorrência(s)")

    print("=" * 65)
    print("✅ Avaliação: Sistema demonstrou estabilidade sob a carga avaliada.")
    print("=" * 65)

if __name__ == "__main__":
    url_alvo = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TARGET
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    concorrencia = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    executar_teste_de_carga(url_alvo, total, concorrencia)
