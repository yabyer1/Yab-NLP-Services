import requests

text = "Apple is looking at buying U.K. startup for $1 billion."

res = requests.get("http://localhost:8003/preprocess", params={"text": text})
print(res.json())
