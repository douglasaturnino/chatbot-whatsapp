"""Carrega e expõe as variáveis de ambiente usadas pelo projeto.

As variáveis são carregadas via python-dotenv (`.env`) e exportadas como
variáveis de módulo para uso em outros pontos do código.
"""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME: Optional[str] = os.getenv("GROQ_MODEL_NAME")
GROQ_MODEL_TEMPERATURE: Optional[int] = os.getenv("GROQ_MODEL_TEMPERATURE")

AI_CONTEXTUALIZE_PROMPT: Optional[str] = os.getenv("AI_CONTEXTUALIZE_PROMPT")
AI_SYSTEM_PROMPT: Optional[str] = os.getenv("AI_SYSTEM_PROMPT")

VECTOR_STORE_PATH: Optional[str] = os.getenv("VECTOR_STORE_PATH")
RAG_FILES_DIR: Optional[str] = os.getenv("RAG_FILES_DIR")

EVOLUTION_API_URL: Optional[str] = os.getenv("EVOLUTION_API_URL")
EVOLUTION_INSTANCE_NAME: Optional[str] = os.getenv("EVOLUTION_INSTANCE_NAME")
EVOLUTION_AUTHENTICATION_API_KEY: Optional[str] = os.getenv(
    "AUTHENTICATION_API_KEY"
)

REDIS_URL: Optional[str] = os.getenv("CACHE_REDIS_URI")

BUFFER_KEY_SUFFIX: str = os.getenv("BUFFER_KEY_SUFFIX")
DEBOUNCE_SECONDS: str = os.getenv("DEBOUNCE_SECONDS")
BUFFER_TTL: str = os.getenv("BUFFER_TTL")
