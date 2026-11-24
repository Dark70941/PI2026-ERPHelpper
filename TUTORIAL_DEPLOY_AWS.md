# 🚀 Guia Definitivo de Deploy na AWS — ERP Helpper (Projeto Integrador)

Este tutorial foi desenvolvido para que **qualquer integrante do grupo**, mesmo sem experiência prévia avançada em computação em nuvem ou Linux, consiga hospedar e colocar em produção o ecossistema completo do **ERP Helpper** na **Amazon Web Services (AWS)**.

---

## 📌 Sumário
1. [Visão Geral da Arquitetura do Projeto](#1-visão-geral-da-arquitetura-do-projeto)
2. [Pré-requisitos e Contas Necessárias](#2-pré-requisitos-e-contas-necessárias)
3. [Passo 1: Criando e Configurando a Instância EC2 na AWS](#passo-1-criando-e-configurando-a-instância-ec2-na-aws)
4. [Passo 2: Configurando o Security Group (Firewall da AWS)](#passo-2-configurando-o-security-group-firewall-da-aws)
5. [Passo 3: Conectando na EC2 via SSH (Windows PowerShell / Terminal)](#passo-3-conectando-na-ec2-via-ssh-windows-powershell--terminal)
6. [Passo 4: Preparação do Servidor (Swap de Memória, Docker e Git)](#passo-4-preparação-do-servidor-swap-de-memória-docker-e-git)
7. [Passo 5: Clonando o Projeto e Configurando as Variáveis de Ambiente](#passo-5-clonando-o-projeto-e-configurando-as-variáveis-de-ambiente)
8. [Passo 6: Subindo a Search API (Flask + ChromaDB) com Docker](#passo-6-subindo-a-search-api-flask--chromadb-com-docker)
9. [Passo 7: Configurando o Nginx e Hospedando o Frontend Web](#passo-7-configurando-o-nginx-e-hospedando-o-frontend-web)
10. [Passo 8: Conectando o n8n ao Novo IP da AWS](#passo-8-conectando-o-n8n-ao-novo-ip-da-aws)
11. [Passo 9: Testes de Validação e Homologação de Ponta a Ponta](#passo-9-testes-de-validação-e-homologação-de-ponta-a-ponta)
12. [Passo 10: Dicas de Ouro, Gestão de Custos (Free Tier) e Troubleshooting](#passo-10-dicas-de-ouro-gestão-de-custos-free-tier-e-troubleshooting)

---

## 1. Visão Geral da Arquitetura do Projeto

O **ERP Helpper** é composto por 3 partes interligadas:

```
[ Usuário ]
    │
    ▼
[ 1. Frontend Web (index.html) ]  <── Hospedado no Nginx da EC2 (ou GitHub Pages)
    │  (Envia pergunta via HTTP POST)
    ▼
[ 2. Orquestrador n8n ]           <── n8n Cloud (ou container Docker)
    │  (Chama rota POST /search)
    ▼
[ 3. Search API (Flask) ]         <── Hospedado na AWS EC2 (Porta 5000 / Nginx)
    ├── ChromaDB (Base Vetorial Persistente em base_de_conhecimento_db/)
    ├── OpenAI API (Embeddings + Rerank gpt-4o-mini)
    └── knowledge_base.json (315+ artigos do UNO ERP)
```

- **Por que a EC2 é necessária?**
  A **Search API** roda Python e depende do **ChromaDB**, que precisa de persistência em disco rígido (`base_de_conhecimento_db/`) e poder de processamento em memória para cálculo de vetores e similaridade de cosseno.

---

## 2. Pré-requisitos e Contas Necessárias

Antes de iniciar, certifique-se de que você possui:
1. Uma conta ativa na **AWS** (pode ser conta Free Tier / Acadêmica / AWS Educate).
2. Chave de API da **OpenAI** (`OPENAI_API_KEY`) com saldo de créditos ativo.
3. Acesso ao repositório GitHub do projeto (`https://github.com/Dark70941/PI2026-ERPHelpper.git`).
4. Computador com **Windows Terminal**, **PowerShell** ou **Git Bash**.

---

## Passo 1: Criando e Configurando a Instância EC2 na AWS

1. Faça login no [Console de Gerenciamento da AWS](https://aws.amazon.com/console/).
2. No canto superior direito, selecione a região mais próxima ou padrão (exemplo: **us-east-1 (Norte da Virgínia)** ou **sa-east-1 (São Paulo)**).
   > *Dica: `us-east-1` costuma ter o Free Tier mais abrangente e menor custo.*
3. Na barra de busca superior, digite **EC2** e clique no serviço.
4. No painel da EC2, clique no botão laranja **Executar instância** (*Launch instance*).
5. Preencha os campos exatamente como abaixo:
   - **Nome:** `erp-helpper-api`
   - **Imagens de aplicação e de SO (AMI):** Selecione **Ubuntu**.
   - **Versão da AMI:** Escolha **Ubuntu Server 24.04 LTS** (ou 22.04 LTS) — *Elegível para nível gratuito*.
   - **Arquitetura:** `64 bits (x86)`.
   - **Tipo de instância:**
     - Ideal para Free Tier: `t2.micro` (1 vCPU, 1 GB RAM) ou `t3.micro`.
     - *Recomendação:* Adicionaremos um arquivo de Swap (memória virtual) no Passo 4 para que o ChromaDB rode sem nenhuma falha de memória.
   - **Par de chaves (Key Pair - Login):**
     - Clique em **Criar novo par de chaves**.
     - Nome da chave: `erp-helpper-key`
     - Tipo de par de chaves: `RSA`
     - Formato de arquivo de chave privada: `.pem` (para OpenSSH / PowerShell / Linux / Mac).
     - Clique em **Criar par de chaves**. O arquivo `erp-helpper-key.pem` será baixado no seu computador.
     - **IMPORTANTE:** Guarde esse arquivo na pasta `Downloads` ou em uma pasta segura (ex: `C:\chaves\`). **Não perca este arquivo!**
   - **Armazenamento (Configure Storage):**
     - Altere o tamanho do disco de 8 GiB para **15 GiB** (o nível gratuito da AWS permite até 30 GiB de SSD gp3/gp2).

Ainda não clique em executar! Vamos configurar as regras de rede (Security Group) a seguir.

---

## Passo 2: Configurando o Security Group (Firewall da AWS)

Na seção **Configurações de rede** (*Network settings*):
1. Marque **Criar grupo de segurança** (*Create security group*).
2. Dê o nome: `erp-helpper-sg`.
3. Descrição: `Grupo de seguranca para API e Frontend do ERP Helpper`.
4. Configure as **Regras de Entrada (Inbound Rules)**:

| Tipo | Protocolo | Intervalo de portas | Origem | Descrição |
| :--- | :---: | :---: | :---: | :--- |
| **SSH** | TCP | 22 | Qualquer lugar (0.0.0.0/0) | Para você acessar o terminal do servidor |
| **HTTP** | TCP | 80 | Qualquer lugar (0.0.0.0/0) | Para acessar o site frontend e API web |
| **HTTPS** | TCP | 443 | Qualquer lugar (0.0.0.0/0) | Para tráfego seguro SSL |
| **TCP Personalizado** | TCP | 5000 | Qualquer lugar (0.0.0.0/0) | Para a Search API Flask (comunicação com n8n) |

5. Clique no botão laranja **Executar instância** (*Launch instance*).
6. Aguarde alguns instantes até o status da instância mudar para **Em execução** (*Running*).
7. Clique sobre a instância criada e anote o **Endereço IPv4 público** (exemplo: `SEU_IP_AWS`).

---

## Passo 3: Conectando na EC2 via SSH (Windows PowerShell / Terminal)

1. No seu computador Windows, abra o **PowerShell** ou **Terminal**.
2. Navegue até a pasta onde você salvou a sua chave `.pem` baixada:
   ```powershell
   cd C:\Users\SEU_USUARIO\Downloads
   ```
3. No Windows, para garantir as permissões corretas do arquivo da chave, execute:
   ```powershell
   icacls erp-helpper-key.pem /inheritance:r
   icacls erp-helpper-key.pem /grant:r "$($env:USERNAME):(R)"
   ```
4. Conecte-se na sua instância EC2 pelo comando SSH (substitua pelo IP público da sua EC2):
   ```bash
   ssh -i erp-helpper-key.pem ubuntu@SEU_IP_PUBLICO_AWS
   ```
5. O terminal perguntará: `Are you sure you want to continue connecting (yes/no/[fingerprint])?`
   - Digite `yes` e pressione **Enter**.
6. Pronto! Você estará dentro do terminal Ubuntu da AWS:
   ```text
   ubuntu@ip-172-31-xx-xx:~$
   ```

---

## Passo 4: Preparação do Servidor (Swap de Memória, Docker e Git)

Dentro do terminal da sua EC2, execute os comandos a seguir.

### 4.1. Criar Memória Swap de 2GB (Essencial para ChromaDB na Free Tier)
Instâncias `t2.micro` / `t3.micro` têm 1GB de RAM. Como o ChromaDB e os modelos de Embedding usam bibliotecas C++ pesadas, criar 2GB de Swap evita travamentos por falta de memória (OOM):

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```
*(Você verá 1GB de Memória física e 2GB de Swap prontos!)*

---

### 4.2. Atualizar o Sistema e Instalar Ferramentas Básicas
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget unzip htop ufw nginx
```

---

### 4.3. Instalar o Docker e Docker Compose
O método mais rápido, limpo e padronizado para todo o grupo é usar Docker:

```bash
# Baixar e executar o script oficial do Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar o usuário ubuntu ao grupo docker (para não precisar usar sudo toda hora)
sudo usermod -aG docker ubuntu

# Instalar o plugin do Docker Compose
sudo apt install -y docker-compose-plugin

# Aplicar a nova permissão de grupo
newgrp docker

# Testar se o Docker está funcionando
docker --version
docker compose version
```

---

## Passo 5: Clonando o Projeto e Configurando as Variáveis de Ambiente

1. Clone o repositório oficial do projeto na sua EC2:
   ```bash
   cd ~
   git clone https://github.com/Dark70941/PI2026-ERPHelpper.git
   cd chatBotAWS1
   ```

2. Crie o arquivo `.env` a partir do modelo `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Abra o arquivo `.env` para edição:
   ```bash
   nano .env
   ```

4. Preencha a sua chave da OpenAI e configure os parâmetros:
   ```ini
   # Chave de API da OpenAI (OBRIGATÓRIO)
   OPENAI_API_KEY=sk-proj-sua-chave-secreta-da-openai-aqui

   # Chave do ElevenLabs (Opcional - necessário apenas se for testar o canal de voz)
   ELEVENLABS_API_KEY=sua_chave_elevenlabs_aqui
   ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

   # Porta e Configurações
   PORT=5000
   DB_PATH=base_de_conhecimento_db
   COLLECTION_NAME=docs_uno_erp_cosine
   MODELO_EMBEDDING=text-embedding-3-small
   MODELO_LLM=gpt-4o-mini
   ```

5. Para salvar no `nano`:
   - Pressione `Ctrl + O` e dê **Enter** (salva o arquivo).
   - Pressione `Ctrl + X` (sai do editor).

---

## Passo 6: Subindo a Search API (Flask + ChromaDB) com Docker

Com o `.env` configurado, basta um único comando para construir a imagem e subir o container da Search API:

```bash
docker compose up -d --build
```

### Como verificar se a API subiu com sucesso:
1. Veja os containers em execução:
   ```bash
   docker compose ps
   ```
   *(O container `erp-helpper-api` deve estar com status `Up`)*

2. Acompanhe os logs em tempo real:
   ```bash
   docker compose logs -f erp-helpper-search-api
   ```
   *(Pressione `Ctrl + C` para sair dos logs a qualquer momento)*

3. Teste a rota `/search` localmente via terminal na própria EC2:
   ```bash
   curl -X POST http://localhost:5000/search \
     -H "Content-Type: application/json" \
     -d '{"query": "rejeição 201"}'
   ```
   *Se retornar uma lista JSON com os manuais do UNO ERP, sua API está 100% operacional!*

---

## Passo 7: Configurando o Nginx e Hospedando o Frontend Web

Vamos configurar o **Nginx** para que:
- O frontend (`index.html`) fique acessível na porta 80 (HTTP padrão: `http://SEU_IP_PUBLICO/`).
- O Nginx faça proxy reverso seguro para a API Flask na porta 5000.

### 7.1. Copiar o Frontend para o Diretório Web
```bash
sudo mkdir -p /var/www/erphelpper
sudo cp /home/ubuntu/chatBotAWS1/index.html /var/www/erphelpper/index.html
```

### 7.2. Configurar o Nginx
Abra a configuração padrão do Nginx:
```bash
sudo nano /etc/nginx/sites-available/default
```

Substitua todo o conteúdo do arquivo pelo bloco abaixo:

```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    # Diretório onde está o index.html
    root /var/www/erphelpper;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy reverso para a Search API Flask
    location /search {
        proxy_pass http://127.0.0.1:5000/search;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }
}
```
*(Salve com `Ctrl + O`, **Enter** e saia com `Ctrl + X`)*

### 7.3. Reiniciar e Validar o Nginx
```bash
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl status nginx
```

Agora abra o navegador no seu computador e acesse:
```text
http://SEU_IP_PUBLICO_AWS
```
Você verá a interface do **Assistente UNO ERP** carregada diretamente da sua máquina na nuvem AWS!

---

## Passo 8: Conectando o n8n ao Novo IP da AWS

O **n8n** é o cérebro que orquestra a comunicação entre a interface do chat, a Search API e a OpenAI:

1. Acesse a sua instância do **n8n** (n8n Cloud ou seu container local).
2. Abra o workflow **`ERP Helpper - UNO ERP AI Workflow`**.
   *(Se for uma nova instalação, importe o arquivo `n8n/workflow_uno_erp_helpper.json`)*.
3. Dê um duplo clique no nó **HTTP Request**:
   - No campo **URL**, altere de:
     `http://localhost:5000/search`
   - Para o **novo IP público da sua AWS**:
     `http://SEU_NOVO_IP_PUBLICO:5000/search`
     *(Ou se configurou o Nginx: `http://SEU_NOVO_IP_PUBLICO/search`)*
4. Salve e clique em **Publish / Ativar** no n8n.
5. Copie a URL do **Webhook de Produção** gerada no nó `Webhook` do n8n.
6. Atualize a URL do webhook no arquivo `/var/www/erphelpper/index.html`:
   ```bash
   sudo nano /var/www/erphelpper/index.html
   ```
   Localize a linha:
   ```javascript
   const n8nWebhookUrl = 'https://seu-n8n.exemplo.com/webhook/...';
   ```
   Substitua pela URL do seu Webhook do n8n e salve o arquivo.

---

## Passo 9: Testes de Validação e Homologação de Ponta a Ponta

Para garantir que tudo está funcionando perfeitamente para a apresentação do PI:

### Teste 1: Teste Direto da Search API via PowerShell
No seu próprio computador Windows, abra o PowerShell e rode:
```powershell
Invoke-RestMethod -Uri "http://SEU_IP_PUBLICO:5000/search" -Method Post -ContentType "application/json" -Body '{"query": "rejeição 201"}' | ConvertTo-Json -Depth 2
```
*Deve retornar uma lista com os artigos e links de suporte.*

### Teste 2: Teste de Conversação no Navegador
1. Abra `http://SEU_IP_PUBLICO/` no navegador.
2. Envie a pergunta: `Olá, como resolver a rejeição 201 no faturamento?`
3. Verifique:
   - ✅ O indicador de digitação ("typing dots") é exibido.
   - ✅ A resposta do bot aparece estruturada em passos.
   - ✅ A área de **Fontes / Referências** contém os links oficiais clicáveis para o manual da UNO ERP.

---

## Passo 10: Dicas de Ouro, Gestão de Custos (Free Tier) e Troubleshooting

### 💡 Dica 1: Gerenciar IP Público (Evitar que o IP mude ao reiniciar)
Na AWS EC2, se você parar (*Stop*) e iniciar (*Start*) a máquina, o IP público padrão muda.
- **Solução:** No menu lateral esquerdo da EC2, vá em **IPs elásticos** (*Elastic IPs*).
- Clique em **Alocar endereço IP elástico** -> **Alocar**.
- Selecione o IP criado -> **Ações** -> **Associar endereço IP elástico**.
- Escolha a sua instância `erp-helpper-api` e associe. Agora o seu IP será **fixo e estático**.

### 💡 Dica 2: Como Reiniciar a Aplicação após Alterações de Código
Sempre que fizer alterações no código do repositório:
```bash
cd ~/chatBotAWS1
git pull origin main
docker compose up -d --build
```

### 💡 Dica 3: Como Economizar Créditos / Não Pagar Nada na AWS
- Se a equipe não estiver testando ou apresentando o projeto, você pode pausar a instância:
  - No console AWS -> Selecione a instância -> **Estado da instância** -> **Interromper instância** (*Stop instance*).
  - *Obs: Ao interromper, não há cobrança de computação da CPU/RAM!*
  - Para voltar a usar, basta clicar em **Iniciar instância** (*Start instance*).

### 🛠️ Troubleshooting (Resolução de Erros Comuns)

| Sintoma / Erro | Causa Provável | Como Resolver |
| :--- | :--- | :--- |
| **Timeout ou "Site não pode ser alcançado"** | Portas bloqueadas no Security Group | Verifique no console AWS se o Security Group possui as portas 80, 5000 e 22 liberadas para `0.0.0.0/0`. |
| **Container morre silenciosamente (*Killed*)** | Falta de memória RAM | Verifique se você executou o passo de criação do **Swap de 2GB** (`free -h`). |
| **Erro 500 ao chamar `/search`** | `OPENAI_API_KEY` ausente ou inválida | Verifique o arquivo `.env` e rode `docker compose logs -f` para inspecionar a mensagem de erro exata. |
| **Chat responde "Ocorreu um erro ao buscar resposta"** | URL do n8n incorreta no `index.html` ou webhook desativado | Abra o n8n e verifique se o fluxo está **Ativo (Active)** e se o nó HTTP Request consegue alcançar o IP da EC2. |

---

> 🎓 **Projeto Integrador — FATEC**  
> Guia elaborado para a equipe e homologado para a disciplina de Projeto Integrador. Em caso de dúvidas durante o deploy, consulte o arquivo `README.md` ou acione os membros da equipe.
