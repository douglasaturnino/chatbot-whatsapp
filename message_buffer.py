"""Módulo para fazer o buffer de mensagens recebidas via WhatsApp usando Redis com debounce."""

import asyncio
from collections import defaultdict

import redis.asyncio as redis

from chains import get_conversational_rag_chain
from config import BUFFER_KEY_SUFFIX, BUFFER_TTL, DEBOUNCE_SECONDS, REDIS_URL
from evolution_api import send_whatsapp_message
from logger import logger

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
conversational_rag_chain = get_conversational_rag_chain()

debounce_tasks = defaultdict(asyncio.Task)


async def buffer_message(chat_id: str, message: str) -> None:
    """Armazena mensagens em buffer no Redis com debounce.

    Args:
        chat_id (str): ID do chat (remoteJid).
        message (str): Mensagem recebida.
    """

    buffer_key = f"{chat_id}{BUFFER_KEY_SUFFIX}"

    await redis_client.rpush(buffer_key, message)
    await redis_client.expire(buffer_key, int(BUFFER_TTL))

    logger.info("Mensagem adicionada ao buffer para o chat_id {}.", chat_id)

    if debounce_tasks.get(chat_id):
        debounce_tasks[chat_id].cancel()
        logger.info("Debounce resetado para o chat_id {}.", chat_id)

    debounce_tasks[chat_id] = asyncio.create_task(handle_buffered(chat_id))


async def handle_buffered(chat_id: str) -> None:
    """Processa mensagens em buffer após o período de debounce.

    Args:
        chat_id (str): ID do chat (remoteJid).
    """

    try:
        logger.info("Iniciando debounce para o chat_id {}.", chat_id)
        await asyncio.sleep(float(DEBOUNCE_SECONDS))

        buffer_key = f"{chat_id}{BUFFER_KEY_SUFFIX}"
        messages = await redis_client.lrange(buffer_key, 0, -1)

        full_message = " ".join(messages).strip()

        if full_message:
            logger.info(
                "Enviando mensagem agrupada para o chat_id {}: {}.",
                chat_id,
                full_message,
            )

            ai_response: str = conversational_rag_chain.invoke(
                input={"input": full_message},
                config={"configurable": {"session_id": chat_id}},
            )["answer"]

            send_whatsapp_message(
                number=chat_id,
                text=ai_response,
            )
            logger.info("Resposta enviada para {}", chat_id)

        await redis_client.delete(buffer_key)

    except asyncio.CancelledError:
        logger.info("Debounce cancelado para o chat_id {}.", chat_id)
