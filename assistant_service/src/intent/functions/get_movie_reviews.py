function_description = {
    "name": "get_movie_reviews",
    "description": "Fetches movie reviews, normalizing the movie title in both Russian and original languages.",
    "parameters": {
        "type": "object",
        "properties": {
            "title_rus": {
                "type": "string",
                "description": "The movie title in Russian."
            },
            "title_original": {
                "type": "string",
                "description": "The original title of the movie."
            }
        },
        "required": ["title_rus", "title_original"]
    }
}


def get_movie_reviews(title_rus, title_original):
    print(f"Получение отзывов о фильме. Русское название: {title_rus}, Оригинальное название: {title_original}")
