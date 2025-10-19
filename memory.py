from langchain_community.chat_message_histories import RedisChatMessageHistory

from config import REDIS_URL


def get_session_history(session_id: str) -> RedisChatMessageHistory:
    """Retorna uma instância de RedisChatMessageHistory para o session_id dado.

    Args:
        session_id: identificador da sessão/histórico

    Returns:
        RedisChatMessageHistory: objeto que gerencia o histórico no Redis
    """
    return RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL,
    )
