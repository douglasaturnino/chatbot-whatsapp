from __future__ import annotations

import os

from loguru import logger

# Cria diretório de logs se não existir
LOG_DIR = os.path.join(os.path.dirname(__file__), "log")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_PATH = os.path.join(LOG_DIR, "app.log")

# Configuração do logger:
# - rotation: gera um novo arquivo a cada dia
# - retention: mantém logs por 30 dias
# - compression: compacta logs antigos em .zip
logger.remove()  # remove configuração padrão
logger.add(
    LOG_PATH,
    rotation="00:00",  # rotaciona à meia-noite
    retention="30 days",
    compression="zip",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
)


def get_logger() -> object:
    """Retorna o logger configurado (compatibilidade de import)."""
    return logger
