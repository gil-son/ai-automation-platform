-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agents created by each user
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations between user and agent
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
    role TEXT NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Documents uploaded to the knowledge base
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    content TEXT,
    embedding vector(768), -- nomic-embed-text dimensions
    created_at TIMESTAMP DEFAULT NOW()
);

-- Clients the agent can send messages to
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Messages sent by the agent to clients
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    channel TEXT NOT NULL, -- 'gmail' or 'whatsapp'
    content TEXT NOT NULL,
    status TEXT DEFAULT 'pending', -- 'pending', 'sent', 'failed'
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Evaluation runs for RAG performance monitoring
CREATE TABLE IF NOT EXISTS evaluations (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT NOW(),
    overall_precision FLOAT, -- Average precision across test queries (0-1)
    overall_relevance FLOAT, -- Average relevance across test queries (0-1)
    overall_latency_ms FLOAT, -- Average latency in milliseconds
    status TEXT NOT NULL, -- 'completed' or 'failed'
    error_message TEXT, -- Error message if status is 'failed'
    test_configuration JSONB, -- Stores the test queries and metrics configuration
    detailed_results JSONB -- Stores per-query results and metrics
);