import os
import ollama

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _safe_path(filename: str) -> str:
    """Restrict all file ops to output/ directory."""
    basename = os.path.basename(filename)
    if not basename:
        basename = "untitled.txt"
    return os.path.join(OUTPUT_DIR, basename)


def create_file(params: dict) -> tuple[str, str]:
    """Create a new text file in output/."""
    filename = params.get("filename", "new_file.txt")
    content = params.get("content", "")
    path = _safe_path(filename)

    with open(path, "w") as f:
        f.write(content)

    return f"✅ File created: `{path}`", path


def write_code(params: dict) -> tuple[str, str]:
    """Generate code via LLM and save to output/."""
    filename = params.get("filename", "script.py")
    language = params.get("language", "python")
    description = params.get("description", params.get("message", "a basic script"))

    prompt = (
        f"Write clean {language} code for the following task:\n{description}\n\n"
        f"Return ONLY the code. No explanation. No markdown fences."
    )

    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )
    code = response['message']['content'].strip()

    # Strip fences if model adds them
    if code.startswith("```"):
        code = "\n".join(code.split("\n")[1:])
    if code.endswith("```"):
        code = "\n".join(code.split("\n")[:-1])

    path = _safe_path(filename)
    with open(path, "w") as f:
        f.write(code)

    return f"✅ Code saved to `{path}`\n\n```{language}\n{code}\n```", path


def summarize_text(params: dict) -> tuple[str, None]:
    """Summarize provided content."""
    content = params.get("content", params.get("message", ""))

    if not content:
        return "⚠️ No content to summarize. Please provide text.", None

    response = ollama.chat(
        model="llama3.2",
        messages=[{
            "role": "user",
            "content": f"Summarize the following text concisely:\n\n{content}"
        }]
    )
    summary = response['message']['content'].strip()
    return summary, None


def general_chat(params: dict) -> tuple[str, None]:
    """Handle general conversation."""
    message = params.get("message", "")

    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": message}]
    )
    return response['message']['content'].strip(), None


def execute_tool(intent_result: dict) -> tuple[str, any]:
    """Route intent to the correct tool."""
    intent = intent_result.get("intent", "chat")
    params = intent_result.get("parameters", {})

    if intent == "create_file":
        return create_file(params)
    elif intent == "write_code":
        return write_code(params)
    elif intent == "summarize":
        return summarize_text(params)
    else:
        return general_chat(params)