import os
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from .config import require
from .loader import load_markdown

EMBED_DIMENSION = 1024  # Cohere multilingual v3

def embedding():
    return CohereEmbedding(api_key=require("COHERE_API_KEY"), model_name=os.getenv("COHERE_EMBED_MODEL", "embed-multilingual-v3.0"), input_type="search_document")

def vector_store():
    client = Pinecone(api_key=require("PINECONE_API_KEY"))
    name = os.getenv("PINECONE_INDEX_NAME", "agentic-knowledge")
    if name not in client.list_indexes().names():
        client.create_index(name=name, dimension=EMBED_DIMENSION, metric="cosine", spec=ServerlessSpec(cloud="aws", region="us-east-1"))
    return PineconeVectorStore(pinecone_index=client.Index(name), namespace=os.getenv("PINECONE_NAMESPACE", "project-docs"))

def build_index(root):
    documents = load_markdown(root)
    if not documents:
        raise ValueError("No markdown files found in supported tool folders")
    nodes = SentenceSplitter(chunk_size=500, chunk_overlap=40).get_nodes_from_documents(documents)
    index = VectorStoreIndex(nodes, storage_context=StorageContext.from_defaults(vector_store=vector_store()), embed_model=embedding(), show_progress=True)
    return index, len(documents), len(nodes)

def existing_index():
    return VectorStoreIndex.from_vector_store(vector_store(), embed_model=embedding())
