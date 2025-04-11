import requests

context = """
The Apollo program was the third United States human spaceflight program carried out by NASA, which 
accomplished landing the first humans on the Moon from 1969 to 1972. First conceived during the Eisenhower 
administration, Apollo began in earnest after President John F. Kennedy's May 25, 1961, address to Congress.
"""

question = "When did the Apollo program land humans on the Moon?"

res = requests.get("http://localhost:8002/qa", params={
    "question": question,
    "context": context
})
print(res.json())
