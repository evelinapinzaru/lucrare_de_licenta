# COMMAND TO RUN BACKEND: `uvicorn main:app --reload -- port 8080`

from fastapi import FastAPI, Request
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_store = {}

@app.middleware("http")
async def session_middleware(request: Request, call_next):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid4())

    request.state.session_id = session_id
    response = await call_next(request)
    response.set_cookie(key="session_id", value=session_id)
    return response

@app.get("/session-test")
def test_session(request: Request):
    session_id = request.state.session_id
    session_store.setdefault(session_id, {"visit_count": 0})
    session_store[session_id]["visit_count"] += 1
    return {"session_id": session_id, "visit_count": session_store[session_id]["visit_count"]}

@app.get("/")
def root():
    return {
        "message": "It's working!"
    }