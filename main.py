from fastapi import FastAPI
import os

app = FastAPI(title="My AI Butler")

@app.get("/")
def root():
    return {
        "status": "✅ Server is LIVE and running",
        "message": "Minimal version - no LLM yet"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

print("✅ Minimal server started successfully")
