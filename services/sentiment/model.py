from transformers import pipeline

# Load a pre-trained Hugging Face sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

def analyze_sentiment(text: str):
    result = sentiment_pipeline(text)
    return {
        "label": result[0]["label"],
        "score": round(result[0]["score"], 4)
    }
