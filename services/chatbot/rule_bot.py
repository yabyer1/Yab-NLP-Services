def get_rule_response(message: str) -> str:
    message = message.lower()

    if "hello" in message or "hi" in message:
        return "Hi there! How can I assist you today?"
    elif "help" in message:
        return "I'm here to help. What do you need assistance with?"
    elif "bye" in message:
        return "Goodbye! Have a great day!"
    else:
        return "I'm not sure how to respond to that. Can you rephrase?"
