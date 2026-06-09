# Functional Design Document: AI Automation Platform

## API Endpoints

### 1. POST /chat
**Purpose**: Send a message to the AI agent and receive a response

**Request Schema**:
```json
{
  "message": "string (required)",
  "agent_id": "integer (optional, defaults to user's active agent)",
  "conversation_id": "integer (optional, creates new conversation if not provided)"
}
```

**Response Schema**:
```json
{
  "response": "string",
  "conversation_id": "integer",
  "message_id": "integer",
  "agent_id": "integer",
  "created_at": "timestamp"
}
```

**Business Rules**:
- If no agent_id is provided, use the user's most recently active agent
- If no conversation_id is provided, create a new conversation for this agent
- Store both user message and agent response in the conversations table
- Agent response is generated using RAG pipeline: retrieve relevant document chunks, construct prompt with context, call LLM
- Agent can execute actions (send messages) based on detected intent in user message
- Maintain conversation history for context in subsequent messages

**Error Cases**:
- 400: Missing required message field
- 404: Specified agent_id not found or doesn't belong to user
- 404: Specified conversation_id not found or doesn't belong to agent
- 500: LLM service unavailable (Ollama not running or model not loaded)
- 500: Database connection failure

**DB Tables Touched**:
- conversations (INSERT for user message, INSERT for agent response)
- agents (READ to verify ownership and get agent details)
- documents (READ during RAG search for relevant context)
- users (READ to verify agent ownership)

### 2. POST /agents
**Purpose**: Create a new AI agent for the user

**Request Schema**:
```json
{
  "name": "string (required)",
  "description": "string (optional)"
}
```

