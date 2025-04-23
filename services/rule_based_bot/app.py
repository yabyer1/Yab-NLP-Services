from fastapi import FastAPI, Query
from rule_bot import get_rule_response
from neural_bot import get_neural_response

app = FastAPI(title="Chatbot Service")

@app.get("/")
def root():
    return {"message": "Chatbot service is live"}

@app.get("/chat")
def chat(
    message: str = Query(..., min_length=1),
    mode: str = Query("rule", enum=["rule", "neural"])
):
    if mode == "rule":
        return {"response": get_rule_response(message)}
    else:
        return {"response": get_neural_response(message)}
