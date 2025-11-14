from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.llm_service import ask_llm, stream_llm

app = FastAPI()

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type"],
)

class Message(BaseModel):
    message: str

@app.get("/api/stream")
async def stream_get(prompt: str):
    event_generator = stream_llm(prompt)
    return StreamingResponse(event_generator, media_type="text/event-stream")


@app.post("/api/chat")
async def chat_endpoint(msg: Message):
    response_text = await ask_llm(msg.message)
    return {"reply": response_text}


@app.get("/api/test")
def test():
    return {"message": "Backend работает!"}
