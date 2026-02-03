import requests
import json
import time
from core.config import load_llm_config
from memory.logger import get_recent_history

LLM_CFG = load_llm_config()
_CACHE = {"input": None, "actions": None, "ts": 0}

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
    # simple cache for identical prompts within 2 minutes
    now = time.time()
    if _CACHE["input"] == user_input and now - _CACHE["ts"] < 120:
        return _CACHE["actions"] or []

    prompt = _build_prompt(user_input)
    payload = {
        "prompt": prompt,
        "temperature": LLM_CFG.temperature,
        "n_predict": LLM_CFG.max_tokens,
    }

    last_error = None
    for attempt in range(LLM_CFG.retries + 1):
        try:
            response = requests.post(
                LLM_CFG.url,
                json=payload,
                timeout=LLM_CFG.timeout
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            last_error = str(e)
            if attempt < LLM_CFG.retries:
                time.sleep(LLM_CFG.backoff_seconds * (attempt + 1))
                continue
            print(f"[LLM] ❌ Request failed: {last_error}")
            return []

        text = _extract_text(data)
        print("[LLM] Raw output:")
        print(text)

        json_objects = extract_json_objects(text)

        if not json_objects:
            last_error = "no JSON object found"
            continue

        for obj in reversed(json_objects):
            try:
                parsed = json.loads(obj)
                actions = _validate_actions(parsed.get("actions", []))
                print("[LLM] ✅ Parsed actions:", actions)
                _CACHE.update({"input": user_input, "actions": actions, "ts": now})
                return actions
            except json.JSONDecodeError:
                continue

        last_error = "no valid JSON parsed"

    print(f"[LLM] ❌ {last_error}")
    return []


def _build_prompt(user_input: str) -> str:
    tools = """
You can return these actions:
 - probe_system (type: tool, params: { "probe": one of ["systeminfo","cpu_mem","power_plan","storage","network_basic","ping","top_processes","startup"] })
 - apply_change (type: tool, params: { "change": one of ["flush_dns","winsock_reset","power_plan_high","power_plan_balanced","power_plan_low"], "confirm": true|false })

Rules:
- Only output JSON matching the schema.
- Do not invent actions outside this list.
- For paths, stay inside the user's home directory.
- Keep params minimal and valid.
- For actions requiring confirmation, set confirm=true only if the user clearly agreed; otherwise omit or set false.
"""

    history = get_recent_history(limit=5)
    history_lines = []
    for h in history:
        history_lines.append(f"- {h.get('timestamp')}: {h.get('command')} -> {h.get('result')}")
    history_block = "\n".join(history_lines) if history_lines else "(none)"

    return f"""
You are a strict JSON generator for a Windows assistant.
Output JSON only; no prose/markdown.

Schema:
{{
  "actions": [
    {{
    "type": "app | file | system | tool",
      "action": "string",
      "params": {{}}
    }}
  ]
}}

{tools}

Recent history:
{history_block}

User command: {user_input}
JSON:
"""


def _extract_text(data: dict) -> str:
    if "content" in data:
        return data["content"]
    if "response" in data:
        return data["response"]
    if "choices" in data:
        return data["choices"][0]["text"]
    raise RuntimeError(f"Unknown llama-server response: {data}")


def answer_with_llm(user_input: str) -> str:
    """General Q&A fallback when no structured actions are produced."""
    prompt = f"You are a concise Windows helper. Answer briefly and clearly.\nQuestion: {user_input}\nAnswer:"
    payload = {
        "prompt": prompt,
        "temperature": max(LLM_CFG.temperature, 0.4),
        "n_predict": min(LLM_CFG.max_tokens, 400),
    }

    last_error = None
    for attempt in range(LLM_CFG.retries + 1):
        try:
            response = requests.post(
                LLM_CFG.url,
                json=payload,
                timeout=LLM_CFG.timeout
            )
            response.raise_for_status()
            data = response.json()
            text = _extract_text(data).strip()
            if text:
                return text
        except Exception as e:
            last_error = str(e)
            if attempt < LLM_CFG.retries:
                time.sleep(LLM_CFG.backoff_seconds * (attempt + 1))
                continue
            break

    return last_error or "No answer available."


def _validate_actions(actions):
    if not isinstance(actions, list):
        return []

    cleaned = []
    for act in actions:
        if not isinstance(act, dict):
            continue
        action_type = act.get("type")
        action_name = act.get("action")
        params = act.get("params", {})

        if not action_type or not action_name:
            continue

        if action_name == "run_command":
            cmd = params.get("cmd") if isinstance(params, dict) else None
            if not cmd:
                continue

        if action_name == "git_clone":
            repo = params.get("repo") if isinstance(params, dict) else None
            if not repo:
                continue

        if action_name in {"optimize_performance", "apply_privacy", "fix_network", "battery_optimize", "dev_mode"}:
            if not isinstance(params, dict):
                params = {}

        if action_name in {"system_info", "network_info"}:
            params = params if isinstance(params, dict) else {}

        if action_type == "tool":
            if action_name == "probe_system":
                probe = params.get("probe") if isinstance(params, dict) else None
                if probe not in {"systeminfo", "cpu_mem", "power_plan", "storage", "network_basic", "ping", "top_processes", "startup"}:
                    continue
            elif action_name == "apply_change":
                change = params.get("change") if isinstance(params, dict) else None
                if change not in {"flush_dns", "winsock_reset", "power_plan_high", "power_plan_balanced", "power_plan_low"}:
                    continue
            else:
                continue
            params = params if isinstance(params, dict) else {}

        cleaned.append({
            "type": action_type,
            "action": action_name,
            "params": params if isinstance(params, dict) else {}
        })

    return cleaned
