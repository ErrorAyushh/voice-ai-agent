import ollama
import json
import re

SYSTEM_PROMPT = """You are an intent classifier for a voice-controlled AI agent.

Analyze the user's text and return ONLY a valid JSON object — no explanation, no markdown, no extra text.

JSON format:
{
  "intent": "<one of: create_file, write_code, summarize, chat>",
  "parameters": {
    "filename": "<if applicable, else null>",
    "language": "<if code: python/javascript/etc, else null>",
    "description": "<what to code or write>",
    "content": "<text to summarize if applicable, else null>",
    "message": "<user message for chat, else null>"
  }
}

Rules — follow strictly:
- If user says "create/write/make a python/javascript/any code file" → intent = write_code
- If user says "create/make a text file / empty file / folder" → intent = create_file  
- If user says "summarize / give summary of" → intent = summarize
- Everything else → intent = chat

Examples:
Input: "Create a Python file with bubble sort function"
Output: {"intent":"write_code","parameters":{"filename":"bubble_sort.py","language":"python","description":"bubble sort function","content":null,"message":null}}

Input: "Create a text file called notes.txt"
Output: {"intent":"create_file","parameters":{"filename":"notes.txt","language":null,"description":null,"content":null,"message":null}}

Input: "Summarize this: AI is changing the world"
Output: {"intent":"summarize","parameters":{"filename":null,"language":null,"description":null,"content":"AI is changing the world","message":null}}

Input: "What is machine learning"
Output: {"intent":"chat","parameters":{"filename":null,"language":null,"description":null,"content":null,"message":"What is machine learning"}}
"""

def classify_intent(text: str) -> dict:
    """Use local LLM to classify intent from transcribed text."""
    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ]
        )
        raw = response['message']['content'].strip()

        # Strip markdown code fences if model adds them
        raw = re.sub(r"```(?:json)?", "", raw).strip().strip("```").strip()

        return json.loads(raw)

    except json.JSONDecodeError:
        # Graceful fallback
        return {
            "intent": "chat",
            "parameters": {"message": text}
        }
    except Exception as e:
        return {
            "intent": "error",
            "parameters": {"message": str(e)}
        }