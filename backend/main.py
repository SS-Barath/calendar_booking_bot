from fastapi import FastAPI
from pydantic import BaseModel
from backend.langgraph_agent import handle_booking

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    reply = handle_booking(request.message)
    return {"response": reply}
