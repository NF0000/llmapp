from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import requests
from db import init_db, insert_message, get_recent_messages

app = FastAPI()

#テンプレートと静的ファイル設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

#LMStudioのAPI情報
load_dotenv()
LMSTUDIO_API = os.getenv("LMSTUDIO_API")
MODEL = os.getenv("MODEL_NAME")

@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    messages = get_recent_messages()
    return templates.TemplateResponse("index.html", {"request": request, "messages": messages})

@app.post("/chat", response_class=HTMLResponse)
def chat(request: Request, message: str = Form(...)):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7
    }
    response = requests.post(LMSTUDIO_API, json=payload)
    data = response.json()
    reply = data["choices"][0]["message"]["content"]
    
    insert_message(message,reply)
    messages=get_recent_messages()
    return templates.TemplateResponse("index.html",{"request": request, "messages": messages})