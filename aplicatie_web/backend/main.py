"""
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
"""

from fastapi import FastAPI
from transformers import pipeline  # Using pipeline for better reliability
import torch
from fastapi.responses import JSONResponse

app = FastAPI()

# Configuration
MODEL_NAME = "Salesforce/codet5p-220m"
DEVICE = 0 if torch.cuda.is_available() else -1

# Initialize generator with multiple fallbacks
try:
    generator = pipeline(
        "text2text-generation",
        model=MODEL_NAME,
        device=DEVICE,
        torch_dtype=torch.float16 if DEVICE != -1 else torch.float32
    )
except Exception as e:
    raise RuntimeError(f"Failed to initialize generator: {str(e)}")


@app.get("/generate_exercise")
async def generate_exercise(concept: str = "for loops"):
    # Multi-stage prompt with explicit formatting
    prompt = f"""Generate a COMPLETE Python exercise about {concept}. Follow this exact format:

    ### Problem Statement
    [Clear description of the programming task]

    ### Example Input/Output
    Input: [sample input]
    Output: [expected output]

    ### Solution Code
    ```python
    [Complete Python code solution]
    ```

    Now generate an exercise about {concept}:
    """

    try:
        # First attempt with careful parameters
        result = generator(
            prompt,
            max_length=600,
            num_beams=4,
            temperature=0.9,
            top_p=0.95,
            do_sample=True,
            early_stopping=True
        )

        full_response = result[0]['generated_text']

        # If response is too short, try more aggressive generation
        if len(full_response.split()) < 30:
            result = generator(
                prompt,
                max_length=800,
                temperature=1.0,
                top_k=50,
                do_sample=True,
                num_return_sequences=1
            )
            full_response = result[0]['generated_text']

        # Final fallback if still too short
        if len(full_response.split()) < 30:
            full_response = f"""### Problem Statement
Write a Python program using {concept} that demonstrates their usage.

### Example Input/Output
Input: [provide example]
Output: [expected result]

### Solution Code
```python
# Basic {concept} example
# [Generated response was too short - please expand this template]
```"""

        return JSONResponse({"exercise": full_response})

    except Exception as e:
        return JSONResponse(
            {"error": str(e), "message": "Failed to generate exercise"},
            status_code=500
        )


@app.get("/")
async def root():
    return {"message": "API is working"}