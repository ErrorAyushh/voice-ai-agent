# Voice-Controlled Local AI Agent

A local AI agent that takes voice input, figures out what you're asking for, and actually does it — creates files, writes code, summarizes text, or just chats. Everything runs on your machine. Nothing goes to any external server.

Built for the Mem0 AI/ML & Generative AI Developer Intern Assignment.

---

## Demo

[Watch on YouTube](#) ← replace with your link

---

## What it does

You speak (or type), and the agent detects your intent and executes the right action.

| Command | What happens |
|---|---|
| "Create a Python file with bubble sort" | Generates the code and saves it locally |
| "Create a text file called notes.txt with meeting at 5pm" | Creates that exact file |
| "Summarize this: AI is transforming industries..." | Returns a concise summary |
| "What is machine learning?" | Answers conversationally |
| "Summarize this and save it to summary.txt" | Runs both actions in sequence |

---

## How it works
Voice input (mic or uploaded file)
↓
Speech-to-Text using faster-whisper (runs locally on CPU)
↓
Intent detection using Ollama + llama3.2 (local LLM)
↓
Tool execution based on detected intent
↓
Result displayed in Streamlit UI

---

## Features

**Core**
- Record directly from mic or upload an audio file
- Local speech-to-text, no API calls
- Intent classification with a local LLM
- Executes 4 types of actions: write code, create file, summarize, chat

**Bonus features implemented**
- Compound commands — one sentence, multiple actions
- Human-in-the-loop — asks for confirmation before any file operation
- Graceful degradation — handles bad audio and unrecognized intents without crashing
- Session memory — keeps track of everything you did during the session

---

## Tech stack

| Component | Tool |
|---|---|
| UI | Streamlit |
| Speech-to-Text | faster-whisper (base, int8, CPU) |
| Intent + LLM | Ollama with llama3.2 |
| Audio recording | sounddevice + scipy |
| Language | Python 3.10+ |

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/ErrorAyushh/voice-ai-agent.git
cd voice-ai-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama and pull the model

Download from [ollama.com](https://ollama.com), then:

```bash
ollama pull llama3.2
ollama serve
```

### 5. Run

```bash
streamlit run app.py
```

Go to `http://localhost:8501`

---

## Project structure
voice-agent/
├── app.py          # UI and main pipeline
├── stt.py          # Speech-to-text module
├── intent.py       # Intent classification
├── tools.py        # Tool execution
├── requirements.txt
└── output/         # All generated files land here

---

## Hardware notes

I'm running this on a CPU-only machine. Whisper via HuggingFace transformers was taking 30-40 seconds per clip which was unusable. Switched to faster-whisper with the base model in int8 quantized mode — brings it down to 3-6 seconds with the same accuracy. Ollama with llama3.2 runs fine on 8GB RAM, intent classification takes about 2-4 seconds.

---

## Model comparison

| Model | Size | Avg time on CPU | Accuracy |
|---|---|---|---|
| whisper tiny | 75MB | 1-2s | Mediocre |
| whisper base | 150MB | 3-6s | Good, chosen for this project |
| whisper small | 500MB | 8-15s | Better but too slow for real-time |

---

## Safety

All file operations are restricted to the output/ folder. The agent cannot touch anything outside it. File operations also require manual confirmation through the UI before they run.

---

## What I'd add with more time

- More intents like opening a browser, searching the web, sending emails
- Persistent memory across sessions using a local vector store
- Wake word detection so it runs passively in the background
