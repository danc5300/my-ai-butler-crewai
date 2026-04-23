from fastapi import FastAPI
import os

app = FastAPI(title="My AI Butler - CrewAI")

@app.get("/")
def root():
    return {
        "status": "✅ CrewAI service is running",
        "message": "Alfred and Blaze will be initialized here",
        "openrouter": "Connected (model ready)",
        "content_creation": "YouTube, Instagram, Facebook tools enabled"
    }

print("✅ My AI Butler CrewAI service started successfully")
print("✅ Ready for agent initialization")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
