# COMMAND TO RUN BACKEND: `uvicorn main:app --reload --port 8080`

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
from dotenv import load_dotenv
from collections import defaultdict
import shutil
import os
import textract
import traceback
from openai import OpenAI
import itertools

load_dotenv()
client = OpenAI()

class MasterConcept(BaseModel):
    concept: str

class ExerciseRequest(BaseModel):
    concept: str

class SolutionSubmission(BaseModel):
    concept: str
    exercise: str
    solution: str

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_concepts = {}
concept_links_by_file = {}

@app.middleware("http")
async def session_middleware(request: Request, call_next):
    session_id = request.cookies.get("session_id")

    if not session_id:
        session_id = str(uuid4())
    request.state.session_id = session_id
    response = await call_next(request)
    response.set_cookie(key="session_id", value=session_id)
    return response

@app.get("/")
def root():
    return {"message": "It's working!"}

def extract_concepts(text: str) -> str:
    gpt_input = text[:3000]
    prompt = (
        "Extract a list of programming concepts mentioned or explained in the text below. "
        "Return them as a comma-separated list only, with no explanations or formatting.\n\n"
        f"{gpt_input}\n\nList:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You extract programming concepts from university course material."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"OpenAI request has failed: {e}")

def map_concept_links (text: str, concepts: list[str]) -> dict:
    concept_links = defaultdict(lambda: defaultdict(int))
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    for paragraph in paragraphs:
        found = [c for c in concepts if c.lower() in paragraph.lower()]
        for a, b in itertools.combinations(set(found), 2):
            concept_links[a][b] += 1
            concept_links[b][a] += 1
    return {k: dict(v) for k, v in concept_links.items()}

@app.post("/upload")
async def handle_file_upload(request: Request, file: UploadFile = File(...)):
    session_id = request.state.session_id
    save_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(save_path, "wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

    try:
        if file.filename.endswith(".txt"):
            with open(save_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = textract.process(save_path).decode("utf-8")
        concept_string = extract_concepts(content)
    except Exception as e:
        return {
            "filename": file.filename,
            "message": "File has been saved, but concepts couldn't be extracted!",
            "error": repr(e),
            "trace": traceback.format_exc()
        }

    concept_list = [c.strip() for c in concept_string.split(",") if c.strip()]
    session_concepts.setdefault(session_id, {})

    for concept in concept_list:
        concept_data = session_concepts[session_id].setdefault(concept, {
            "complexity": "unknown",
            "understanding": 0,
            "files": []
        })
        if file.filename not in concept_data["files"]:
            concept_data["files"].append(file.filename)

    concept_links = map_concept_links (content, concept_list)
    concept_links_by_file[file.filename] = concept_links
    mastered = [
        concept for concept in concept_list
        if session_concepts[session_id][concept]["understanding"] == 1
    ]

    return {
        "filename": file.filename,
        "message": "File has been uploaded and processed!",
        "text_preview": content[:500],
        "concepts": concept_list,
        "mastered_concepts": {concept: True for concept in mastered},
        "concept_links": concept_links
    }

@app.post("/mark")
def mark_concept_as_mastered(request: Request, payload: MasterConcept):
    session_id = request.state.session_id
    concept = payload.concept

    if session_id not in session_concepts:
        return {"message": "Session hasn't been found."}
    if concept not in session_concepts[session_id]:
        return {"message": "Concept hasn't been found."}
    session_concepts[session_id][concept]["understanding"] = 1
    return {"message": f"{concept} has been marked as mastered."}

@app.post("/generate-exercise")
def generate_exercise(request: Request, payload: ExerciseRequest):
    session_id = request.state.session_id
    concept = payload.concept

    prompt = (
        f"Generate a beginner-friendly coding exercise for the concept: {concept}. "
        f"Keep it short. Then provide a hint. Format it like this:\n\n"
        f"Exercise:\n<exercise>\n\nHint:\n<hint>"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You help students learn programming by generating exercises."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        content = response.choices[0].message.content
        exercise_text = content.strip()

        # Store in session if possible
        if session_id in session_concepts and concept in session_concepts[session_id]:
            session_concepts[session_id][concept]["exercise"] = exercise_text

        return {"concept": concept, "exercise": exercise_text}

    except Exception as e:
        return {"error": str(e)}

@app.post("/check-solution")
def evaluate_solution(request: Request, payload: SolutionSubmission):
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
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You evaluate student code and provide constructive feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return {"feedback": response.choices[0].message.content.strip()}

    except Exception as e:
        return {"error": str(e)}