**Response Schema**:
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "user_id": "integer",
  "created_at": "timestamp"
}
```

**Business Rules**:
- Associate the new agent with the authenticated user (from auth context)
- Agent name must be unique per user (enforced at application level)
- Description defaults to empty string if not provided
- Created timestamp is set automatically

**Error Cases**:
- 400: Missing required name field
- 400: Agent name already exists for this user
- 401: User not authenticated
- 500: Database creation failure

**DB Tables Touched**:
- agents (INSERT new record)
- users (READ to get user_id from auth context)

### 3. POST /rag/ingest
**Purpose**: Upload and process files for the knowledge base

**Request Schema**:
```
multipart/form-data:
- files: array of file objects (required)
- agent_id: integer (required, specifies which agent's knowledge base to update)
```

**Response Schema**:
```json
{
  "ingested_count": "integer",
  "failed_count": "integer",
  "documents": [
    {
      "id": "integer",
      "filename": "string",
      "status": "string (success/failed)",
      "error": "string (optional, present only if failed)",
      "chunks_created": "integer"
    }
  ]
}
```

**Business Rules**:
- Process each file: extract text, split into chunks, generate embeddings, store in vector DB
- Supported file types: PDF, DOC/DOCX, TXT (based on available libraries)
- Chunking strategy: configurable size with overlap (default: 500 chars with 50 char overlap)
- Embedding model: nomic-embed-text via Ollama (768 dimensions)
- Store original files in data/raw/, processed chunks referenced in documents table
- Associate documents with specified agent_id
- Replace existing documents with same filename for the agent (update rather than duplicate)

**Error Cases**:
- 400: Missing required files or agent_id
- 404: Specified agent_id not found or doesn't belong to user
- 413: File too large (configurable limit, default 50MB)
- 415: Unsupported file type
- 500: Ollama service unavailable for embedding generation
- 500: Vector database storage failure
- 500: Text extraction failure for specific file types

**DB Tables Touched**:
- documents (INSERT/UPDATE records for each file)
- agents (READ to verify ownership)
- users (READ to get user_id from auth context)

### 4. POST /integrations/send
**Purpose**: Send a message via Gmail or WhatsApp

**Request Schema**:
```json
{
  "agent_id": "integer (required)",
  "channel": "string (required, enum: ['gmail', 'whatsapp'])",
  "content": "string (required)",
  "client_id": "integer (required)",
  "subject": "string (required for gmail, optional for whatsapp)"
}
```

**Response Schema**:
```json
{
  "id": "integer",
  "channel": "string",
  "status": "string (enum: ['pending', 'sent', 'failed'])",
  "sent_at": "timestamp (nullable)",
  "created_at": "timestamp"
}
```

**Business Rules**:
- Validate that agent_id belongs to authenticated user
- Validate that client_id belongs to authenticated user
- Check that required integration credentials are configured in .env:
  - For gmail: GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET
  - For whatsapp: WHATSAPP_API_TOKEN, WHATSAPP_PHONE_NUMBER_ID
- Format message according to channel requirements:
  - Gmail: requires subject, recipient email from client record
  - WhatsApp: recipient phone number from client record, no subject
- Set initial status to 'pending'
- Attempt to send via appropriate API
- Update status to 'sent' on success or 'failed' on error
- Record timestamp when sent

**Error Cases**:
- 400: Missing required fields
- 400: Invalid channel value
- 404: Specified agent_id not found or doesn't belong to user
- 404: Specified client_id not found or doesn't belong to user
- 400: Missing required integration credentials for specified channel
- 400: Missing recipient contact info (email for gmail, phone for whatsapp)
- 500: External API failure (Gmail or WhatsApp service error)
- 500: Authentication failure with external service
- 500: Rate limit exceeded from external service

**DB Tables Touched**:
- messages (INSERT new record)
- agents (READ to verify ownership)
- clients (READ to verify ownership and get contact info)
- users (READ to get user_id from auth context)

### 5. GET /health
**Purpose**: Check system health and service availability

**Request Schema**: None (GET request with no body)

**Response Schema**:
```json
{
  "status": "string (enum: ['healthy', 'degraded', 'unhealthy'])",
  "timestamp": "timestamp",
  "services": {
    "api": "string (enum: ['healthy', 'unhealthy'])",
    "database": "string (enum: ['healthy', 'unhealthy'])",
    "ollama": "string (enum: ['healthy', 'unhealthy', 'unknown'])",
    "vector_store": "string (enum: ['healthy', 'unhealthy'])"
  },
  "version": "string"
}
```

**Business Rules**:
- API service: always healthy if endpoint responds
- Database: check connectivity and basic query execution
- Ollama: check if service is reachable and llama3.2 model is available
- Vector store: check if pgvector extension is available and functional
- Overall status:
  - healthy: all critical services (api, database) healthy
  - degraded: api healthy but one or more non-critical services unhealthy
  - unhealthy: api unhealthy or database unhealthy

**Error Cases**:
- 503: Service unavailable (when API itself is unhealthy)
- Note: This endpoint should ideally not return 500; unhealthy services are reported in response body

**DB Tables Touched**:
- None for basic health check
- May touch any table for detailed connectivity test (typically users table for simplest query)

### 6. POST /rag/evaluate
**Purpose**: Evaluate the performance of the RAG system using lightweight local metrics

**Request Schema**:
```json
{
  "agent_id": "integer (required)",
  "test_queries": [
    {
      "query": "string (required)",
      "expected_relevant_document_ids": "array of integers (optional)",
      "expected_answer_contains": "array of strings (optional)"
    }
  ],
  "metrics": "array of strings (optional, defaults to ['precision', 'relevance', 'latency'])",
  "top_k": "integer (optional, defaults to 5)"
}
```

**Response Schema**:
```json
{
  "evaluation_id": "integer",
  "agent_id": "integer",
  "timestamp": "timestamp",
  "overall_scores": {
    "precision": "float (0-1)",
    "relevance": "float (0-1)",
    "latency_ms": "float"
  },
  "query_results": [
    {
      "query": "string",
      "precision": "float (0-1)",
      "relevance": "float (0-1)",
      "latency_ms": "float",
      "retrieved_documents": [
        {
          "document_id": "integer",
          "filename": "string",
          "score": "float"
        }
      ],
      "expected_relevant_found": "integer",
      "total_expected_relevant": "integer"
    }
  ],
  "status": "string (enum: ['completed', 'failed'])",
  "error_message": "string (optional)"
}
```

**Business Rules**:
- Requires authentication context to verify agent ownership
- Agent must exist and belong to the authenticated user
- If test_queries is empty, returns error 400
- For each test query:
  - Performs RAG search using the agent's knowledge base
  - Measures latency from query submission to result retrieval
  - Calculates precision as (number of expected relevant documents found) / (total number of retrieved documents)
  - Calculates relevance based on whether expected answer phrases are present in retrieved content (if expected_answer_contains provided)
  - If expected_relevant_document_ids provided, calculates precision based on overlap with retrieved documents
- Overall scores are averages across all test queries
- Stores evaluation run and results in the evaluations table for historical tracking
- Does not require external APIs or services - uses only local Ollama models for embeddings and LLM
- Evaluation does not modify any existing data - read-only operation on documents and embeddings

**Error Cases**:
- 400: Missing required agent_id field
- 400: Missing or empty test_queries array
- 404: Specified agent_id not found or doesn't belong to user
- 400: Invalid metrics values (must be subset of ['precision', 'relevance', 'latency'])
- 400: Invalid top_k value (must be positive integer)
- 500: Ollama service unavailable for embedding generation
- 500: Vector database query failure
- 500: Internal server error during evaluation processing

**DB Tables Touched**:
- evaluations (INSERT new evaluation run and results)
- agents (READ to verify ownership and get agent details)
- documents (READ during RAG search for relevant context - no modifications)
- users (READ to get user_id from auth context)

## RAG Pipeline Flow

1. **Document Ingestion**:
   - User uploads file via POST /rag/ingest
   - File saved to data/raw/ directory
   - Text extraction based on file type (PDF→PyPDF2, DOCX→python-docx, TXT→direct read)
   - Text split into chunks with configurable overlap
   - Each chunk embedded using nomic-embed-text model via Ollama
   - Chunks stored in PostgreSQL with pgvector:
     - content: text chunk
     - embedding: 768-dimensional vector
     - metadata: filename, agent_id, chunk index
   - Reference to processed file maintained in data/processed/

2. **Query Processing** (during POST /chat):
   - User message received
   - Message embedded using same nomic-embed-text model
   - Cosine similarity search performed against document vectors:
     - Query: SELECT * FROM documents WHERE agent_id = $1 ORDER BY embedding <=> $2 LIMIT $3
     - Where $2 is the query embedding, $3 is limit (typically 5-10 results)
   - Top-k most relevant chunks retrieved
   - Context constructed from retrieved chunks
   - Final prompt constructed: [System Prompt] + [Conversation History] + [Context] + [User Query]
   - Prompt sent to Llama 3.2 model via Ollama
   - Generated response returned to user
   - Both user query and agent response stored in conversations table

## Agent Decision Flow

1. **Message Reception**:
   - User message received via POST /chat
   - System retrieves conversation history for context

2. **Intent Analysis**:
   - Agent analyzes message for actionable intentions:
     - Communication intent: "send email to X", "message Y on WhatsApp"
     - Information request: questions about uploaded documents
     - Conversational: general chat, follow-ups
   - Simple rule-based or LLM-based intent detection (configurable)

3. **Context Gathering**:
   - For information requests: trigger RAG pipeline to retrieve relevant document chunks
   - For communication actions: extract parameters (recipient, content, channel)
   - For conversational: use conversation history and agent instructions

4. **Action Determination**:
   - If communication intent detected with sufficient confidence:
     - Validate recipient exists in clients table
     - Generate message content (use RAG context if available, otherwise from user instructions)
     - Execute via appropriate integration (Gmail/WhatsApp)
     - Record message attempt in messages table
   - If information request:
     - Use RAG context to inform LLM response
   - If conversational:
     - Generate response based on conversation history and agent personality

5. **Response Generation**:
   - Construct final prompt including:
     - Agent system instructions/personality
     - Conversation history (last N messages)
     - Relevant context from RAG (if applicable)
     - User's current message
   - Send prompt to Llama 3.2 via Ollama
   - Receive and post-process response
   - Store agent response in conversations table
   - Return response to user

6. **Learning & Adaptation** (Future Enhancement):
   - Track which responses users find helpful (via feedback mechanism)
   - Adjust retrieval parameters or agent behavior based on interactions
   - Update agent instructions based on successful patterns