"""Aplicação FastAPI que expõe o endpoint de webhook usado pela EvolutionAPI.

Este módulo inicializa a cadeia conversacional RAG e trata eventos de webhook
recebidos. Extrai os campos relevantes da mensagem, envia a entrada ao fluxo
RAG para gerar a resposta e encaminha a resposta de volta via EvolutionAPI.
"""

from typing import Dict, Optional

from fastapi import FastAPI, Request

from chains import get_conversational_rag_chain
from evolution_api import send_whatsapp_message
from logger import logger

app = FastAPI()

conversational_rag_chain = get_conversational_rag_chain()
logger.info("Convesational RAG chain inicializado")


@app.post("/webhook")
async def webhook(request: Request) -> Dict[str, object]:
    """Recebe e processa eventos de webhook enviados pela EvolutionAPI.

    Args:
        request (fastapi.Request): requisição contendo o JSON do webhook.

    Comportamento:
        - Extrai de forma defensiva os campos `remoteJid`, `fromMe`,
          `conversation` e `pushName` do payload.
        - Registra em log apenas os campos solicitados (remoteJid, pushName,
          conversation).
        - Quando aplicável, envia o texto ao chain RAG e encaminha a
          resposta via EvolutionAPI.

    Returns:
        dict: {"status": "ok"} indicando que o webhook foi processado.
    """

    data: Dict[str, object] = await request.json()
    # estrutura esperada do webhook: data.data.key.remoteJid, data.data.key.fromMe, data.data.message.conversation
    chat_id: Optional[str] = data.get("data").get("key").get("remoteJid")
    from_me: Optional[bool] = data.get("data").get("key").get("fromMe")
    message: Optional[str] = (
        data.get("data").get("message").get("conversation")
    )
    push_name: Optional[str] = data.get("data").get("pushName")

    logger.info(
        "Webhook recebido - remoteJid={}, pushName={}, conversation={}",
        chat_id,
        push_name,
        message,
    )

    if chat_id and message and from_me and "@g.us" not in chat_id:
        ai_response: str = conversational_rag_chain.invoke(
            input={"input": message},
            config={"configurable": {"session_id": chat_id}},
        )["answer"]
        send_whatsapp_message(
            number=chat_id,
            text=ai_response,
        )
        logger.info("Resposta enviada para {}", chat_id)

    return {"status": "ok"}
