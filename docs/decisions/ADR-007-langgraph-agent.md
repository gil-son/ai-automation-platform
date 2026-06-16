# ADR-007: Agent Orchestration via LangGraph

## Status
Accepted

## Context
The AI Automation Platform currently uses manual decision-making logic (as described in docs/fdd.md, Agent Decision Flow) to determine agent actions based on user intent. This approach involves:
1. **Message Reception**: User message received via POST /chat, system retrieves conversation history for context.
2. **Intent Analysis**: Agent analyzes message for actionable intentions (communication intent, information request, conversational) using simple rule-based or LLM-based intent detection.
3. **Context Gathering**: For information requests: trigger RAG pipeline to retrieve relevant document chunks; for communication actions: extract parameters (recipient, content, channel); for conversational: use conversation history and agent instructions.
4. **Action Determination**: If communication intent detected with sufficient confidence: validate recipient, generate message content, execute via integration (Gmail/WhatsApp), record message attempt. If information request: use RAG context to inform LLM response. If conversational: generate response based on conversation history and agent personality.
5. **Response Generation**: Construct final prompt including agent system instructions/personality, conversation history, relevant context from RAG, user's current message; send prompt to Llama 3.2 via Ollama; receive and post-process response; store agent response in conversations table; return response to user.

As the agent's capabilities grow, this manual logic becomes difficult to maintain and extend. LangGraph provides a framework for building stateful, multi-actor applications with LLMs, making it ideal for agent orchestration. It allows modeling agent behavior as a graph of nodes (actions, decisions) and edges (transitions), with built-in state management.

## Decision
We will replace the manual decision-making logic with LangGraph to orchestrate agent behavior. The agent's state, decisions, and actions will be modeled as nodes and edges in a LangGraph StateGraph. This enables:
- Clear separation of concerns (each node has a single responsibility)
- Stateful interactions across multiple steps
- Conditional branching based on agent state and tool outputs
- Easy integration of new tools and decision points
- Visualization and debugging of agent workflows

## Consequences

### Positive
1. **State Management**: Built-in state persistence and management across agent interactions, eliminating manual state passing.
2. **Workflow Visualization**: Ability to visualize and debug agent workflows using LangGraph Studio or Langfuse integration.
3. **Modularity**: Easy to add new nodes (decision points, actions) without modifying existing logic; each node is a standalone function.
4. **Integration**: Seamless integration with LangChain components (LLMs, tools, memory) and Langfuse for tracing.
5. **Scalability**: Supports complex workflows with cycles, conditional logic, and parallel execution (e.g., running multiple tools in parallel).
6. **LangChain Ecosystem**: Leverages the broader LangChain ecosystem for agents, tools, and memory.

### Negative
1. **Learning Curve**: Requires understanding of LangGraph concepts (nodes, edges, state, StateGraph).
2. **Migration Effort**: Requires rewriting existing decision-making logic into a graph-based structure.
3. **Overhead**: Minimal overhead from the LangGraph framework (negligible for typical usage).
4. **Debugging Complexity**: Debugging distributed workflows can be more complex than linear code, though tooling mitigates this.

### Mitigations
- Provide documentation and examples of LangGraph usage in the codebase.
- Start with simple workflows (e.g., a linear chain) and gradually migrate complex logic.
- Performance impact is minimal and outweighed by maintainability benefits.
- Use LangGraph Studio for local debugging and visualization of workflows.

## Related Decisions
- Enabled by ADR-005 (LLM Integration via LangChain) which provides the LLM component and LangChain integration.
- Complements ADR-006 (Langfuse Tracing) for observing agent workflows and debugging.
- Relates to ADR-003 (Web Framework Selection) as FastAPI works well with asynchronous LangGraph execution.
- Builds upon the orchestrator framework decision in HLD (LangChain & LangGraph) by specifying the concrete implementation.

## Implementation Notes
- Define an AgentState that includes conversation history, user message, agent instructions, tool outputs, and control flow flags.
- Create nodes for:
  - Intent Analysis: Determine user intent (communication, information, conversational)
  - Context Gathering: For information requests, trigger RAG; for communication, extract parameters
  - Action Determination: Based on intent, route to appropriate action nodes
  - Response Generation: Construct prompt and call LLM
  - Tool Execution: Execute communication tools (Gmail/WhatsApp) or other tools
- Use conditional edges to route between nodes based on state.
- Integrate with Langfuse via LangChain callbacks for automatic tracing.