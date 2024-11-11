function_description = {
    "name": "get_information_from_rag",
    "description": "Extracts the main intent of the user's query and forms a search query in both Russian and English.",
    "parameters": {
        "type": "object",
        "properties": {
            "eng": {
                "type": "string",
                "description": "Search query in English."
            },
            "rus": {
                "type": "string",
                "description": "Search query in Russian."
            }
        },
        "required": ["eng", "rus"]
    }
}


def get_information_from_rag(eng, rus):
    print(f"Получен информационный запрос. Английский: {eng}, Русский: {rus}")
    # Заглушка для дальнейшей реализации
    pass
