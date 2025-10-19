"""Construção dos chains RAG usados pelo bot.

Este módulo cria o retriever (Chroma) e combina com um LLM (ChatGroq) para
montar o fluxo de RAG que responde às consultas do usuário, preservando o
histórico de mensagens por sessão.
"""

from langchain_classic.chains import (
    create_history_aware_retriever,
    create_retrieval_chain,
)
from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq

from config import GROQ_MODEL_NAME, GROQ_MODEL_TEMPERATURE
from logger import logger
from memory import get_session_history
from prompts import contextualize_prompt, qa_prompt
from vectorstore import get_vectorstore


def get_rag_chain() -> object:
    """Cria e retorna o chain básico de RAG.

    O chain combina o LLM ChatGroq com um retriever (Chroma) e dois
    componentes principais: um history-aware retriever e uma cadeia de
    resposta (stuff documents).

    Returns:
        object: Chain pronto para ser usado pelo fluxo de recuperação + QA.
    """

    llm = ChatGroq(
        model=GROQ_MODEL_NAME,
        temperature=GROQ_MODEL_TEMPERATURE,
    )
    retriever = get_vectorstore().as_retriever()

    history_aware_chain = create_history_aware_retriever(
        llm, retriever, contextualize_prompt
    )
    question_answer_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=qa_prompt,
    )
    chain = create_retrieval_chain(history_aware_chain, question_answer_chain)
    logger.info("RAG chain criado com LLM={}", GROQ_MODEL_NAME)
    return chain


def get_conversational_rag_chain() -> RunnableWithMessageHistory:
    """Retorna um RunnableWithMessageHistory que envolve o chain RAG.

    Esse wrapper preserva e injeta o histórico de mensagens por sessão quando
    o chain é executado, permitindo conversas stateful por `session_id`.

    Returns:
        RunnableWithMessageHistory: runnable que gerencia histórico por sessão.
    """

    rag_chain: object = get_rag_chain()
    return RunnableWithMessageHistory(
        runnable=rag_chain,
        get_session_history=get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
