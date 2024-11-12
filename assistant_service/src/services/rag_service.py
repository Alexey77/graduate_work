import json
from functools import lru_cache
from typing import Any

from core.logger import get_logger
from dependencies import get_llm_client
from fastapi import Depends
from llm import LLMClient
from schemes import ReplyResponseModel, Role

logger = get_logger(__name__)


class RAGService:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    async def determine_intent(self, user_query: str) -> str:
        intent_prompt = (
            "Определи намерение пользователя на основе запроса. Ответь одним словом "
            "с использованием одного из следующих вариантов: "
            "'get_info_about_person_or_movie', 'get_cinema_info', 'handle_subscription_request', "
            "'get_movie_reviews', 'get_personal_recommendations', 'report_technical_issue', "
            "'handle_general_inquiry'. Ответь только названием намерения, без пояснений."
        )
        messages = [
            {"role": "system", "content": intent_prompt},
            {"role": "user", "content": user_query},
        ]
        response = await self._llm.get_completion(
            service=3,
            model="gpt-4o-mini",
            system=intent_prompt,
            max_tokens=10,
            messages=json.dumps(messages, ensure_ascii=False),
        )

        intent = response.reply.strip().lower()

        valid_intents = {
            "get_info_about_person_or_movie",
            "get_cinema_info",
            "handle_subscription_request",
            "get_movie_reviews",
            "get_personal_recommendations",
            "report_technical_issue",
            "handle_general_inquiry",
        }

        if intent not in valid_intents:
            intent = "handle_general_inquiry"

        if intent == "handle_general_inquiry":
            lower_query = user_query.lower()
            if any(
                keyword in lower_query
                for keyword in [
                    "кто он",
                    "фильм",
                    "снимался",
                    "актёр",
                    "актриса",
                    "фильмы",
                    "режиссёр",
                    "персона",
                ]
            ):
                intent = "get_info_about_person_or_movie"
            elif any(
                keyword in lower_query
                for keyword in [
                    "подписка",
                    "условия",
                    "тариф",
                    "стоимость",
                    "доступ",
                    "доступен",
                    "сеанс",
                    "расписание",
                    "в прокате",
                ]
            ):
                intent = "get_cinema_info"
            elif any(
                keyword in lower_query
                for keyword in [
                    "подписаться",
                    "оформить подписку",
                    "отписаться",
                    "отмена подписки",
                    "оплата",
                    "счёт",
                    "платёж",
                    "продлить",
                    "активировать",
                ]
            ):
                intent = "handle_subscription_request"
            elif any(
                keyword in lower_query
                for keyword in [
                    "отзывы",
                    "мнение",
                    "рейтинг",
                    "оценка",
                    "как фильм",
                    "обзор",
                ]
            ):
                intent = "get_movie_reviews"
            elif any(
                keyword in lower_query
                for keyword in [
                    "рекомендации",
                    "посоветуй",
                    "посоветовать",
                    "что посмотреть",
                    "совет",
                    "под настроение",
                    "на выходные",
                    "лучшие фильмы",
                    "для семьи",
                ]
            ):
                intent = "get_personal_recommendations"
            elif any(
                keyword in lower_query
                for keyword in [
                    "проблема",
                    "не работает",
                    "ошибка",
                    "сбой",
                    "техническая поддержка",
                    "не загружается",
                    "проблемы с доступом",
                    "вход",
                    "аккаунт",
                    "зависает",
                    "не воспроизводится",
                    "звука нет",
                ]
            ):
                intent = "report_technical_issue"

        return intent

    async def get_info_about_person_or_movie(self, query: str) -> dict[str, Any]:
        return {"source": query, "search_query": "информация о фильме или человеке"}

    async def get_cinema_info(self, query: str) -> dict[str, Any]:
        return {"info": "условия подписки или доступность фильма"}

    async def handle_subscription_request(
        self, action: str, user_id: int
    ) -> dict[str, Any]:
        return {"status": f"Subscription {action}", "user_id": user_id}

    async def get_movie_reviews(self, movie_title: str) -> dict[str, Any]:
        return {"reviews": f"Отзывы о фильме {movie_title}"}

    async def get_personal_recommendations(self, preferences: str) -> dict[str, Any]:
        return {"recommendations": f"Рекомендации по фильмам на основе {preferences}"}

    async def report_technical_issue(self, issue_description: str) -> dict[str, Any]:
        return {"status": "Issue reported", "description": issue_description}

    async def handle_general_inquiry(self, query: str) -> dict[str, Any]:
        return {"response": f"Общий ответ на запрос: {query}"}

    async def process_query(self, user_query: str) -> dict[str, Any]:
        intent = await self.determine_intent(user_query)
        parameters = {
            "query": user_query,
            "action": "subscribe",
            "user_id": 123,
            "movie_title": "Some Movie",
            "preferences": "comedy",
            "issue_description": "Issue description here",
        }

        intent_function_mapping = {
            "get_info_about_person_or_movie": self.get_info_about_person_or_movie,
            "get_cinema_info": self.get_cinema_info,
            "handle_subscription_request": self.handle_subscription_request,
            "get_movie_reviews": self.get_movie_reviews,
            "get_personal_recommendations": self.get_personal_recommendations,
            "report_technical_issue": self.report_technical_issue,
        }

        func = intent_function_mapping.get(intent, self.handle_general_inquiry)

        if intent in ["get_info_about_person_or_movie", "get_cinema_info"]:
            result = await func(parameters["query"])
        elif intent == "handle_subscription_request":
            result = await func(parameters["action"], parameters["user_id"])
        elif intent == "get_movie_reviews":
            result = await func(parameters["movie_title"])
        elif intent == "get_personal_recommendations":
            result = await func(parameters["preferences"])
        elif intent == "report_technical_issue":
            result = await func(parameters["issue_description"])
        else:
            result = await func(parameters["query"])

        return result

    async def get_enriched_context(self, user_query: str) -> str:
        similar_fragments = await self._llm.get_similar_fragments(user_query)

        enriched_context = "\n".join(
            [
                f"{frag['text']} (relevance score: {frag['score']})"
                for frag in similar_fragments
            ]
        )
        logger.info("Enriched context generated for query.")

        return enriched_context

    async def get_answer(
        self, messages: dict, system_prompt: str
    ) -> ReplyResponseModel:
        response = await self._llm.get_completion(
            service=3,
            model="gpt-4o-mini",
            system=system_prompt,
            max_tokens=150,
            messages=json.dumps([messages], ensure_ascii=False),
        )

        return ReplyResponseModel(
            messages=[
                messages,
                {"role": Role.assistant.value, "content": response.reply},
            ]
        )


@lru_cache
def get_rag_service(llm=Depends(get_llm_client)) -> RAGService:
    return RAGService(llm)
