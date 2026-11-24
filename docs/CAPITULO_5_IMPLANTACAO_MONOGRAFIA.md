# 5. Implantação

Neste capítulo são descritos os procedimentos técnicos e requisitos operacionais necessários para a disponibilização, instalação, execução, monitoramento e manutenção do ecossistema do **ERP Helpper**. A solução adota princípios de arquitetura modular, conteinerização e computação em nuvem, garantindo portabilidade entre ambientes de desenvolvimento e homologação em produção.

---

## 5.1 Repositório e Controle de Versão

O código-fonte integral da aplicação, bem como seus arquivos de configuração, modelos de dados, artefatos de infraestrutura como código (IaC) e pipelines de integração contínua (CI/CD), encontra-se devidamente versionado sob o sistema de controle de versão distribuído Git.

- **Repositório Oficial (GitHub):** [https://github.com/Dark70941/PI2026-ERPHelpper.git](https://github.com/Dark70941/PI2026-ERPHelpper.git)
- **Branch Principal de Produção:** `main`
- **Search API em Produção (AWS EC2):** `http://SEU_IP_AWS:5000/search`
- **Health Check da API (AWS EC2):** `http://SEU_IP_AWS:5000/health`
- **Webhook de Orquestração (n8n Cloud / ElevenLabs):** `https://seu-n8n.exemplo.com/webhook/seu-webhook-id`

Em consonância com as boas práticas de segurança da informação e governança em nuvem, o repositório é configurado com políticas estritas de proteção contra vazamento de dados sensíveis. Nenhuma credencial de produção, token de API ou chave de serviço está versionada em texto plano; tais parâmetros são gerenciados exclusivamente por meio de variáveis de ambiente declaradas no arquivo `.env` (ignorado pelo `.gitignore`), sendo fornecido no repositório o modelo seguro [.env.example](https://github.com/Dark70941/PI2026-ERPHelpper/blob/main/.env.example).

---

## 5.2 Requisitos de Sistema e Softwares Complementares

Para o correto funcionamento do ecossistema do ERP Helpper, o ambiente computacional deve atender aos seguintes pré-requisitos de infraestrutura e serviços externos:

### 5.2.1 Requisitos Mínimos de Infraestrutura (Hardware)
- **Processamento:** 1 vCPU (x86_64 ou ARM64) de 2.0 GHz ou superior.
- **Memória RAM:** 1 GB de memória física acompanhada obrigatoriamente de 2 GB de memória virtual (*swap*), ou 2 GB de RAM dedicados (essenciais para alocação do índice vetorial em memória sem estouro de capacidade).
- **Armazenamento:** 15 GB de espaço livre em disco de estado sólido (SSD gp3), garantindo taxas de leitura e escrita satisfatórias para o banco de dados vetorial.

### 5.2.2 Softwares de Sistema e Runtimes
- **Sistema Operacional:** Linux Ubuntu Server 22.04 / 24.04 LTS (para servidores em nuvem), Windows 10/11 ou macOS (para desenvolvimento).
- **Python:** Versão 3.10 ou superior.
- **Docker Engine & Docker Compose:** Versão 24.0+ e Compose v2.x (para isolamento e execução em contêineres).
- **Git:** Versão 2.30+ para versionamento e sincronização contínua de código.

### 5.2.3 Softwares Complementares e Serviços Integrados
1. **ChromaDB (Vector Database):** Banco de dados vetorial embutido que opera com base no algoritmo HNSW (*Hierarchical Navigable Small World*) e banco relacional SQLite interno, responsável pelo armazenamento e recuperação por similaridade de cosseno de 530+ artigos técnicos do UNO ERP.
2. **ElevenLabs API (Canal de Voz / Conversational AI):** Mecanismo de conversão de texto em fala (*Text-to-Speech - TTS*) e processamento de voz neural em tempo real, responsável pela interação telefônica humanizada, gestão de pausas e atendimento por voz de baixa latência.
3. **n8n Workflow Hub (Community ou Cloud):** Plataforma de automação e orquestração de fluxos, atuando como concentrador entre as chamadas do canal de voz, a Search API na AWS e os modelos generativos de IA.
4. **OpenAI API:** Provedor externo utilizado para a conversão de textos em embeddings vetoriais de 1536 dimensões (*modelo text-embedding-3-small*) e para expansão semântica de dúvidas operacionais e rerank de relevância (*modelo gpt-4o-mini*).

---

## 5.3 Procedimento de Instalação e Execução

A implantação do sistema pode ser realizada em ambiente de desenvolvimento local ou em servidores em nuvem por meio de contêineres Docker.

### 5.3.1 Instalação Manual em Ambiente Local
1. **Clonagem do Repositório:**
   ```bash
   git clone https://github.com/Dark70941/PI2026-ERPHelpper.git
   cd chatBotAWS1
   ```
2. **Criação e Ativação do Ambiente Virtual Python:**
   - No Windows:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - No Linux/macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. **Instalação das Dependências:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. **Definição das Variáveis de Ambiente:**
   ```bash
   cp .env.example .env
   ```
   Inserir as chaves da OpenAI (`OPENAI_API_KEY`) e ElevenLabs (`ELEVENLABS_API_KEY`).
5. **Inicialização da Search API:**
   ```bash
   python main.py
   ```
   O serviço responderá no endereço local `http://127.0.0.1:5000`.

### 5.3.2 Implantação Automatizada com Docker e Docker Compose
Para padronizar o ambiente de produção e assegurar paridade entre os testes, a aplicação disponibiliza o `Dockerfile` e o `docker-compose.yml`:
1. **Configuração inicial:**
   ```bash
   cp .env.example .env  # Inserir as credenciais necessárias
   ```
2. **Construção e Execução em Segundo Plano:**
   ```bash
   docker compose up -d --build
   ```
3. **Acompanhamento de Logs de Operação:**
   ```bash
   docker compose logs -f erp-helpper-search-api
   ```

---

## 5.4 Utilização e Operação do Software

O ERP Helpper foi concebido como um agente de inteligência artificial focado primordialmente no **atendimento por voz inteligente** e na recuperação documental precisa:

1. **Canal Telefônico e Agente de Voz (ElevenLabs + Twilio/VoIP):**  
   Constitui o canal de atendimento principal do projeto. O usuário estabelece uma chamada telefônica ou simulação de áudio, cuja voz é capturada, transcrita via Speech-to-Text (STT) e encaminhada ao orquestrador n8n. O n8n consulta a Search API na AWS para resgatar os manuais oficiais do UNO ERP, sintetiza a orientação passo a passo com o modelo de linguagem e converte a resposta em áudio ultra-realista por meio da API da **ElevenLabs**, gerando uma experiência fluida de diálogo em tempo real.
2. **Simulador de Atendimento por Voz (`test_voice.py`):**  
   Script automatizado desenvolvido para homologação local do canal de voz, permitindo enviar perguntas operacionais (ex.: *"Como tratar a rejeição 201?"*), consultar a Search API na AWS e gerar o arquivo de áudio resultante `resposta_voz.mp3` para validação imediata da equipe.
3. **Interface Web de Apoio (`index.html`):**  
   Interface leve em Single Page Application (SPA), desenvolvida para testes visuais rápidos e validação textual das consultas retornadas pelo webhook do n8n.
4. **Endpoints da API REST (Search API na AWS):**  
   - `GET /health`: Rota de diagnóstico utilizada para inspecionar a saúde do sistema, tempo de atividade (*uptime*) e integridade da base vetorial.
   - `POST /search`: Endpoint consumido pelo orquestrador n8n, recebendo a pergunta em formato JSON e retornando os documentos mais relevantes através de busca híbrida (semântica e lexical) com rerank.

---

## 5.5 Monitoramento e Telemetria

A sustentação da aplicação é viabilizada por meio de monitoramento em duas camadas:

1. **Health Check Contínuo da Aplicação:**  
   O sistema expõe a rota `GET /health`, que valida se o processo da aplicação está ativo e se a coleção de vetores do ChromaDB permanece acessível e íntegra. Em caso de anomalia, o serviço responde com código HTTP `503 Service Unavailable`, viabilizando integração direta com balanceadores de carga e ferramentas de alerta.
2. **Logs Estruturados:**  
   O backend emite registros estruturados nos padrões `INFO`, `WARNING`, `ERROR` e `CRITICAL`, registrando timestamps, duração das buscas em segundos, identificadores de documentos recuperados e status das requisições externas, facilitando auditoria e depuração técnica.
3. **Métricas de Infraestrutura e Alarmes (AWS CloudWatch):**  
   Em ambiente de nuvem na AWS, a máquina virtual é monitorada continuamente por métricas de CPU, disco e rede no Amazon CloudWatch. Um alarme automatizado (`ERPHelpperHighCPUAlarm`) está pré-configurado para notificar a equipe técnica caso a utilização de processamento ultrapasse 80% por mais de 10 minutos consecutivos.

---

## 5.6 Estratégia de Backup e Recuperação contra Desastres

Para assegurar a continuidade do negócio e a salvaguarda da base de conhecimento, o projeto contempla rotinas padronizadas de backup e restauração:

1. **Ativos Críticos Mapeados:**  
   - Diretório da Base Vetorial (`base_de_conhecimento_db/`), contendo os vetores indexados e as estruturas relacionais do SQLite;
   - Base Factual Documental (`knowledge_base.json`), contendo 530+ artigos técnicos do UNO ERP;
   - Fluxos de Orquestração (`n8n/workflow_uno_erp_helpper.json`).
2. **Procedimento de Backup Automatizado:**  
   Por meio do script `scripts/backup_s3.sh`, executado periodicamente via agendador Cron no servidor, os diretórios de dados são compactados em arquivos `.tar.gz` identificados por data e hora (`backup_vector_db_YYYYMMDD_HHMMSS.tar.gz`) e sincronizados para armazenamento de alta durabilidade em nuvem (Amazon S3).
3. **Procedimento de Restauração (Restore):**  
   O script `scripts/restore_s3.sh` automatiza a recuperação em caso de falha: localiza o snapshot mais recente no S3, descompacta os arquivos sobre a base de conhecimento e reinicia os contêineres Docker, restabelecendo a operação completa do sistema em um tempo médio inferior a 8 minutos (*Recovery Time Objective - RTO*), com perda máxima de dados limitada à janela de 24 horas (*Recovery Point Objective - RPO*).
