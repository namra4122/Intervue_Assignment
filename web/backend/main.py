import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List
import google.genai.types as types
from utils.json_loader import load_flow_from_json
from services.llm_service import LLMService
from services.flow_service import FlowService

class ChatService:
    def __init__(self, username: str):
        self.username = username
        self.nodes = self._load_flow()
        self.llm_service = LLMService(self.username)
        self.flow_service = FlowService(self.nodes, self.llm_service)
    
    def _load_flow(self):
        basedir = os.path.dirname(os.path.abspath(__file__))
        flow_dir = os.path.join(basedir, 'config', 'interview_flow.json')
        return load_flow_from_json(flow_dir)
    
    def init_response(self):
        if self.flow_service.current_node:
            initial_response_chunks = self.llm_service.generate_response(self.flow_service.current_node.prompt)
            initial_response = ""
            for chunk in initial_response_chunks:
                initial_response = initial_response + chunk.text if chunk.text else ""
            self.flow_service.chat_history.append(
                types.Content(role="model", parts=[types.Part.from_text(text=initial_response),],)
            )
            return initial_response
        return "Failed to initialize chat"

chat_sessions: Dict[str, ChatService] = {}
question_counts: Dict[str, int] = {}

class InitRequest(BaseModel):
    username: str
    session_id: Optional[str] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ResetRequest(BaseModel):
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    current_node: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Intervue Assignment"}

def get_chat_service(session_id: str):
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return chat_sessions[session_id]

@app.post("/api/init", response_model=ChatResponse)
async def chat_init(request: InitRequest):
    session_id = request.session_id or os.urandom(16).hex()
    
    chat_service = ChatService(request.username)
    chat_sessions[session_id] = chat_service
    question_counts[session_id] = 0
    
    initial_response = chat_service.init_response()
    
    return {
        "response": initial_response,
        "session_id": session_id,
        "current_node": chat_service.flow_service.current_node.node_id
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_response(request: ChatRequest):
    chat_service = get_chat_service(request.session_id)
    
    question_counts[request.session_id] = question_counts.get(request.session_id, 0) + 1
    q_count = question_counts[request.session_id]
    
    response = chat_service.flow_service.process_user_input(
        user_input=request.message,
        username=chat_service.username,
        q_count=q_count
    )
    
    return {
        "response": response,
        "session_id": request.session_id,
        "current_node": chat_service.flow_service.current_node.node_id
    }

@app.post("/api/reset", response_model=ChatResponse)
async def reset_chat(request: ResetRequest):
    chat_service = get_chat_service(request.session_id)
    
    chat_service.flow_service.reset()
    question_counts[request.session_id] = 0
    
    initial_response = chat_service.init_response()
    
    return {
        "response": initial_response,
        "session_id": request.session_id,
        "current_node": chat_service.flow_service.current_node.node_id
    }

@app.get("/api/sessions/{session_id}/history")
async def get_chat_history(session_id: str):
    chat_service = get_chat_service(session_id)
    
    formatted_history = []
    for content in chat_service.flow_service.chat_history:
        if content.role and content.parts and len(content.parts) > 0:
            formatted_history.append({
                "role": content.role,
                "content": content.parts[0].text if content.parts[0].text else ""
            })
    
    return {
        "history": formatted_history,
        "current_node": chat_service.flow_service.current_node.node_id
    }