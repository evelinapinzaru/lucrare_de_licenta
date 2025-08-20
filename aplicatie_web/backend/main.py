# COMMAND TO RUN BACKEND: `uvicorn main:app --reload --port 8080`

# Standard library imports
import itertools
import json
import logging
import os
import shutil
import traceback
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Any, cast
from uuid import uuid4

# Third-party imports
from fastapi import FastAPI, File, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI

# Local imports
from auth import auth_router
from config import settings
from models import ExerciseRequest, MasterConcept, SolutionSubmission

client = OpenAI(api_key=settings.OPENAI_API_KEY)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_SESSION = "fallback_session"
MAX_CONTENT_LENGTH = 4000

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

def get_session_id(request: Request) -> str:
    if hasattr(request.state, 'session_id'):
        return request.state.session_id
    else:
        logger.warning("Session ID not found, using default session")
        return DEFAULT_SESSION

@asynccontextmanager
async def lifespan(_app: FastAPI):
    if not os.path.exists(settings.DATABASE_PATH):
        with open(settings.DATABASE_PATH, "w") as f:
            json.dump({}, cast(Any, f))
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    cast(Any, CORSMiddleware),
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_concepts = {}
concept_links_by_file = {}

@app.middleware("http")
async def session_middleware(request: Request, call_next) -> Response:
    try:
        session_id = request.cookies.get("session_id")
        if not session_id:
            session_id = str(uuid4())
        request.state.session_id = session_id
        response = await call_next(request)
        response.set_cookie(key="session_id", value=session_id)
        return response
    except Exception as e:
        logger.error(f"Session middleware failed: {e}")
        request.state.session_id = DEFAULT_SESSION
        response = await call_next(request)
        return response

app.include_router(auth_router)

@app.get("/public-config")
def get_public_config():
    return {
        "maxSizeMb": settings.MAX_SIZE_MB,
        "supportedExtensions": settings.SUPPORTED_EXTENSIONS,
        "supportedMimeTypes": settings.SUPPORTED_MIME_TYPES
    }

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "It's working!"}

@app.get("/progress")
async def get_progress(request: Request) -> JSONResponse:
    session_id = get_session_id(request)
    if session_id not in session_concepts:
        return JSONResponse({"mastered": 0, "unmastered": 0, "total": 0})
    concepts = session_concepts[session_id]
    mastered = sum(1 for c in concepts.values() if c["understanding"] == 1)
    total = len(concepts)
    return JSONResponse({
        "mastered": mastered,
        "unmastered": total - mastered,
        "total": total
    })

def extract_concepts(text: str) -> str:
    gpt_input = text[:MAX_CONTENT_LENGTH]
    prompt = (
        "Extract a list of programming concepts mentioned or explained in the text below. "
        "Return them as a comma-separated list only, with no explanations or formatting.\n\n"
        f"{gpt_input}\n\nList:"
    )
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You extract programming concepts from university course material."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            timeout=10
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("OpenAI extraction failed: %s", e)
        raise RuntimeError(f"OpenAI request has failed: {e}")

def map_concept_links(text: str, concepts: list[str]) -> dict[str, dict[str, int]]:
    concept_links = defaultdict(lambda: defaultdict(int))
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    for paragraph in paragraphs:
        found = [c for c in concepts if c.lower() in paragraph.lower()]
        for a, b in itertools.combinations(set(found), 2):
            concept_links[a][b] += 1
            concept_links[b][a] += 1
    return {k: dict(v) for k, v in concept_links.items()}

# @app.post("/upload")
# async def handle_file_upload(request: Request, file: UploadFile = File(...)):
#     session_id = get_session_id(request)
#     save_path = os.path.join(settings.UPLOAD_DIR, file.filename)
#     with open(save_path, "wb") as out_file:
#         shutil.copyfileobj(file.file, out_file)
#     try:
#         if file.filename.endswith(".txt"):
#             with open(save_path, "r", encoding="utf-8") as f:
#                 content = f.read()
#         else:
#             content = textract.process(save_path).decode("utf-8")
#         concept_string = extract_concepts(content)
#     except Exception as e:
#         return JSONResponse({
#             "filename": file.filename,
#             "message": "File has been saved, but concepts couldn't be extracted!",
#             "error": repr(e),
#             "trace": traceback.format_exc()
#         })
#     concept_list = [c.strip() for c in concept_string.split(",") if c.strip()]
#     session_concepts.setdefault(session_id, {})
#     for concept in concept_list:
#         concept_data = session_concepts[session_id].setdefault(concept, {
#             "complexity": "unknown",
#             "understanding": 0,
#             "files": []
#         })
#         if file.filename not in concept_data["files"]:
#             concept_data["files"].append(file.filename)
#     concept_links = map_concept_links (content, concept_list)
#     concept_links_by_file[file.filename] = concept_links
#     return JSONResponse({
#         "filename": file.filename,
#         "message": "File has been uploaded and processed!",
#         "concepts": concept_list
#     })

@app.post("/mark")
async def mark_concept_as_mastered(request: Request, payload: MasterConcept) -> dict[str, str]:
    session_id = get_session_id(request)
    concept = payload.concept
    if session_id not in session_concepts:
        return {"error": "Session hasn't been found."}
    if concept not in session_concepts[session_id]:
        return {"error": "Concept hasn't been found."}
    session_concepts[session_id][concept]["understanding"] = 1
    return {"message": f"{concept} has been marked as mastered."}

@app.post("/generate-exercise")
async def generate_exercise(request: Request, payload: ExerciseRequest) -> JSONResponse:
    session_id = get_session_id(request)
    concept = payload.concept
    prompt = (
        f"Generate a beginner-friendly coding exercise for the concept: {concept}. "
        f"Keep it short. Then provide a hint. Format it like this:\n\n"
        f"Exercise:\n<exercise>\n\nHint:\n<hint>"
    )
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You help students learn programming by generating exercises."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        content = response.choices[0].message.content
        exercise_text = content.strip()

        match = exercise_text.split("\n\n")
        exercise = match[0].replace("Exercise:", "").strip()
        hint = match[1].replace("Hint:", "").strip()

        if session_id not in session_concepts:
            session_concepts[session_id] = {}
        session_concepts[session_id][concept] = session_concepts[session_id].get(concept, {})
        session_concepts[session_id][concept]["exercise"] = exercise
        session_concepts[session_id][concept]["hint"] = hint
        return JSONResponse({"exercise": exercise, "hint": hint})

    except Exception as e:
        return JSONResponse({"error": str(e)})

@app.post("/check-solution")
async def evaluate_solution(payload: SolutionSubmission) -> JSONResponse:
    concept = payload.concept
    exercise = payload.exercise
    solution = payload.solution
    prompt = (
        f"You're an AI tutor. Here's a student's solution to a programming exercise about '{concept}'.\n"
        f"Exercise:\n{exercise}\n\nStudent's solution:\n{solution}\n\n"
        f"Evaluate the correctness of the solution. Respond with a short explanation and suggestion if needed."
    )
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You evaluate student code and provide constructive feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return JSONResponse({"feedback": response.choices[0].message.content.strip()})
    except Exception as e:
        return JSONResponse({"error": str(e)})