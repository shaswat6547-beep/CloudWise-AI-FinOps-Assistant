from fastapi import FastAPI, UploadFile, File
import tempfile
import os

from billing_analyzer import analyze_billing


app = FastAPI(
    title="CloudWise AI FinOps Assistant",
    description="AI-powered cloud cost analysis platform",
    version="1.0"
)


@app.get("/")
def home():
    return {
        "message": "CloudWise is running!",
        "status": "success"
    }


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    contents = await file.read()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".csv"
    ) as temp:

        temp.write(contents)
        temp_path = temp.name

    try:
        result = analyze_billing(temp_path)
        return result

    finally:
        os.remove(temp_path)