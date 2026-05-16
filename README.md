# AI Automation Platform

A local AI assistant that can read your files, learn from them, and send messages to your clients via Gmail or WhatsApp — all running on your own machine.

---

## What this does

1. **Chat with an AI** powered by a local model (Llama 3.2 via Ollama)
2. **Upload your files** (PDFs, docs, text) so the AI learns your business context
3. **Create a personal agent** that knows your products, tone, and client behaviors
4. **Send messages** to specific clients via Gmail or WhatsApp through simple commands
5. **Search a knowledge base** so the agent always answers based on *your* information

---

## Before you start

Make sure you have these installed:

| Tool | Why you need it | Link |
|---|---|---|
| Python 3.11+ | Runs the backend | [python.org](https://python.org) |
| Docker + Docker Compose | Runs the database and services | [docker.com](https://docker.com) |
| Ollama | Runs the AI model locally | [ollama.com](https://ollama.com) |

---

## Quick start

```bash
# 1. Clone the project
git clone https://github.com/your-username/ai-automation-platform.git
cd ai-automation-platform

# 2. Copy the environment file and fill in your keys
cp example.env .env

# 3. Pull the AI model
ollama pull llama3.2

# 4. Start the database and services
docker-compose up -d

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Run the app
python app/main.py
```

The API will be running at `http://localhost:8000`

---

## Environment variables

Open `.env` and fill in the values below. Everything else has a default.

```env
# Gmail (follow the Gmail setup guide in docs/)
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=

# WhatsApp Business API
WHATSAPP_API_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=

# Database
POSTGRES_URL=postgresql://postgres:password@localhost:5432/ai_platform

# Vector DB
VECTOR_DB=pgvector
```

---

## Project structure

```
ai-automation-platform/
│
├── app/
│   ├── main.py                  # App entry point
│   ├── config/                  # Settings and constants
│   │
│   ├── api/
│   │   ├── routes/              # HTTP endpoints (chat, agents, RAG)
│   │   └── schemas/             # Request/response data shapes
│   │
│   ├── core/
│   │   ├── llm/                 # Ollama client and prompts
│   │   ├── agents/              # Agent logic, memory, and tools
│   │   ├── rag/                 # File ingestion, search, and evaluation
│   │   └── workflows/           # Automation and task routing
│   │
│   ├── integrations/
│   │   ├── gmail/               # Send emails
│   │   └── whatsapp/            # Send WhatsApp messages
│   │
│   ├── database/
│   │   ├── postgres/            # User, agent, and conversation data
│   │   └── vector_db/           # Stores file embeddings for search
│   │
│   └── services/                # Business logic layer
│
├── data/
│   ├── raw/                     # Files you upload
│   └── processed/               # Files after chunking and processing
│
├── scripts/
│   ├── ingest_documents.py      # Load files into the knowledge base
│   └── evaluate_rag.py          # Test how well the search is working
│
├── docs/                        # Architecture and decision records
├── postgres/
│   └── schema.sql               # Database schema
├── docker-compose.yml
├── requirements.txt
└── example.env
```

---

## How it works (simple version)

```
You upload files → files are split into chunks → chunks are turned into
vectors → stored in a database

You talk to the agent → agent searches the vector database → finds
relevant chunks → uses them to answer or take action

You say "send email to João" → agent checks its knowledge base for
tone and product info → drafts and sends the message
```

---

## Verifying the database

After running `docker-compose up -d`, confirm the database is set up correctly.

**Option 1 — Adminer (visual)**

Open `http://localhost:5001` and connect with:

| Field | Value |
|---|---|
| System | PostgreSQL |
| Server | `db` |
| Username | `postgres` |
| Password | `password` |
| Database | `ai_platform` |

Then run this query to check all tables exist:

```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```

You should see 6 tables: `users`, `agents`, `conversations`, `documents`, `clients`, `messages`.

Check the vector extension is active:

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

**Option 2 — Terminal**

```bash
docker exec -it pgvector-db psql -U postgres -d ai_platform -c "\dt"
```

**If the tables are missing**, paste the contents of `postgres/schema.sql` directly into the Adminer query box and execute. This creates all tables manually without needing to restart Docker.

---

## Main API endpoints

| Method | Endpoint | What it does |
|---|---|---|
| POST | `/chat` | Send a message to the AI |
| POST | `/agents` | Create a new agent |
| POST | `/rag/ingest` | Upload files to the knowledge base |
| POST | `/integrations/send` | Send a message via Gmail or WhatsApp |
| GET | `/health` | Check if everything is running |

Full API docs available at `http://localhost:8000/docs` when the app is running.

---

## Known limitations

- WhatsApp requires a verified Meta Business account to send messages outside sandbox mode
- The AI model runs locally — a machine with at least 8GB RAM is recommended
- File ingestion is currently manual (run the script); no automatic sync yet

---

## Docs

- [`docs/architecture.md`](docs/architecture.md) — How the pieces connect
- [`docs/rag_pipeline.md`](docs/rag_pipeline.md) — How file search works
- [`docs/agent_flow.md`](docs/agent_flow.md) — How the agent makes decisions
- [`docs/decisions/`](docs/decisions/) — Why we made key technical choices