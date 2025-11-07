from fastapi import FastAPI, HTTPException
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
def read_root():
    return {"msg": "Mindmap Agent API is running"}

@app.get("/verify-api-key")
def verify_api_key():
    """
    Verify if the OpenAI API key is valid by making a simple API call.
    """
    try:
        # Try to list available models (lightweight API call)
        response = client.models.list()

        # If we get here, the API key is valid
        return {
            "status": "success",
            "message": "API 키가 유효합니다!",
            "api_key_prefix": os.getenv("OPENAI_API_KEY")[:20] + "..." if os.getenv("OPENAI_API_KEY") else None,
            "models_available": True
        }
    except Exception as e:
        # If there's an error, the API key is likely invalid
        error_message = str(e)
        return {
            "status": "error",
            "message": "API 키가 유효하지 않습니다.",
            "error": error_message
        }

@app.get("/test-chat")
def test_chat():
    """
    Test the API key with a simple chat completion request.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'API key is working!' in Korean"}
            ],
            max_tokens=50
        )

        return {
            "status": "success",
            "message": "API 키가 정상적으로 작동합니다!",
            "response": response.choices[0].message.content
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"API 호출 실패: {str(e)}")