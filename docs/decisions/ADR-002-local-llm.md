# ADR-002: Local LLM Selection

## Status
Accepted

## Context
The AI Automation Platform requires a Large Language Model (LLM) for natural language understanding, generation, and reasoning capabilities. The system needs to:
- Process user queries and generate contextual responses
- Understand and execute user commands (like sending messages)
- Operate in alignment with the local-first privacy principle
- Function on consumer-grade hardware
- Provide reasonable response times for interactive use

Options considered:
- Cloud LLM APIs (OpenAI GPT, Anthropic Claude, etc.)
- Local LLM inference via Ollama with various models
- Hybrid approaches (local for embeddings, cloud for generation)
- Smaller specialized models (Phi, Mistral, etc.)

## Decision
We selected Ollama running Llama 3.2 for local LLM inference.

## Consequences

### Positive
1. **Privacy Compliance**: All data processing remains on the user's machine, no data leaves local environment
2. **Cost Predictability**: No per-token or API usage costs after initial setup
3. **Offline Functionality**: System works completely offline without internet dependency
4. **Lower Latency**: No network round-trip to external APIs (beneficial for local network)
5. **Model Flexibility**: Ability to swap models (different sizes, quantizations) based on hardware
6. **No Rate Limits**: Unlimited usage without concerns about API quotas
7. **Transparent Operation**: Users can inspect and verify exactly what model is running
8. **Customization Potential**: Ability to fine-tune or adapt models locally if needed

### Negative
1. **Hardware Requirements**: Requires sufficient RAM (8GB+ recommended) and potentially GPU for optimal performance
2. **Model Capabilities**: Local models may not match the reasoning capabilities of largest cloud models
3. **Setup Complexity**: Requires users to install and configure Ollama and pull models
4. **Maintenance Responsibility**: Users manage model updates and system maintenance
5. **Quantization Trade-offs**: To fit in consumer RAM, models may need quantization affecting quality
6. **Limited Context Windows**: Local models often have smaller context windows than cloud counterparts
7. **Inference Speed**: CPU-only inference can be slow; GPU acceleration recommended for better experience

### Mitigations
- Clear hardware requirements documented (8GB RAM minimum, GPU recommended)
- Guidance on model quantization options for different hardware tiers
- Llama 3.2 selected for strong reasoning capabilities relative to size
- Ollama simplifies model management and pulling process
- Documentation includes performance expectations and optimization tips
- Fallback guidance for lower-end hardware (smaller models, aggressive quantization)