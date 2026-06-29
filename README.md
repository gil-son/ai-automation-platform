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

## Docker Compose — Port Mapping

| Host (your machine) | Container port | Service |
|---|---|---|
| `localhost:5432` | 5432 | PostgreSQL (pgvector) |
| `localhost:5001` | 8080 | Adminer |
| `localhost:3000` | 3000 | Langfuse |
| `localhost:5433` | 5432 | Langfuse DB |

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
├── app/
│   ├── main.py                  # App entry point
│   ├── api/
│   │   ├── routes/              # API route implementations
│   │   │   ├── agents.py
│   │   │   ├── chat.py
│   │   │   ├── rag.py
│   │   │   ├── integrations.py
│   │   │   └── health.py
│   │   └── schemas/             # Pydantic models for request/response
│   │       ├── agents.py
│   │       ├── chat.py
│   │       ├── integrations.py
│   │       └── rag.py
│   ├── core/                    # Core services and AI functionality
│   │   ├── llm/                 # LLM integration (Ollama)
│   │   │   ├── model.py
│   │   │   ├── callback_handler.py
│   │   │   └── prompts/         # Prompt templates
│   │   │       ├── agent_prompt.py
│   │   │       ├── chat_prompt.py
│   │   │       └── rag_prompt.py
│   │   ├── agents/              # Agent framework (LangGraph)
│   │   │   ├── agent.py         # Base agent class
│   │   │   ├── state.py         # Agent state management
│   │   │   ├── agent_graph.py   # Agent workflow graph
│   │   │   └── tools/       # Agent tools (Gmail, WhatsApp)
│   │   │       ├── gmail_tool.py
│   │   │       └── whatsapp_tool.py
│   │   ├── rag/             # Retrieval-Augmented Generation
│   │   │   ├── document_processor.py
│   │   │   ├── chunking.py
│   │   │   ├── embedding.py
│   │   │   ├── vector_store.py
│   │   │   ├── search.py
│   │   │   └── retrieval_chain.py
│   │   └── workflows/       # Workflow definitions and automation
│   │       ├── task_router.py
│   │       ├── automation_workflow.py
│   │       └── automation_routines.py
│   ├── database/            # Data layer
│   │   ├── postgres/        # Relational data models and operations
│   │   │   ├── models.py
│   │   │   └── operations.py
│   │   └── vector_db/       # Vector storage and similarity search (pgvector)
│   │       ├── vector_store.py
│   │       └── operations.py
│   └── integrations/        # External service connectors
│       ├── gmail/           # Gmail API integration
│       │   ├── gmail_service.py
│       │   └── gmail_utils.py
│       └── whatsapp/        # WhatsApp Business API integration
│           ├── whatsapp_service.py
│           └── whatsapp_utils.py
├── docs/
│   ├── decisions/               # Architecture Decision Records
│   │   ├── ADR-001-vector-storage.md
│   │   ├── ADR-002-local-llm.md
│   │   ├── ADR-003-framework.md
│   │   ├── ADR-004-evaluation-strategy.md
│   │   ├── ADR-005-ollama-langchain.md
│   │   ├── ADR-006-langfuse-tracing.md
│   │   └── ADR-007-langgraph-agent.md
│   ├── fdd.md
│   ├── hld.md
│   └── PROGRESS.md
├── postgres/
│   └── schema.sql
├── example.env
├── docker-compose.yml
├── README.md
├── CLAUDE.md
└── .gitignore
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

You should see 7 tables: `users`, `agents`, `conversations`, `documents`, `clients`, `messages`, `evaluations`.

Check the vector extension is active:

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

**Option 2 — Terminal**

Confirm pgvector extension works:

```bash
docker exec -it pgvector-db psql -U postgres -d ai_platform -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

Outcomes:

```
  oid  | extname | extowner | extnamespace | extrelocatable | extversion | extconfig | extcondition 
-------+---------+----------+--------------+----------------+------------+-----------+--------------
 16385 | vector  |       10 |         2200 | t              | 0.8.2      |           | 
(1 row)
```

Confirm all 7 tables exist:

```bash
docker exec -it pgvector-db psql -U postgres -d ai_platform -c "\dt"
```

Outcomes:

```
             List of relations
 Schema |     Name      | Type  |  Owner   
--------+---------------+-------+----------
 public | agents        | table | postgres
 public | clients       | table | postgres
 public | conversations | table | postgres
 public | documents     | table | postgres
 public | evaluations   | table | postgres
 public | messages      | table | postgres
 public | users         | table | postgres
(7 rows)
```

**If the tables are missing**, paste the contents of `postgres/schema.sql` directly into the Adminer query box and execute. This creates all tables manually without needing to restart Docker.

---

## Architecture Decisions

### ADR-001: Vector Storage Selection
The platform uses **PostgreSQL with the pgvector extension** for vector storage. This decision was made because it provides:
- Local-first compliance (all data stays on the user's machine)
- Operational simplicity (single database for relational and vector data)
- ACID guarantees and mature tooling
- Sufficient performance for desktop-class workloads (hundreds/thousands of documents)

The `documents` table includes a `vector(768)` column to store embeddings from the `nomic-embed-text` model.

### ADR-007: Agent Orchestration via LangGraph
Agent decision-making is orchestrated using **LangGraph**, replacing manual logic with a stateful graph workflow. Benefits include:
- Clear separation of concerns (nodes for intent analysis, context gathering, action determination, response generation, tool execution)
- Built-in state management and visualization (via Langfuse integration)
- Modularity to easily add new tools and decision points
- Seamless integration with LangChain components and Langfuse for tracing

This architecture leverages the existing LangFuse services (configured in docker-compose.yml) for observability.

---

## Main API endpoints

| Method | Endpoint | What it does |
|---|---|---|
| POST | `/chat` | Send a message to the AI |
| POST | `/agents` | Create a new agent |
| POST | `/rag/ingest` | Upload files to the knowledge base |
| POST | `/integrations/send` | Send a message via Gmail or WhatsApp |
| POST | `/rag/evaluate` | Evaluate the performance of the RAG system |
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