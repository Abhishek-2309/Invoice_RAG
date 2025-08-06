import unsloth
from fastapi import FastAPI
from app.routes import router
from app.models.vl_model import load_model

app = FastAPI()

@app.on_event("startup")
def startup_event():
    print("Loading Qwen LLM...")
    load_model()
    print("Qwen model loaded successfully.")

app.include_router(router)
@app.get("/")
def root():
    return {"status": "FastAPI is running!"}