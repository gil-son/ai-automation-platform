# ADR-004: RAG Evaluation Strategy

## Status
Accepted

## Context
The AI Automation Platform needs a way to evaluate the performance of its Retrieval-Augmented Generation (RAG) system to ensure that improvements to the pipeline (chunking strategies, embedding models, retrieval parameters) actually enhance the quality of results. 

Common RAG evaluation frameworks like RAGAS (https://github.com/explodinggradients/ragas) provide comprehensive metrics including:
- Faithfulness: Measures if the generated answer is consistent with the retrieved context
- Answer Relevancy: Measures how relevant the generated answer is to the question
- Context Precision: Measures if the retrieved context is relevant to the question
- Context Recall: Measures how much of the relevant context was retrieved
- Answer Similarity: Semantic similarity between generated and ground truth answers
- Answer Correctness: Fact-based correctness compared to ground truth

However, implementing such a framework would introduce several challenges for our local-first architecture:
1. Dependency on external APIs or large models for semantic similarity measurements
2. Need for ground truth datasets which require manual curation
3. Increased computational complexity and latency
4. Potential violation of local-first principle if external services are required
5. Over-engineering for a single-user desktop application

## Decision
We will implement a lightweight, local-only evaluation approach that focuses on three core metrics that can be computed entirely on the user's machine without external dependencies:
1. **Retrieval Precision**: Measures the relevance of retrieved documents to the query
2. **Answer Relevance**: Measures if the generated answer addresses the query intent
3. **Latency**: Measures end-to-end response time for the RAG pipeline

## Consequences

### Positive
1. **Local-First Compliance**: All evaluation computations happen on the user's machine using existing local models (Ollama)
2. **Minimal Dependencies**: No additional models, APIs, or external services required beyond what's already used
3. **Low Overhead**: Evaluation adds minimal latency and computational cost
4. **Actionable Metrics**: The three chosen metrics directly correlate with user experience improvements
5. **Historical Tracking**: Evaluation runs are stored in the database for trend analysis over time
6. **Simplicity**: Easy to understand, implement, and interpret results
7. **Privacy Preserving**: No evaluation data leaves the user's machine

### Negative
1. **Less Comprehensive**: Doesn't capture all aspects of RAG quality that frameworks like RAGAS measure
2. **Manual Test Case Creation**: Requires users to create test queries with expected outcomes
3. **Limited Semantic Understanding**: Answer relevance is based on keyword matching rather than deep semantic analysis
4. **No Ground Truth Comparison**: Lacks sophisticated answer correctness measurements

### Mitigations
1. **Focus on Core Metrics**: Precision, relevance, and latency are the most important factors for user satisfaction in a local RAG system
2. **User-Friendly Test Creation**: Provide guidelines and examples for creating effective test queries
3. **Configurable Metrics**: Allow users to adjust weighting or add custom metrics in future iterations
4. **Baseline Establishment**: Encourage users to run evaluations after significant changes to establish baselines
5. **Correlation with User Feedback**: While not measuring answer correctness directly, high precision and relevance typically correlate with better answers

## Implementation Details
The evaluation endpoint (POST /rag/evaluate) will:
1. Accept a set of test queries with optional expected outcomes
2. For each query, perform a standard RAG retrieval using the agent's knowledge base
3. Measure retrieval precision by comparing retrieved documents against expected relevant documents (if provided)
4. Measure answer relevance by checking for expected keywords/phrases in retrieved content (if provided)
5. Measure end-to-end latency from query to retrieved results
6. Store the evaluation run in an evaluations table for historical tracking
7. Return aggregated scores and per-query breakdowns

The evaluation uses the same embedding model (nomic-embed-text via Ollama) and similarity search (pgvector cosine similarity) as the main RAG pipeline, ensuring consistency between evaluation and production behavior.

## Related Decisions
- Complements ADR-001 (pgvector) by providing a way to measure the effectiveness of the vector search implementation
- Relates to ADR-002 (local LLM) as evaluation uses the same local Ollama infrastructure
- Supports iterative improvement of the RAG pipeline mentioned in ADR-003 (Web Framework Selection) by providing measurable feedback