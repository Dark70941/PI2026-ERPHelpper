# 🚀 Guia Passo a Passo: Deploy via AWS CloudFormation (IaC)
## ERP Helpper — Projeto Integrador FATEC (Computação em Nuvem)

> 📌 **Objetivo deste manual:**  
> Permitir que **qualquer integrante da equipe** consiga provisionar toda a infraestrutura da Search API (EC2, Docker, Segurança, Storage e Monitoramento) na sua própria conta do **AWS Academy** em menos de 5 minutos, utilizando o arquivo de **Infraestrutura como Código (CloudFormation)** já pronto no repositório.

---

## 📋 Pré-requisitos
Antes de começar, certifique-se de que você possui:
1. Acesso ao **AWS Academy Learner Lab** com créditos ativos.
2. O repositório clonado no seu computador ou o arquivo [`cloudformation/aws-infrastructure.yaml`](cloudformation/aws-infrastructure.yaml) baixado.
3. Sua chave de API da **OpenAI** (`OPENAI_API_KEY`) para habilitar o motor de IA.

---

## 🧭 Passo a Passo no Console AWS

### 1. Acessar o Console AWS no AWS Academy
1. Entre no seu laboratório no **AWS Academy Canvas** e clique no botão verde **Start Lab**.
2. Quando o ícone ao lado de *AWS* ficar verde (ativo), clique em **AWS Details** e depois no link **AWS Console**.
3. **MUITO IMPORTANTE:** No canto superior direito da barra da AWS, confirme que a região selecionada é **Norte da Virgínia (`us-east-1`)**.

---

### 2. Acessar o Serviço AWS CloudFormation
1. Na barra de pesquisa superior da AWS, digite **CloudFormation** e clique no serviço.
2. No canto superior direito da página do CloudFormation, clique no botão laranja:
   👉 **Criar pilha** (*Create stack*) ➔ **Com novos recursos (padrão)** (*With new resources (standard)*).

---

### 3. Fazer o Upload do Template IaC
Na tela de preparação do modelo (*Prerequisite - Prepare template*):
1. Em **Preparar modelo**, selecione: **O modelo está pronto** (*Template is ready*).
2. Em **Origem do modelo**, selecione: **Carregar um arquivo de modelo** (*Upload a template file*).
3. Clique no botão **Escolher arquivo** (*Choose file*).
4. No seu computador, navegue até a pasta do projeto e selecione o arquivo:
   📂 `chatBotAWS1/cloudformation/aws-infrastructure.yaml`
5. Clique no botão laranja **Próximo** (*Next*) no final da página.

---

### 4. Configurar os Parâmetros da Pilha
Preencha exatamente como descrito abaixo:
- **Nome da pilha** (*Stack name*): `erp-helpper-stack`
- **EnvironmentName**: mantenha `dev`
- **InstanceType**: mantenha `t3.micro` (ou `t2.micro`)
- **KeyName**: no campo suspenso, selecione **`vockey`**  
  *(A `vockey` é a chave oficial gerada automaticamente pelo AWS Academy para sua conta).*
- Clique no botão laranja **Próximo** (*Next*).

---

### 5. Configurar Opções da Pilha e Revisar
1. Na tela **Configurar opções da pilha** (*Configure stack options*), não altere nada. Apenas role até o final e clique em **Próximo** (*Next*).
2. Na tela de **Revisão** (*Review*), role até o final da página.
3. Se houver uma caixa de seleção com um aviso de recursos IAM:
   > ☑️ *"Eu reconheço que o AWS CloudFormation pode criar recursos do IAM com nomes personalizados..."*
   Marque essa caixinha de autorização.
4. Clique no botão laranja **Enviar** (*Submit* ou *Criar pilha*).

---

### 6. Acompanhar a Criação (Dicas sobre Telas da AWS)

> ⚠️ **Aviso sobre alertas vermelhos no topo:**  
> Podem aparecer 1 ou 2 alertas vermelhos no topo dizendo `User ... is not authorized to perform: codestar-connections:...`.  
> **Não se preocupe, isso NÃO é erro da sua máquina!** É apenas o painel da AWS tentando verificar um recurso chamado Git Sync que o AWS Academy bloqueia por padrão. Pode fechar os avisos no `X`.

1. A criação levará cerca de **2 a 3 minutos**.
2. **Entendendo a aba "Eventos":** A aba *Eventos* é um histórico cronológico de log. As linhas azuis `CREATE_IN_PROGRESS` mostram o que *começou*, e as linhas verdes `CREATE_COMPLETE` mostram o que *terminou*.
3. Atualize a página no botão circular de refresh até que o status principal da pilha fique com a bolinha verde: **`CREATE_COMPLETE`**!

---

