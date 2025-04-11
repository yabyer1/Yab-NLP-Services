from fastapi import FastAPI, Query
from summarizer import summarize_text

app = FastAPI(title="Summarization Service")

@app.get("/")
def root():
    return {"message": "Summarization service is live"}

@app.get("/summarize")
def get_summary(
    text: str = Query(..., min_length=20),
    min_length: int = 30,
    max_length: int = 130
):
    return summarize_text(text, max_length=max_length, min_length=min_length)
