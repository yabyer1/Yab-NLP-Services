import requests

long_text = """
Artificial intelligence (AI) is transforming industries and society. From healthcare and finance 
to entertainment and transportation, AI systems are enabling new efficiencies and insights. 
Machine learning models can predict diseases, personalize recommendations, and even drive vehicles. 
However, ethical and societal implications—like bias, transparency, and labor impact—must be carefully managed.
"""

res = requests.get("http://localhost:8001/summarize", params={"text": long_text})
print(res.json())
