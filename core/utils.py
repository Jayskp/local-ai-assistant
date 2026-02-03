def summarize_output(stdout: str, stderr: str, max_chars: int = 500) -> str:
    combined = (stdout or "") + ("\n" + stderr if stderr else "")
    combined = combined.strip()
    if not combined:
        return "(no output)"
    if len(combined) > max_chars:
        return combined[:max_chars].rstrip() + " …"
    return combined
