from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"msg": "Mindmap Agent API is running"}