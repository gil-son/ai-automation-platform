# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup
1. Copy environment file and configure:
   ```bash
   cp example.env .env
   # Edit .env with your API keys and configuration
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Pull the AI model:
   ```bash
   ollama pull llama3.2
   ```

4. Start database and services:
   ```bash
   docker-compose up -d
   ```

### Running the Application
- Start the application:
  ```bash
  python app/main.py
  ```
- The API will be available at `http://localhost:8000`
- API documentation at `http://localhost:8000/docs`

### Database Management
- Verify database setup:
  ```bash
  # Via Adminer UI
  open http://localhost:5001
  
  # Via terminal
  docker exec -it pgvector-db psql -U postgres -d ai_platform -c "\dt"
  ```
- If tables are missing, manually apply schema:
  ```bash
  docker exec -i pgvector-db psql -U postgres -d ai_platform < ./postgres/schema.sql
  ```

### Scripts
- Ingest documents into knowledge base:
  ```bash
  python scripts/ingest_documents.py
  ```
- Evaluate RAG performance:
  ```bash
  python scripts/evaluate_rag.py
  ```

## Code Architecture

### Core Structure
The application follows a modular architecture organized around these key components:

1. **Entry Point**: `app/main.py` - FastAPI application initialization
2. **API Layer**: `app/api/` - HTTP endpoints organized by feature
   - `routes/` - Endpoint implementations (chat, agents, RAG, integrations, evaluation)
   - `schemas/` - Pydantic models for request/response validation
3. **Core Services**: `app/core/` - Business logic and AI functionality
   - `llm/` - Ollama client integration and prompt management
   - `agents/` - Agent creation, memory, and decision-making logic
   - `rag/` - Retrieval-Augmented Generation pipeline (file ingestion, chunking, embedding, search)
   - `workflows/` - Automation routines and task routing logic
4. **Integrations**: `app/integrations/` - External service connectors
   - `gmail/` - Email sending via Gmail API
   - `whatsapp/` - WhatsApp Business API integration
5. **Data Layer**: `app/database/` - Persistence layer
   - `postgres/` - Relational data models and operations
   - `vector_db/` - Vector storage and similarity search using pgvector
6. **Data Storage**: `data/` directory for file persistence
   - `raw/` - Original uploaded files
   - `processed/` - Processed chunks after ingestion

### Key Technologies
- **Backend**: Python/FastAPI
- **Database**: PostgreSQL with pgvector extension for vector storage
- **AI Model**: Llama 3.2 via Ollama (local inference)
- **Vector Operations**: pgvector for similarity search
- **Containerization**: Docker Compose for service orchestration

### Data Flow
1. File Upload → Document Processing → Vector Embedding → Storage in pgvector
2. User Query → Similarity Search → Context Retrieval → LLM Response Generation
3. Action Commands → Intent Recognition → Tool Execution (Gmail/WhatsApp) → Response

## Common Tasks

### Adding New API Endpoints
1. Define schema in `app/api/schemas/`
2. Implement route in `app/api/routes/`
3. Register router in main API router
4. Add corresponding service logic in `app/core/`

### Extending Agent Capabilities
1. Add new tools in `app/core/agents/tools/`
2. Update agent prompt templates in `app/core/llm/prompts/`
3. Modify agent logic in `app/core/agents/` as needed

### Adding New Integrations
1. Create new directory in `app/integrations/`
2. Implement service following existing patterns
3. Expose via API routes in `app/api/routes/`
4. Add configuration to `.env` and config modules

### Working with Vectors
- Embeddings are handled in `app/core/rag/`
- Search operations use cosine similarity via pgvector
- Chunking strategies configurable in RAG module