# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import chatbot_api, whatshapp, rag_api
app = FastAPI(title="ChatBot ASN API", version="1.0.0")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


print("test")
app.include_router(chatbot_api.router, prefix="/api/v1")
app.include_router(whatshapp.router, prefix="/api/v1")
app.include_router(rag_api.router, prefix="/api/v1")