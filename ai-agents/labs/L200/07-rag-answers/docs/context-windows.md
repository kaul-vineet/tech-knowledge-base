# Context windows

The context window is the maximum number of tokens a model can read in one request, counting the system prompt, the history and the new message. Ollama uses a 4096-token context window by default and the OLLAMA_CONTEXT_LENGTH variable changes it.

When a conversation grows past the window, the client must drop or summarise older turns. Servers may silently truncate the oldest tokens, so the client should count tokens itself.
