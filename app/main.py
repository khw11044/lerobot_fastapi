from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from .routers import chatbot, audio
import os

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 챗봇 라우터 등록
app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(audio.router, prefix="/audio", tags=["Audio"])

# 메인 페이지 서빙
@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)