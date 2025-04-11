from fastapi import FastAPI, Query
from qa_engine import answer_question

app = FastAPI(title="QA Service")

@app.get("/")
def root():
    return {"message": "Question Answering service is live"}

@app.get("/qa")
def get_answer(
    question: str = Query(..., min_length=5),
    context: str = Query(..., min_length=20)
):
    return answer_question(question, context)
