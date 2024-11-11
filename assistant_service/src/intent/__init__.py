from intent.functions import information_from_rag_desc, movie_reviews_desc, unknown_intent_desc
from intent.functions import get_information_from_rag, get_movie_reviews, handle_unknown_intent

functions = [
    information_from_rag_desc,
    movie_reviews_desc,
    unknown_intent_desc
]

function_map = {
    "get_information_from_rag": get_information_from_rag,
    "get_movie_reviews": get_movie_reviews,
    "handle_unknown_intent": handle_unknown_intent
}

system_prompt = {
    "rus": (
        "Вы являетесь ассистентом для онлайн кинотеатра. "
        "Ваша задача - анализировать запросы пользователей и определять интент. "
        "В зависимости от интента, вы должны вернуть соответствующую функцию и аргументы."
    ),
    "eng": (
        "You are an assistant for an online cinema platform. "
        "Your task is to analyze user requests and determine the intent. "
        "Depending on the intent, you should return the corresponding function and arguments."
    )
}


async def determine_intent(user_request):

    messages = [
        {"role": "system", "content": system_prompt["eng"]},
        {"role": "user", "content": user_request}
    ]

    # Формируем payload для запроса к LLM
    api_request_payload = {
        "model": "gpt-4",  # или другая используемая модель
        "messages": messages,
        "functions": functions,
        "function_call": "auto"
    }

    # Отправляем запрос к LLM (реализация функции get_llm_response уже есть)
    assistant_response = await get_llm_response(api_request_payload)

    # Извлекаем функцию из ответа LLM
    assistant_message = assistant_response["choices"][0]["message"]
    function_call = assistant_message.get("function_call")

    if function_call:
        function_name = function_call["name"]
        arguments = json.loads(function_call["arguments"])

        # Вызываем соответствующую функцию
        func = function_map.get(function_name)
        if func:
            func(**arguments)
        else:
            print(f"Функция {function_name} не реализована.")
    else:
        # Обработка случая, когда функция не возвращена
        print("LLM не вернула функцию для вызова.")
