function_description = {
    "name": "handle_unknown_intent",
    "description": "Handles an unknown or unclear user intent.",
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "A message indicating that the user's intent was not understood."
            }
        },
        "required": ["message"]
    }
}


def handle_unknown_intent(message):
    print(f"Неизвестный интент. Сообщение пользователю: {message}")
