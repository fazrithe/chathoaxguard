from langchain.llms import HuggingFaceHub
from dotenv import load_dotenv
import os

load_dotenv()

HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

if not HUGGINGFACEHUB_API_TOKEN:
    raise ValueError("HUGGINGFACEHUB_API_TOKEN tidak ditemukan di .env")

llm = HuggingFaceHub(
    repo_id="google/flan-t5-base",  # Bisa diganti ke model lain
    huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
    task="text2text-generation",  # WAJIB sesuai jenis model
    model_kwargs={"temperature": 0.5, "max_length": 512},
)
