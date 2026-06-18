# High-Level Design: AI Automation Platform

## System Overview

The AI Automation Platform is a local-first AI assistant that enables users to interact with their personal data through natural language, create intelligent agents that learn from uploaded documents, and automate communications via Gmail and WhatsApp. The system operates entirely on the user's machine, ensuring data privacy and control.

## Component Diagram (ASCII)

```
+---------------------+     +---------------------+     +---------------------+
|     Frontend/API    |     |   Core Services     |     |   Data Layer        |
|  (app/main.py)      |     |  (app/core/)        |     |  (app/database/)    |
|                     |     |                     |     |                     |
|  +----------------+  |     |  +--------------+   |     |  +--------------+  |
|  |   HTTP Routes  |  |     |  |     LLM      |---+----->|  | PostgreSQL   |  |
|  | (chat, agents, |  |     |  | (Ollama,     |   |     |  |   DB Layer   |  |
|  |  RAG, etc.)    |  |     |  |  Prompts)    |   |     |  +--------------+  |
|  +----------------+  |     |  +--------------+   |     |                     |
|                     |     |  +--------------+   |     |  +--------------+  |
|  +----------------+  |     |  |    Agents    |---+----->|  |  Vector DB   |  |
|  | Request/Response|  |     |  | (Memory,     |   |     |  | (pgvector)   |  |
|  |   Schemas      |  |     |  |  Tools, Logic)|   |     |  +--------------+  |
|  +----------------+  |     |  +--------------+   |     |                     |
|                     |     |  +--------------+   |     |  +--------------+  |
|  +----------------+  |     |  |     RAG      |---+----->|  |  Filesystem  |  |
|  | Middleware,    |  |     |  | (Ingestion,  |   |     |  | (data/raw,   |  |
|  |  Auth, etc.)   |  |     |  |  Chunking,   |   |     |  | data/processed)|
|  +----------------+  |     |  |  Embedding,  |   |     |  +--------------+  |
|                     |     |  |  Search)     |   |     |                     |
|                     |     |  +--------------+   |     |                     |
|                     |     |  +--------------+   |     |                     |
|                     |     |  |  Workflows   |   |     |                     |
|                     |     |  | (Automation, |   |     |                     |
|                     |     |  |  Task Routing)|   |     |                     |
|                     |     |  +--------------+   |     |                     |
+---------------------+     +---------------------+     +---------------------+

+---------------------+     +---------------------+
|  Integrations       |     |  Infrastructure     |
|  (app/integrations/)|     |  (docker-compose.yml)|
|                     |     |                     |
|  +--------------+   |     |  +--------------+  |
|  |   Gmail      |   |     |  |   PostgreSQL  | |
|  | (API Client) |   |     |  |   + pgvector  | |
|  +--------------+   |     |  +--------------+  |
|                     |     |                     |
|  +--------------+   |     |  +--------------+  |
|  | WhatsApp     |   |     |  |   Adminer     | |
|  | (API Client) |   |     |  |   (UI)        | |
|  +--------------+   |     |  +--------------+  |
|                     |     |                     |
|                     |     |  +--------------+  |
|                     |     |  |   Ollama      | |
|                     |     |  |   (LLM Server)| |
|                     |     |  +--------------+  |
+---------------------+     +---------------------+
```
*Note: The Core Services components (LLM, Agents, RAG, Workflows) are now implemented using LangChain and LangGraph, with Langfuse for distributed tracing.*

## Data Flow

### Upload Pipeline (Document Ingestion)
1. User uploads file via `/rag/ingest` endpoint
2. File stored in `data/raw/` directory
3. RAG service processes file:
   - Text extraction (PDF, DOC, TXT)
   - Document chunking into smaller segments
   - Embedding generation using local Ollama model (nomic-embed-text)
   - Vector storage in PostgreSQL with pgvector extension
4. Processed chunks saved to `data/processed/`
5. Metadata (filename, agent association) stored in documents table

### Query Pipeline (Chat/Question Answering)
1. User sends message via `/chat` endpoint
2. System retrieves user's active agent context
3. RAG service performs similarity search:
   - Query embedded using same Ollama model
   - Cosine similarity search against document vectors
   - Top-k relevant chunks retrieved
4. Retrieved context combined with user query and agent instructions
5. Prompt constructed and sent to Ollama Llama 3.2 model
6. Generated response returned to user
7. Conversation stored in database for context persistence

### Action Pipeline (Message Sending)
1. User issues command like "Send email to John about project update"
2. Agent analyzes intent and extracts parameters:
   - Recipient (from clients table or extracted from message)
   - Channel (Gmail/WhatsApp based on available config)
   - Content (generated using RAG context and user instructions)
3. Integration service validates credentials from environment
4. Message formatted according to channel requirements
5. External API called (Gmail API or WhatsApp Business API)
6. Message status recorded in messages table
7. Result returned to user

## Technology Choices & Rationale

### Backend Framework: Python/FastAPI
- **Rationale**: High performance, automatic API documentation, excellent Python ecosystem integration, async support for concurrent operations
- **Alternative Considered**: Django (too heavyweight for microservice-style architecture)

