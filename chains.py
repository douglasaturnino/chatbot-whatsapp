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
    rag_chain: object = get_rag_chain()
    return RunnableWithMessageHistory(
        runnable=rag_chain,
        get_session_history=get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
