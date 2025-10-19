from typing import Optional

import requests

from config import (
    EVOLUTION_API_URL,
    EVOLUTION_AUTHENTICATION_API_KEY,
    EVOLUTION_INSTANCE_NAME,
)
from logger import logger


def send_whatsapp_message(number: str, text: str) -> None:
    """Envia uma mensagem de texto para um número/ID via EvolutionAPI.

    Args:
        number: número ou remoteJid (ex: '5511999999999@c.us' ou id de chat)
        text: texto da mensagem a ser enviada
    """
    url: Optional[str] = (
        f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE_NAME}"
        if EVOLUTION_API_URL and EVOLUTION_INSTANCE_NAME
        else None
    )
    if not url:
        logger.error(
            "EVOLUTION_API_URL ou EVOLUTION_INSTANCE_NAME não configurados"
        )
        return

    headers = {
        "apikey": EVOLUTION_AUTHENTICATION_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {"number": number, "text": text}
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        logger.exception("Erro ao enviar mensagem via EvolutionAPI: %s", e)
