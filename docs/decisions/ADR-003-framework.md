# ADR-003: Web Framework Selection

## Status
Accepted

## Context
The AI Automation Platform requires a web framework to expose RESTful APIs for:
- Chat interactions with AI agents
- Agent creation and management
- Document ingestion and knowledge base operations
- Integration triggers (sending messages via Gmail/WhatsApp)
- Health checks and system monitoring

The framework needs to:
- Support asynchronous operations for concurrent request handling
- Provide automatic API documentation (Swagger/OpenAPI)
- Integrate well with Python 3.11+ and the chosen libraries (Ollama, PostgreSQL, etc.)
- Be lightweight and suitable for a single-user desktop application
- Have good performance for the expected load (low to moderate requests)
- Offer easy development and debugging experience

Options considered:
- Django REST Framework
- FastAPI
- Flask with extensions (Flask-RESTful, Flask-RESTX)
- Starlette (the underlying framework for FastAPI)
- Falcon

## Decision
We selected FastAPI as the web framework.

## Consequences

### Positive
1. **Automatic API Documentation**: Generates Swagger UI and ReDoc automatically from code, reducing documentation overhead
2. **Async Support**: Built-in support for asynchronous request handling, improving concurrency
3. **Performance**: High performance due to Starlette foundations and Pydantic for data validation
4. **Developer Experience**: Modern Python features (type hints) enable excellent editor support and autocompletion
5. **Data Validation**: Pydantic integration provides robust request/response validation and serialization
6. **Dependency Injection**: Built-in system for managing dependencies (database connections, services, etc.)
7. **Minimal Boilerplate**: Less code required to set up endpoints compared to alternatives
8. **Community and Ecosystem**: Growing adoption with good third-party plugin support
9. **Compatibility**: Based on Starlette, so it works with any ASGI server (Uvicorn, Hypercorn, etc.)

### Negative
1. **Learning Curve**: Requires understanding of async Python and type hints for full utilization
2. **Maturity**: Younger framework than Django or Flask, though rapidly maturing
3. **Template Engine**: Not designed for server-side HTML rendering (though we don't need this for an API-centric app)
4. **Plugin Ecosystem**: Fewer mature plugins compared to Django's extensive ecosystem
5. **Async Dependencies**: Requires async-compatible libraries for database operations (we use asyncpg or similar)

### Mitigations
- The development team has experience with async Python and type hints
- Performance benefits outweigh the learning curve for this project
- We are building an API-first application, so lack of template engine is not a drawback
- Critical dependencies (PostgreSQL driver) have async alternatives
- Documentation and examples in the codebase help onboard developers
- The project's scope does not require the extensive ecosystem of Django

## Related Decisions
- This decision complements ADR-002 (local LLM) as FastAPI works well with async calls to Ollama
- Works well with ADR-001 (pgvector) using async PostgreSQL drivers