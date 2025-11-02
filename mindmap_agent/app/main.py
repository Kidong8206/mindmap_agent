from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from anthropic import Anthropic

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for chat sessions
chat_sessions = {}

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

class MindmapRequest(BaseModel):
    session_id: str

# Initialize Anthropic client
anthropic_client = None
try:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        anthropic_client = Anthropic(api_key=api_key)
except Exception as e:
    print(f"Warning: Could not initialize Anthropic client: {e}")

@app.get("/")
def read_root():
    return {"msg": "Mindmap Agent API is running"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat messages and return AI responses
    """
    session_id = request.session_id
    user_message = request.message

    # Initialize session if it doesn't exist
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    # Add user message to session
    chat_sessions[session_id].append({
        "role": "user",
        "content": user_message
    })

    # Generate AI response
    if anthropic_client:
        try:
            response = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=chat_sessions[session_id]
            )
            ai_response = response.content[0].text
        except Exception as e:
            ai_response = f"I'm a demo AI response. (API Error: {str(e)})"
    else:
        ai_response = "I'm a demo AI response. To get real AI responses, set the ANTHROPIC_API_KEY environment variable."

    # Add AI response to session
    chat_sessions[session_id].append({
        "role": "assistant",
        "content": ai_response
    })

    return ChatResponse(response=ai_response, session_id=session_id)

@app.get("/api/chat/{session_id}")
async def get_chat_history(session_id: str):
    """
    Get chat history for a session
    """
    if session_id not in chat_sessions:
        return {"messages": []}
    return {"messages": chat_sessions[session_id]}

@app.post("/api/mindmap")
async def generate_mindmap(request: MindmapRequest):
    """
    Generate a mindmap from chat history
    """
    session_id = request.session_id

    if session_id not in chat_sessions or len(chat_sessions[session_id]) == 0:
        raise HTTPException(status_code=404, detail="No chat history found for this session")

    messages = chat_sessions[session_id]

    # Use Claude to analyze the conversation and create a mindmap structure
    if anthropic_client:
        try:
            mindmap_prompt = """Analyze the following conversation and create a structured mindmap in JSON format.
The mindmap should have a hierarchical structure with a central topic and related subtopics.

Return ONLY a JSON object with this structure:
{
    "name": "Central Topic",
    "children": [
        {
            "name": "Subtopic 1",
            "children": [
                {"name": "Detail 1"},
                {"name": "Detail 2"}
            ]
        },
        {
            "name": "Subtopic 2",
            "children": [...]
        }
    ]
}

Conversation:
"""
            for msg in messages:
                mindmap_prompt += f"\n{msg['role'].upper()}: {msg['content']}"

            response = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[{"role": "user", "content": mindmap_prompt}]
            )

            mindmap_json = response.content[0].text
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in mindmap_json:
                mindmap_json = mindmap_json.split("```json")[1].split("```")[0].strip()
            elif "```" in mindmap_json:
                mindmap_json = mindmap_json.split("```")[1].split("```")[0].strip()

            import json
            mindmap_data = json.loads(mindmap_json)
            return {"mindmap": mindmap_data}

        except Exception as e:
            print(f"Error generating mindmap with AI: {e}")
            # Fallback to simple structure
            pass

    # Fallback: Create a simple mindmap structure
    topics = []
    for i in range(0, len(messages), 2):
        if i < len(messages):
            user_msg = messages[i]['content'][:50] + "..." if len(messages[i]['content']) > 50 else messages[i]['content']
            topic = {"name": f"Q{i//2 + 1}: {user_msg}", "children": []}

            if i + 1 < len(messages):
                ai_msg = messages[i + 1]['content'][:50] + "..." if len(messages[i + 1]['content']) > 50 else messages[i + 1]['content']
                topic["children"].append({"name": f"A: {ai_msg}"})

            topics.append(topic)

    mindmap_data = {
        "name": "Chat Conversation",
        "children": topics
    }

    return {"mindmap": mindmap_data}

@app.delete("/api/chat/{session_id}")
async def clear_chat(session_id: str):
    """
    Clear chat history for a session
    """
    if session_id in chat_sessions:
        chat_sessions[session_id] = []
    return {"status": "cleared"}

# Serve static files (frontend)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/app")
    async def serve_app():
        return FileResponse(os.path.join(static_dir, "index.html"))
