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
        logger.info(
            "Resposta enviada para {}, Resposta {}", chat_id, ai_response
        )

    return {"status": "ok"}
