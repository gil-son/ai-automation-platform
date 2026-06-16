# ADR-005: LLM Integration via LangChain

## Status
Accepted

## Context
The AI Automation Platform uses Llama 3.2 via Ollama for local LLM inference. Initially, the raw ollama Python library was used for direct API calls to the Ollama server. However, to integrate with LangChain components and leverage its ecosystem (such as LangGraph for agent orchestration and Langfuse for tracing), we decided to use LangChain's ChatOllama wrapper.

## Decision
We will use LangChain's ChatOllama class to interact with the Ollama server running Llama 3.2, replacing direct calls to the ollama library.

## Consequences

### Positive
1. **LangChain Integration**: Seamless integration with LangChain components (LLMs, embeddings, chains, agents)
2. **Ecosystem Benefits**: Access to LangChain's extensive ecosystem of integrations and utilities
3. **Consistent Interface**: Uniform way to interact with LLMs, making it easier to swap models or providers in the future
4. **Tracing Support**: Better compatibility with Langfuse for distributed tracing
5. **Reduced Boilerplate**: LangChain handles retry logic, timeout management, and other concerns

### Negative
1. **Additional Dependency**: Adds LangChain as a dependency
2. **Learning Curve**: Requires understanding of LangChain's abstraction layers
3. **Performance Overhead**: Minimal overhead introduced by the LangChain wrapper (negligible)
4. **Version Coupling**: Tied to LangChain's release schedule for updates

### Mitigations
- LangChain is lightweight and well-maintained
- Documentation and examples will be provided in the codebase
- Performance impact is minimal and outweighed by integration benefits
- We will pin LangChain version to ensure stability

## Related Decisions
- Relates to ADR-002 (Local LLM Selection) as it uses the same Ollama server and model
- Enables ADR-007 (LangGraph Agent Orchestration) by providing the LLM component
- Supports ADR-006 (Langfuse Tracing) through LangChain's callback system