from fastapi import FastAPI
from model import analyze_sentiment

app = FastAPI()

@app.get("/sentiment")
def get_sentiment(text: str):
    return analyze_sentiment(text)
# Yab-NLP-Services
