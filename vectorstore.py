import os
import shutil
from typing import List, Protocol

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import RAG_FILES_DIR, VECTOR_STORE_PATH
from logger import logger

embedding = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")


class DocumentProtocol(Protocol):
    page_content: str
    metadata: dict


def load_documents() -> List[DocumentProtocol]:
    docs: List[DocumentProtocol] = []

    processed_dir: str = os.path.join(RAG_FILES_DIR, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    files = [
        os.path.join(RAG_FILES_DIR, f)
        for f in os.listdir(RAG_FILES_DIR)
        if f.endswith((".pdf") or f.endswith(".txt"))
    ]
    logger.info("Arquivos para vetorização encontrados: {}", files)

    for file in files:
        loader = (
            PyPDFLoader(file) if file.endswith(".pdf") else TextLoader(file)
        )
        docs.extend(loader.load())
        dest_path: str = os.path.join(processed_dir, os.path.basename(file))
        shutil.move(file, dest_path)

    return docs


def get_vectorstore() -> Chroma:
    docs: List[DocumentProtocol] = load_documents()
    logger.info("Número de documentos carregados: {}", len(docs))
    if docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

        splits = text_splitter.split_documents(docs)
        chroma = Chroma.from_documents(
            documents=splits,
            embedding=embedding,
            persist_directory=VECTOR_STORE_PATH,
        )
        logger.info("Chroma persistido em {}", VECTOR_STORE_PATH)
        return chroma

    logger.info("Inicializando Chroma vazio em {}", VECTOR_STORE_PATH)
    return Chroma(
        embedding_function=embedding,
        persist_directory=VECTOR_STORE_PATH,
    )
