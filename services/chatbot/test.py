import requests

message = "hello"
res = requests.get("http://localhost:8004/chat", params={"message": message, "mode": "rule"})
print("Rule-based:", res.json())

res = requests.get("http://localhost:8004/chat", params={"message": message, "mode": "neural"})
print("Neural:", res.json())
