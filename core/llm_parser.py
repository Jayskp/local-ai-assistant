import requests
import json

LLAMA_SERVER_URL = "http://127.0.0.1:8080/completion"

SYSTEM_PROMPT = """
You are a strict JSON generator for a Windows assistant.

Convert the user command into JSON ONLY.

Rules:
- Output JSON only
- No explanation
- No markdown
- No comments

JSON format:
{
  "actions": [
    {
      "type": "app | file | system",
      "action": "string",
      "params": {}
    }
  ]
}

Valid actions:
open_chrome
open_vscode
organize_downloads
"""

# ===============================
# BALANCED JSON EXTRACTOR
# ===============================
def extract_json_objects(text: str):
    objects = []
    brace_stack = []
    start_idx = None

    for i, ch in enumerate(text):
        if ch == "{":
            if not brace_stack:
                start_idx = i
            brace_stack.append("{")
        elif ch == "}":
            if brace_stack:
                brace_stack.pop()
                if not brace_stack and start_idx is not None:
                    objects.append(text[start_idx:i + 1])
                    start_idx = None

    return objects


# ===============================
# MAIN PARSER
# ===============================
def parse_with_llm(user_input: str):
    print("[LLM] Sending request to llama-server...")

    prompt = SYSTEM_PROMPT + "\nUser command: " + user_input + "\nJSON:\n"

    payload = {
        "prompt": prompt,
        "temperature": 0.0,
        "n_predict": 120,
    }

    response = requests.post(
        LLAMA_SERVER_URL,
        json=payload,
        timeout=60
    )

    data = response.json()

    # Handle multiple llama-server response formats
    if "content" in data:
        text = data["content"]
    elif "response" in data:
        text = data["response"]
    elif "choices" in data:
        text = data["choices"][0]["text"]
    else:
        raise RuntimeError(f"Unknown llama-server response: {data}")

    print("[LLM] Raw output:")
    print(text)

    # ===============================
    # EXTRACT COMPLETE JSON OBJECTS
    # ===============================
    json_objects = extract_json_objects(text)

    if not json_objects:
        print("[LLM] ❌ No complete JSON object found")
        return []

    # Try parsing from LAST valid JSON (most relevant)
    for obj in reversed(json_objects):
        try:
            parsed = json.loads(obj)
            actions = parsed.get("actions", [])
            print("[LLM] ✅ Parsed actions:", actions)
            return actions
        except json.JSONDecodeError:
            continue

    print("[LLM] ❌ No valid JSON could be parsed")
    return []
