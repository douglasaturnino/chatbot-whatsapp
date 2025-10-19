# Chatbot IA para WhatsApp (EvolutionAPI + LangChain)

Este repositório contém um chatbot para WhatsApp que integra:

- EvolutionAPI (painel + gateway para WhatsApp)
- FastAPI para expor o webhook e endpoints
- LangChain (Fluxos RAG) para recuperar documentos e conversar com LLMs
- Chroma para persistência de vetores
- Modelos Groq (ChatGroq) para LLM e FastEmbed/BGE para embeddings
- Docker / Docker Compose para facilitar deploy

Este README explica como configurar, executar e ajustar o projeto.

## Sumário

- Pré-requisitos
- Variáveis de ambiente (exemplo)
- Como executar (Docker e local)
- Adicionar documentos para RAG (vetorização)
- Qual modelo usar e recomendações
- Troubleshooting e notas

## 1) Pré-requisitos

- Docker & Docker Compose (recomendado para produção/testes locais consistentes)
- Python 3.11+ (para execução local)
- Chaves/credenciais da EvolutionAPI
- (Opcional) Conta/credenciais para provedores de modelos se for usar outros LLMs

## 2) Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto. Abaixo está um exemplo com variáveis detectadas no código — ajuste conforme necessário:

```
# EvolutionAPI
EVOLUTION_API_URL=http://localhost:8080/api
EVOLUTION_INSTANCE_NAME=nome_da_instancia
AUTHENTICATION_API_KEY=suachave_da_evolution

# Groq (LLM) - usado pelo ChatGroq
GROQ_MODEL_NAME=llama-3.3-70b-versatile (exemplo ou outro modelo Groq compatível)
GROQ_MODEL_TEMPERATURE=0

# Vetor store / RAG
RAG_FILES_DIR=./rag_files
VECTOR_STORE_PATH=./vectorstore_data

# Redis (cache) — usado pelo docker-compose como `CACHE_REDIS_URI`
CACHE_REDIS_URI=redis://redis:6379/0

# Opcional: configura prompts via variáveis
AI_CONTEXTUALIZE_PROMPT="Seu prompt de contextualização aqui"
AI_SYSTEM_PROMPT="Seu prompt de sistema (papel do assistente) aqui"

```

Observações:
- `EVOLUTION_INSTANCE_NAME` deve corresponder ao nome da instância configurada no painel da EvolutionAPI (Manager).
- `EVOLUTION_API_URL` aponta para onde o serviço EvolutionAPI está escutando (no docker-compose padrão: http://localhost:8080/api).
- `GROQ_MODEL_NAME` e `GROQ_MODEL_TEMPERATURE` controlam qual modelo Groq será usado pelo `langchain_groq.ChatGroq`.
- `RAG_FILES_DIR` é a pasta onde você coloca PDFs e .txt para vetorização.

## 3) Como executar

3.1 Usando Docker Compose (recomendado)

1. Copie/exemplo e edite `.env`:

```bash
cp .env.example .env || true
# edite .env com suas chaves
```

2. Suba os serviços:

```bash
docker-compose up --build
```

Serviços principais:
- `evolution-api` — painel e gateway para WhatsApp
- `bot` — aplicação FastAPI que expõe `/webhook`
- `redis`, `postgres` — dependências do EvolutionAPI

Depois que o painel do EvolutionAPI estiver no ar, adicione sua instância do WhatsApp no painel (Manager) e configure o webhook da instância para:

```
http://bot:8000/webhook
```

Habilite o evento `MESSAGES_UPSERT` para receber mensagens.

3.2 Execução local (sem Docker)

1. Crie e ative um virtualenv, instale dependências:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Exporte as variáveis de ambiente (ou use `.env` com python-dotenv) e rode o servidor:

```bash
# com uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000
```

Nota: se executar localmente, você ainda precisa de um EvolutionAPI acessível (pode rodar via docker-compose apenas o serviço `evolution-api`) e apontar `EVOLUTION_API_URL` para ele.

## 4) Adicionar documentos para RAG

1. Coloque arquivos PDF ou TXT dentro da pasta `rag_files/` na raiz do projeto.
2. No próximo start do serviço `bot` (ou ao chamar o código manualmente), o módulo `vectorstore.py`:
	- vai carregar os documentos (PyPDFLoader / TextLoader),
	- dividir em chunks (chunk_size=1000, overlap=200),
	- gerar embeddings com `FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")`,
	- persistir no diretório indicado por `VECTOR_STORE_PATH` (ex: `./vectorstore_data`).

Os arquivos processados serão movidos para `rag_files/processed/`.

Dica: para re-processar todos os documentos, remova ou renomeie a pasta `rag_files/processed` para que os arquivos voltem a ser lidos.

## 5) Modelos e recomendações

- LLM principal no projeto: ChatGroq (via `langchain_groq.ChatGroq`). A variável `GROQ_MODEL_NAME` define qual modelo Groq usar. Exemplos: `openai/gpt-oss-20b` (verifique disponibilidade/compatibilidade com sua conta Groq).
- Embeddings: `BAAI/bge-base-en-v1.5` via `FastEmbedEmbeddings` (bom trade-off entre custo e qualidade para embeddings).
- Vetor store: Chroma (persistência local em `VECTOR_STORE_PATH`).

Sugestões:
- Para conversas em português, teste a qualidade do modelo e ajuste `GROQ_MODEL_TEMPERATURE` (0.0-0.5 para respostas mais determinísticas).
- Se quiser usar OpenAI ou outro provedor, será necessário adaptar `chains.py` para criar o LLM correspondente (por exemplo, `OpenAI` ou `ChatOpenAI`) e ajustar variáveis de ambiente.

## 6) Estrutura importante de arquivos

- `app.py` — entrada FastAPI e webhook `/webhook` que processa eventos da EvolutionAPI.
- `chains.py` — constrói o chain RAG com histórico, ChatGroq e retrieval.
- `vectorstore.py` — carrega documentos, cria/salva Chroma e embeddings.
- `evolution_api.py` — função `send_whatsapp_message` que chama a API Evolution para enviar respostas.
- `prompts.py` — prompts usados nos fluxos (carregados de `AI_CONTEXTUALIZE_PROMPT` e `AI_SYSTEM_PROMPT`).

## 7) Troubleshooting / notas

- Webhook 404/500: verifique se o container `bot` está rodando e expõe a porta 8000. Verifique logs do container:

```bash
docker-compose logs -f bot
```

- Mensagens não chegam no bot: confirme que o webhook configurado na instância do EvolutionAPI está exatamente `http://bot:8000/webhook` (ou `http://localhost:8000/webhook` se exposto diretamente) e que `MESSAGES_UPSERT` está habilitado.
- Vetores não são encontrados / base vazia: verifique `VECTOR_STORE_PATH` e se o processo de vetorização foi executado. Logs ao iniciar o bot mostrarão a criação/persistência do Chroma.
- Problemas de credenciais: confirme `AUTHENTICATION_API_KEY` e `EVOLUTION_INSTANCE_NAME` no painel da EvolutionAPI.

## 8) Como contribuir

- Abra issues descrevendo bugs ou melhorias.
- Envie PRs com testes pequenos e documentação.

## 9) Resumo rápido (cheat sheet)

- Subir tudo com Docker:

```bash
cp .env.example .env
# editar .env
docker-compose up --build
```

- Executar localmente:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

