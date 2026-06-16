# ADR-006: Tracing via Langfuse (Self-Hosted)

## Status
Accepted

## Context
The AI Automation Platform requires observability into LLM calls, chain executions, and agent operations to debug and monitor performance. Given the local-first architecture, data must not leave the user's machine. LangSmith (by LangChain) requires an external account and sends data to their servers, which violates the local-first principle. Langfuse offers a self-hosted, open-source alternative that can run locally via Docker, keeping all trace data on the user's machine.

## Decision
We will use Langfuse (self-hosted via Docker Compose) for distributed tracing of LLM calls, LangChain executions, and LangGraph workflows. Langfuse will be integrated via its LangChain SDK, which automatically captures traces when configured.

## Consequences

### Positive
1. **Local-First Compliance**: All trace data is stored in a local PostgreSQL database (part of the Langfuse stack) and does not leave the user's machine unless explicitly shared.
2. **Seamless Integration**: Langfuse provides official SDKs for LangChain and LangGraph, enabling automatic tracing with minimal code changes.
3. **Rich UI**: Provides a web-based UI for visualizing traces, inspecting inputs/outputs, and monitoring performance.
4. **Cost Effective**: Open-source and free to self-host; no per-trace costs.
5. **Extensible**: Supports custom metrics, feedback scores, and integration with other observability tools.

### Negative
1. **Additional Infrastructure**: Requires running additional services (Langfuse API and PostgreSQL) via Docker Compose.
2. **Resource Usage**: The Langfuse stack consumes additional RAM and CPU (approximately 512MB-1GB).
3. **Setup Complexity**: Adds another service to the docker-compose.yml file and requires initial configuration.
4. **Version Management**: Need to track Langfuse version and update periodically.

### Mitigations
- The Langfuse service is lightweight and can be configured to use minimal resources.
- Documentation will be provided on how to set up and configure Langfuse via Docker Compose.
- Performance impact on the main application is minimal as tracing is asynchronous.
- We will pin the Langfuse Docker image version to ensure stability.

## Related Decisions
- Enabled by ADR-005 (LLM Integration via LangChain) as Langfuse integrates via LangChain callbacks.
- Complements ADR-007 (LangGraph Agent Orchestration) by providing traceability for agent workflows.
- Relates to ADR-003 (Web Framework Selection) as FastAPI works well with asynchronous tracing.

## Implementation Notes
- Add Langfuse service to docker-compose.yml with a PostgreSQL database for persistence.
- Set environment variables LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY (can be generated).
- In the application, configure the Langfuse handler for LangChain callbacks.