import os
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.services.gemini_client import ask_gemini_api  # fungsi kamu

PDF_FOLDER = "data/pdf"
FAISS_INDEX_DIR = "data/vector_index"

def train_pdf_to_faiss():
    docs = []
    for filename in os.listdir(PDF_FOLDER):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(PDF_FOLDER, filename))
            docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(texts, embeddings)

    os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
    vectorstore.save_local(FAISS_INDEX_DIR)

def answer_question_with_rag(query: str) -> str:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    if not os.path.exists(FAISS_INDEX_DIR):
        train_pdf_to_faiss()

    db = FAISS.load_local(FAISS_INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever()
    
    docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
Berikut adalah konteks dokumen:

{context}

Berdasarkan konteks di atas, jawablah pertanyaan berikut secara akurat dan jelas:
Pertanyaan: {query}
"""

    response = ask_gemini_api(prompt)
    return response
