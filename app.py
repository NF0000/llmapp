from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import requests

app = FastAPI()

#テンプレートと静的ファイル設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

#LMStudioのAPI情報
load_dotenv()
LMSTUDIO_API = os.getenv("LMSTUDIO_API")
MODEL = os.getenv("MODEL_NAME")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "messages": []})

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

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "messages": [
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply}
        ]}
    )