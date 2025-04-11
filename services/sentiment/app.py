from fastapi import FastAPI, Query
from model import analyze_sentiment

app = FastAPI(title="Sentiment Analysis Service")

@app.get("/")
def root():
    return {"message": "Sentiment Analysis API is running"}

@app.get("/sentiment")
def get_sentiment(text: str = Query(..., min_length=1)):
    return analyze_sentiment(text)
