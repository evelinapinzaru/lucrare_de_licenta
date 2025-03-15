from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_content = await file.read()
    return JSONResponse({
        "filename": file.filename,
        "size": len(file_content)
    })

@app.get("/")
async def root():
    return {"message": "Welcome to my web app!"}