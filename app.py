from fastapi import FastAPI, Request
from loguru import logger as logging

from evolution_api import send_whatsapp_message

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    chat_id = data.get("data").get("key").get("remoteJid")
    from_me = data.get("data").get("key").get("fromMe")
    message = data.get("data").get("message").get("conversation")

    if chat_id and message and from_me and "@g.us" not in chat_id:
        send_whatsapp_message(
            number=chat_id,
            text="Oi, fala ai mano",
        )

    return {"status": "ok"}
