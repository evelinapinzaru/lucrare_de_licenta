# COMMAND TO RUN BACKEND: `uvicorn main:app --reload --port 8080`

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
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

concept_registry = {} # per session
cooccurrence_maps = {} # per file

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

def get_concepts_from_text(text: str) -> str:
    limited_text = text[:3000]
    prompt = (
        "Extract a list of programming concepts mentioned or explained in the text below. "
        "Return them as a comma-separated list only, with no explanations or formatting.\n\n"
        f"{limited_text}\n\nList:"
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
        raise RuntimeError(f"OpenAI request failed: {e}")

def build_cooccurrence_map(text: str, concepts: list[str]) -> dict:
    co_map = defaultdict(lambda: defaultdict(int))
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    for paragraph in paragraphs:
        found = [c for c in concepts if c.lower() in paragraph.lower()]
        for a, b in itertools.combinations(set(found), 2):
            co_map[a][b] += 1
            co_map[b][a] += 1
    return {k: dict(v) for k, v in co_map.items()}

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

        concept_string = get_concepts_from_text(content)
    except Exception as e:
        return {
            "filename": file.filename,
            "message": "File saved, but concept extraction failed!",
            "error": repr(e),
            "trace": traceback.format_exc()
        }

    concept_list = [c.strip() for c in concept_string.split(",") if c.strip()]
    concept_registry.setdefault(session_id, {})

    for concept in concept_list:
        concept_data = concept_registry[session_id].setdefault(concept, {
            "complexity": "unknown",
            "understanding": 0,
            "files": []
        })
        if file.filename not in concept_data["files"]:
            concept_data["files"].append(file.filename)

    co_map = build_cooccurrence_map(content, concept_list)
    cooccurrence_maps[file.filename] = co_map

    return {
        "filename": file.filename,
        "message": "File uploaded and processed!",
        "text_preview": content[:500],
        "concepts": concept_list,
        "concept_links": co_map
    }