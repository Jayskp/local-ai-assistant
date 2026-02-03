import os
from dataclasses import dataclass


@dataclass
class LLMConfig:
    url: str
    temperature: float
    max_tokens: int
    timeout: float
    retries: int
    backoff_seconds: float


@dataclass
class ServerConfig:
    base_url: str
    exe_path: str
    model_path: str
    port: int


def load_llm_config() -> LLMConfig:
    return LLMConfig(
        url=os.environ.get("LLM_SERVER_URL", "http://127.0.0.1:8080/completion"),
        temperature=float(os.environ.get("LLM_TEMPERATURE", "0.1")),
        max_tokens=int(os.environ.get("LLM_MAX_TOKENS", "200")),
        timeout=float(os.environ.get("LLM_TIMEOUT", "30")),
        retries=int(os.environ.get("LLM_RETRIES", "2")),
        backoff_seconds=float(os.environ.get("LLM_BACKOFF", "1.5")),
    )


def load_server_config() -> ServerConfig:
    return ServerConfig(
        base_url=os.environ.get("LLM_SERVER_BASE", "http://127.0.0.1:8080"),
        exe_path=os.environ.get("LLM_SERVER_EXE", r"C:\\Users\\Admin\\llma.cpp\\llama-server.exe"),
        model_path=os.environ.get("LLM_MODEL_PATH", r"C:\\Users\\Admin\\llma.cpp\\models\\phi3.gguf"),
        port=int(os.environ.get("LLM_SERVER_PORT", "8080")),
    )
