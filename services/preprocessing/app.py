from fastapi import FastAPI, Query
from processor import preprocess_text

app = FastAPI(title="Preprocessing Service")

@app.get("/")
def root():
    return {"message": "Text Preprocessing API is live"}

@app.get("/preprocess")
def get_preprocessed(text: str = Query(..., min_length=5)):
    return preprocess_text(text)