### 7. Pegar o IP Público e URLs da Aplicação
Quando o status estiver verde:
1. Clique na aba **Saídas** (*Outputs*) no topo da sua pilha `erp-helpper-stack`.
2. Você verá as informações essenciais da sua máquina:
   - **`PublicIP`**: O endereço IP público da sua EC2 (exemplo: `SEU_IP_AWS`).
   - **`HealthCheckURL`**: `http://<SEU_IP>:5000/health`
   - **`SearchAPIURL`**: `http://<SEU_IP>:5000/search`

---

## 🌐 Como Validar os Links (Atenção às Portas!)

### ⚠️ Regras Importantes do Navegador:
1. **Não clique no `PublicDNS` puro:**  
   O DNS público aponta para a porta 80/443 (HTTP padrão), mas a nossa aplicação roda na **porta 5000**. Se abrir sem a porta `:5000`, o navegador dará `ERR_CONNECTION_REFUSED`.
2. **Não abra a `SearchAPIURL` na aba do navegador:**  
   A rota `/search` só aceita requisições do tipo **POST** (feitas pelo n8n). Abrir na barra do navegador faz um **GET**, retornando `405 Method Not Allowed`.
3. **O link para testar no navegador é o Health Check:**  
   Digite ou cole com `http://` (sem 's') e com a porta `:5000`:
   ```text
   http://<SEU_IP_PUBLICO>:5000/health
   ```
   Você verá a resposta em JSON confirmando:
   ```json
   {
     "status": "UP",
     "version": "1.0.0",
     "database": {
       "status": "UP",
       "type": "ChromaDB (SQLite/Vector)",
       "chunks_count": 534
     }
   }
   ```

---

## 🔑 Passo Final Obrigatório: Configurar a Chave da OpenAI

O CloudFormation já instalou o Docker, clonou o projeto e iniciou o container automaticamente. No entanto, para a Inteligência Artificial conseguir responder às perguntas dos usuários, você precisa colocar a sua chave real da OpenAI:

1. No Console AWS, pesquise por **EC2** e clique em **Instâncias** (*Instances*).
2. Clique na sua máquina criada (ex.: `erp-helpper-dev-api` ou `i-0dd4...`).
3. No canto superior direito, clique no botão **Conectar** (*Connect*).
4. Na aba **EC2 Instance Connect**, clique no botão laranja **Conectar** (*Connect*).  
   *(Um terminal preto do Linux abrirá diretamente na aba do seu navegador, sem precisar de programas externos).*
5. No terminal aberto, digite os seguintes comandos:
   ```bash
   cd /home/ubuntu/app
   nano .env
   ```
6. Procure a linha:
   ```env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
7. Substitua pelo seu token real da OpenAI.
8. Para salvar o arquivo:
   - Pressione **Ctrl + O** e depois tecle **Enter**.
   - Pressione **Ctrl + X** para fechar o editor.
9. Reinicie o container para aplicar a nova chave:
   ```bash
   docker compose restart
   ```

---

## 🔄 Conectando a sua AWS ao n8n Cloud

Se o seu grupo utiliza o n8n para orquestrar as conversas e canais:
1. Acesse o seu workflow no **n8n Cloud** (ou local).
2. Localize o nó **HTTP Request** responsável por chamar a Search API.
3. Atualize a URL para o IP gerado na sua máquina da AWS:
   ```text
   http://<SEU_NOVO_IP_PUBLICO>:5000/search
   ```
4. Salve e ative o workflow (*Save / Active*).

---

## 🧪 Validando com Teste de Carga e Automação

No seu computador, você pode rodar o teste automatizado em Python contra a sua máquina recém-criada:

```bash
# Teste de saúde e busca
python test_api.py aws

# Teste de carga e latência concorrente (Item de Maturidade)
python scripts/load_test.py http://<SEU_IP_PUBLICO>:5000 30 5
```

---

## 🆘 Solução de Problemas Rápidos (Troubleshooting)

| Sintoma | Causa Mais Provável | Solução |
| :--- | :--- | :--- |
| `ERR_CONNECTION_REFUSED` no navegador | Esqueceu de colocar `:5000` ou digitou `https://` | Use sempre `http://<IP>:5000/health` (com `http://` e porta 5000). |
| `405 Method Not Allowed` na rota `/search` | Tentou abrir `/search` direto na barra do navegador | Normal. O `/search` só aceita chamadas POST do n8n. Teste via `/health`. |
| Busca retorna vazia ou erro 500 | `OPENAI_API_KEY` vazia ou inválida | Conecte via EC2 Instance Connect, edite o `.env` e rode `docker compose restart`. |
| Stack com erro `CREATE_FAILED` | KeyName incorreto ou cota excedida | Certifique-se de escolher a chave `vockey` e região `us-east-1`. |
