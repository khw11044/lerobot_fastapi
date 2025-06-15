

```
project/
├── app
│   ├── config.py
│   ├── __init__.py
│   ├── main.py
│   ├── __pycache__
│   │   ├── config.cpython-310.pyc
│   │   ├── __init__.cpython-310.pyc
│   │   └── main.cpython-310.pyc
│   ├── routers
│   │   ├── camera.py
│   │   ├── chatbot.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── camera.cpython-310.pyc
│   │   │   ├── chatbot.cpython-310.pyc
│   │   │   ├── __init__.cpython-310.pyc
│   │   │   ├── robot.cpython-310.pyc
│   │   │   └── stream.cpython-310.pyc
│   │   └── robot.py
│   └── services
│       ├── camera_service.py
│       ├── communication_service.py
│       ├── __init__.py
│       ├── llm_service.py
│       └── __pycache__
│           ├── communication_service.cpython-310.pyc
│           ├── __init__.cpython-310.pyc
│           └── llm_service.cpython-310.pyc
├── chat_history.db
├── README.md
├── requirements.txt
├── run.py
├── static
│   ├── index.html
│   ├── script.js
│   └── style.css
└── utils
    ├── databases
    │   ├── database.py
    │   └── __init__.py
    ├── __init__.py
    ├── prompts
    │   ├── __init__.py
    │   └── prompt.py


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

# 실행 

```
python run.py
```