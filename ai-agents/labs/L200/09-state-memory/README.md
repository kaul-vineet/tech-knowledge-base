# 09 – State and memory

The message list is short-term state you must keep under the context window; facts that must survive go into SQLite through explicit tools.

## Run (fake server – validated)
```bash
python ../../L100/01-setup/fake_model_server.py --port 8765   # terminal 1
LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model python memory_agent.py
python -c "import sqlite3; print(sqlite3.connect('memory_demo.db').execute('SELECT * FROM notes').fetchall())"
python -m unittest -v
```
PowerShell (Windows 11):
```powershell
python ..\..\L100\01-setup\fake_model_server.py --port 8765   # terminal 1
$env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"; python memory_agent.py
python -c "import sqlite3; print(sqlite3.connect('memory_demo.db').execute('SELECT * FROM notes').fetchall())"
python -m unittest -v
```

### Expected output (observed 2026-10-28)
```
> Remember that the staging database is on port 5433.
  Final answer: save_memory(note=the staging database is on port 5433) = saved note 1
  tokens=34 summaries=0
> Thanks. Now tell me a fun fact about otters.
  Hello from fake-model! You said: 'Thanks. Now tell me a fun fact about otters.'
  tokens=57 summaries=0
> And one about penguins please, keep it short.
  Hello from fake-model! You said: 'And one about penguins please, keep it short.'
  tokens=62 summaries=1
system now: Earlier: Summary: Remember that the staging database is on port; Thanks. Now tell me a fun fact about
> What do you remember about staging?
  Final answer: recall_memory(query=staging) = 1: the staging database is on port 5433
```
Tests: `Ran 8 tests ... OK`.

## Build task
Cap long-term memory at max_notes=3: saving a 4th note deletes the oldest.

Hints:
- Subclass MemoryStore and override save().
- DELETE FROM notes WHERE id NOT IN (SELECT id ... ORDER BY id DESC LIMIT ?)
- Use a placeholder for the limit too.

Solution: `solution/capped_memory.py` · proof: `python -m unittest -v test_build_task`

## Equivalents
- MemGPT / Letta: the model manages tiered memory through tools (paper: MemGPT, Packer et al.)
- LangGraph checkpointers persist conversation state per thread (SQLite or Postgres)
- llama.cpp: -c/--ctx-size sets the window, --context-shift trims old tokens on long generations

## Optional steps (not run in the sandbox)
**real model with a bigger window** – Raise Ollama's context window, then run with the defaults; raise Chat(budget=...) to match, minus room for the reply.
```bash
OLLAMA_CONTEXT_LENGTH=8192 ollama serve      # or: launchctl setenv OLLAMA_CONTEXT_LENGTH 8192, then restart the app
python memory_agent.py
```
```powershell
# quit Ollama from the taskbar first
$env:OLLAMA_CONTEXT_LENGTH="8192"; ollama serve
python memory_agent.py   # second PowerShell window
```
Expected: Same flow; real summaries are model-worded and token counts differ from word counts

## Troubleshooting
| Symptom | Action |
|---|---|
| Answers ignore early facts | They were summarised away; store must-keep facts with save_memory or raise the budget. |
| database is locked / file in use (Windows) | Close every connection (memory.close()) before deleting or reopening the file. |
| Budget never triggers on a real model | Words underestimate tokens; calibrate with usage.prompt_tokens. |

## Try it (validated, observed 2026-10-28)
Predict first, then run `python -m unittest -v test_try_it_09` (each test makes the change and prints what it observed).

| Change | Observed |
|---|---|
| Create Chat(budget=500) instead of 60 and send the same three turns. | summaries = 0 / messages = 9 / tokens = 78 - nothing summarised; the list just keeps growing. |
| Use MemoryStore() (in-memory) for both conversations instead of memory_demo.db. | Final answer: recall_memory(query=staging) = no matching notes - memory lives in the file, not in the model. |
