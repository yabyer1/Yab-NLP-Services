import requests

text = "I love this project, it's so helpful and clean!"
response = requests.get("http://localhost:8000/sentiment", params={"text": text})
print(response.json())
