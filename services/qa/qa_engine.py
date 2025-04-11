from transformers import pipeline

qa_pipeline = pipeline("question-answering")

def answer_question(question: str, context: str) -> dict:
    result = qa_pipeline({
        "question": question,
        "context": context
    })
    return {
        "answer": result["answer"],
        "score": round(result["score"], 4),
        "start": result["start"],
        "end": result["end"]
    }
