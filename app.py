from fastapi import FastAPI, Request, Form
from fastapi import UploadFile, File
from rag import register_pdf, retrieve_context, clear_rag_data
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import requests
from db import init_db, insert_message, get_recent_messages,clear_chat_history

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

@app.get("/chat", response_class=HTMLResponse)
def chat(request: Request):
    messages = get_recent_messages()
    return templates.TemplateResponse("index.html", {"request": request, "messages": messages})

@app.post("/chat")
def chat(request: Request, message: str = Form(...)):
    #RAG検索
    context=retrieve_context(message)
    
    #LLMへ渡すプロンプトを生成
    prompt=f"""
    以下の資料内容を参考にして質問に答えてください。
    ---
    {context}
    ---
    質問:{message}
    """
    
    print(prompt)
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(LMSTUDIO_API, json=payload)
    data = response.json()
    reply = data["choices"][0]["message"]["content"]
    
    insert_message(message,reply)
    messages=get_recent_messages()
    return templates.TemplateResponse("index.html",{"request": request, "messages": messages})

@app.post("/upload_pdf")
async def upload_pdf(file:UploadFile=File(...)):
    os.makedirs("uploads",exist_ok=True)
    file_path=f"uploads/{file.filename}"
    
    with open(file_path,"wb") as f:
        f.write(await file.read())
        
        num_chunks=register_pdf(file_path)
        return {"message":f"{file.filename}を登録しました({num_chunks}チャンクに分割)"}
    
@app.post("/clear_data")
def clear_data():
    clear_chat_history()
    clear_rag_data()
    return {"message":"All chat and RAG data cleared"}
    