### Database: PostgreSQL with pgvector
- **Rationale**: ACID compliance for critical data, mature ecosystem, pgvector provides efficient vector similarity search without separate vector DB
- **Alternative Considered**: Pinecone/Weaviate (would compromise local-first principle), SQLite + FAISS (less production-ready for concurrent access)

### AI Model: Llama 3.2 via Ollama
- **Rationale**: Strong performance for local deployment, good balance of capability/resource usage, permissive license, active community
- **Alternative Considered**: Mistral, Phi-3 (selected Llama 3.2 for better reasoning capabilities)
- **Integration**: Using LangChain's ChatOllama for seamless integration with LangChain components

### Vector Embeddings: nomic-embed-text
- **Rationale**: 768-dimensional vectors optimized for text search, good performance/quality trade-off, open source
- **Alternative Considered**: OpenAI embeddings (would violate local-first principle), sentence-transformers (similar performance)
- **Integration**: Using LangChain embeddings wrapper for nomic-embed-text

### Orchestration Framework: LangChain & LangGraph
- **Rationale**: Provides standardized interfaces for LLMs, vector stores, and agents; enables complex workflows with state management; supports local-first deployment
- **Alternative Considered**: Manual pipeline logic (current implementation), LlamaIndex (chosen LangChain for broader ecosystem and LangGraph for agent orchestration)
- **Components**: 
  - LangChain for LLM abstraction, embedding integration, and vector store connectivity
  - LangGraph for agent orchestration, replacing manual decision-making logic
  - Langfuse integration for tracing and monitoring

### Tracing: Langfuse
- **Rationale**: Local-first tracing solution that integrates with LangChain/LangGraph; provides observability without external dependencies; complies with privacy requirements
- **Alternative Considered**: LangSmith (requires external account and data transmission), custom logging (chosen Langfuse for built-in LangChain integration and UI)
- **Benefits**: 
  - Automatic tracing of LLM calls, chain executions, and agent operations
  - Local storage of trace data
  - Visualization via Langfuse UI (can be run locally via Docker)
  - Compatibility with LangChain and LangGraph out-of-the-box

### Containerization: Docker Compose
- **Rationale**: Simplifies setup of PostgreSQL+pgvector and Adminer, ensures consistent environments, easy local development
- **Alternative Considered**: Manual installation (creates setup friction for users)

### File System: Local Storage
- **Rationale**: Maintains local-first principle, simple backup/restore, no external dependencies
- **Alternative Considered**: Cloud storage (would compromise privacy goals)

## External Dependencies

### Runtime Dependencies
1. **Ollama** - Local LLM inference server (runs Llama 3.2 and nomic-embed-text models)
2. **PostgreSQL** - Primary database with pgvector extension for vector storage
3. **Python 3.11+** - Backend runtime

### API Dependencies (Optional - only if features used)
1. **Gmail API** - For email sending (requires OAuth credentials)
2. **WhatsApp Business API** - For WhatsApp messaging (requires Meta Business account)

### Development Dependencies
1. **Docker & Docker Compose** - For local development and testing
2. **Git** - Version control

## Non-Functional Requirements

### Local-First Architecture
- **Requirement**: All data processing and storage occurs on user's machine
- **Implementation**: 
  - No data leaves the local environment unless explicitly sent via user-initiated actions (email/WhatsApp)
  - LLM models run locally via Ollama
  - Vector database is local PostgreSQL instance
  - File storage is local filesystem

### Latency Considerations
- **Target**: <2 second response time for simple queries on adequate hardware
- **Factors affecting latency**:
  - LLM inference time (dependent on hardware and model quantization)
  - Vector search performance (pgvector with proper indexing)
  - File I/O for document retrieval
- **Mitigations**:
  - Chunk size optimization for relevant context retrieval
  - Efficient embedding model selection
  - Connection pooling for database access

### RAM Constraints
- **Minimum**: 8GB RAM recommended for smooth operation
- **Breakdown**:
  - Ollama Llama 3.2: ~4-6GB RAM (depending on quantization)
  - PostgreSQL: ~512MB-1GB for cache and connections
  - Python/FastAPI: ~200-500MB
  - Operating system and other processes: ~1-2GB
- **Scalability**: 
  - With 16GB+ RAM: Can run larger models or multiple concurrent users
  - With 4-8GB RAM: May need to use smaller models or quantized versions

### Security & Privacy
- **Data Isolation**: Each user's data is isolated via user_id foreign keys
- **Credential Management**: API keys stored in environment variables (.env file)
- **Network Exposure**: Services bind to localhost by default; external access requires explicit configuration
- **Audit Trail**: All conversations, documents, and messages stored with timestamps

### Reliability
- **Data Durability**: PostgreSQL ensures ACID compliance for all structured data
- **File Persistence**: Uploaded files stored on disk with configurable retention
- **Service Resilience**: Docker-compose restart policies ensure service recovery
- **Backup Strategy**: Users can backup `.env`, `data/`, and PostgreSQL volume for complete recovery

## Deployment Model
- **Single-user desktop application** designed for personal/local use
- **Not designed for multi-user SaaS deployment** without significant modifications
- **Horizontal scaling** not applicable; vertical scaling via hardware resources
- **Typical deployment**: One instance per user machine