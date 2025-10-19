"""Templates de prompt usados para contextualização e QA.

Este módulo define dois ChatPromptTemplate: um para contextualizar a
pergunta com o histórico e outro para a etapa de QA (resposta usando
o conteúdo recuperado).
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from config import AI_CONTEXTUALIZE_PROMPT, AI_SYSTEM_PROMPT

contextualize_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
    [
        ("system", AI_CONTEXTUALIZE_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

qa_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
    [
        ("system", AI_SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
