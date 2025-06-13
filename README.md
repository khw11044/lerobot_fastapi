

```
project/
├── README.md                  # 프로젝트 설명서
├── run.py                     # 서버 실행 파일
├── requirements.txt           # 필요한 패키지 목록
├── check_camera.py           # 카메라 확인 스크립트
├── app/
│   ├── __init__.py           # 앱 초기화 파일
│   ├── main.py               # FastAPI 메인 서버
│   ├── routers/
│   │   ├── __init__.py       # 라우터 초기화 파일
│   │   └── chatbot.py        # 챗봇 라우터
│   └── services/
│       ├── __init__.py       # 서비스 초기화 파일
│       └── llm_service.py    # LLM 서비스 로직
└── static/
    ├── index.html            # 메인 웹 페이지
    ├── style.css             # 스타일시트
    └── script.js             # JavaScript 로직
```


# 가상 환경 준비 

```
conda create -n fastapi python=3.10 -y

conda activate fastapi
```

# 패키지 설치 

```
pip install -r requirements.txt
```