# API

OpenAPI is available at:

```text
http://127.0.0.1:8000/docs
```

Core memory endpoints:

- `GET /memory/query?q=<text>`
- `GET /memory/recent`
- `POST /memory/write`

Developer endpoints require:

```text
Authorization: Bearer dev-admin-token
```

The chat response format avoids exposing chain-of-thought. Debug data is returned as `developer_trace`.

```json
{
  "message_id": "string",
  "conversation_id": "string",
  "spoken_words": "string",
  "developer_trace": {
    "retrieved_memories": [],
    "emotion_state": {},
    "memory_write_decision": "written",
    "prompt_summary": "L1 messages=2, retrieved_memories=1"
  }
}
```

## Model Gateway

Default mode is offline mock:

```text
AETHER_MODEL_PROVIDER=mock
```

To use an OpenAI-compatible chat-completions provider:

```text
AETHER_MODEL_PROVIDER=openai_compatible
AETHER_MODEL_BASE_URL=https://api.openai.com/v1
AETHER_MODEL_NAME=gpt-4.1-mini
AETHER_MODEL_API_KEY=...
```
