import sys

def main():
    # Read the file
    with open('/home/gilson/Workflow/Repositories/ai-automation-platform/README.md', 'r') as f:
        lines = f.readlines()

    # Find the line index of "## Project structure"
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip() == '## Project structure':
            start_idx = i
            break

    if start_idx is None:
        print("Could not find '## Project structure'")
        sys.exit(1)

    # Find the start of the code block (next line that starts with '```')
    code_start = start_idx + 1
    while code_start < len(lines) and not lines[code_start].strip().startswith('```'):
        code_start += 1
    if code_start >= len(lines):
        print("Could not find opening ``` after the header")
        sys.exit(1)

    # Find the end of the code block (next line that starts with '```' after code_start+1)
    code_end = code_start + 1
    while code_end < len(lines) and not lines[code_end].strip().startswith('```'):
        code_end += 1
    if code_end >= len(lines):
        print("Could not find closing ```")
        sys.exit(1)

    # Now we want to replace lines from code_start to code_end (inclusive) with our new code block
    new_code_block = [
        "```\n",
        "ai-automation-platform/\n",
        "├── app/\n",
        "│   ├── main.py                  # App entry point\n",
        "│   ├── api/\n",
        "│   │   ├── routes/              # API route implementations\n",
        "│   │   │   ├── agents.py\n",
        "│   │   │   ├── chat.py\n",
        "│   │   │   ├── rag.py\n",
        "│   │   │   ├── integrations.py\n",
        "│   │   │   └── health.py\n",
        "│   │   └── schemas/             # Pydantic models for request/response\n",
        "│   │       ├── agents.py\n",
        "│   │       ├── chat.py\n",
        "│   │       ├── integrations.py\n",
        "│   │       └── rag.py\n",
        "│   ├── core/                    # Core services and AI functionality\n",
        "│   │   ├── llm/                 # LLM integration (Ollama)\n",
        "│   │   │   ├── model.py\n",
        "│   │   │   ├── callback_handler.py\n",
        "│   │   │   └── prompts/         # Prompt templates\n",
        "│   │   │       ├── agent_prompt.py\n",
        "│   │   │       ├── chat_prompt.py\n",
        "│   │   │       └── rag_prompt.py\n",
        "│   │   ├── agents/              # Agent framework (LangGraph)\n",
        "│   │   │   ├── agent.py         # Base agent class\n",
        "│   │   │   ├── state.py         # Agent state management\n",
        "│   │   │   ├── agent_graph.py   # Agent workflow graph\n",
        "│   │   │   └── tools/       # Agent tools (Gmail, WhatsApp)\n",
        "│   │   │       ├── gmail_tool.py\n",
        "│   │   │       └── whatsapp_tool.py\n",
        "│   │   ├── rag/             # Retrieval-Augmented Generation\n",
        "│   │   │   ├── document_processor.py\n",
        "│   │   │   ├── chunking.py\n",
        "│   │   │   ├── embedding.py\n",
        "│   │   │   ├── vector_store.py\n",
        "│   │   │   ├── search.py\n",
        "│   │   │   └── retrieval_chain.py\n",
        "│   │   └── workflows/       # Workflow definitions and automation\n",
        "│   │       ├── task_router.py\n",
        "│   │       ├── automation_workflow.py\n",
        "│   │       └── automation_routines.py\n",
        "│   ├── database/            # Data layer\n",
        "│   │   ├── postgres/        # Relational data models and operations\n",
        "│   │   │   ├── models.py\n",
        "│   │   │   └── operations.py\n",
        "│   │   └── vector_db/       # Vector storage and similarity search (pgvector)\n",
        "│   │       ├── vector_store.py\n",
        "│   │       └── operations.py\n",
        "│   └── integrations/        # External service connectors\n",
        "│       ├── gmail/           # Gmail API integration\n",
        "│       │   ├── gmail_service.py\n",
        "│       │   └── gmail_utils.py\n",
        "│       └── whatsapp/        # WhatsApp Business API integration\n",
        "│           ├── whatsapp_service.py\n",
        "│           └── whatsapp_utils.py\n",
        "├── docs/\n",
        "│   ├── decisions/               # Architecture Decision Records\n",
        "│   │   ├── ADR-001-vector-storage.md\n",
        "│   │   ├── ADR-002-local-llm.md\n",
        "│   │   ├── ADR-003-framework.md\n",
        "│   │   ├── ADR-004-evaluation-strategy.md\n",
        "│   │   ├── ADR-005-ollama-langchain.md\n",
        "│   │   ├── ADR-006-langfuse-tracing.md\n",
        "│   │   └── ADR-007-langgraph-agent.md\n",
        "│   ├── fdd.md\n",
        "│   ├── hld.md\n",
        "│   └── PROGRESS.md\n",
        "├── postgres/\n",
        "│   └── schema.sql\n",
        "├── example.env\n",
        "├── docker-compose.yml\n",
        "├── README.md\n",
        "├── CLAUDE.md\n",
        "└── .gitignore\n",
        "```\n"
    ]

    # Replace the lines
    new_lines = lines[:code_start] + new_code_block + lines[code_end+1:]

    # Write back
    with open('/home/gilson/Workflow/Repositories/ai-automation-platform/README.md', 'w') as f:
        f.writelines(new_lines)

if __name__ == '__main__':
    main()