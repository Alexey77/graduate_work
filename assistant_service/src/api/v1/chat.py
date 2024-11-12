from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.logger import get_logger
from schemes import ChatMessage, ReplyResponseModel, Role, UserMessage
from services.chats import ChatService, get_chat_service
from services.exception import ServiceException
from services.rag_service import RAGService, get_rag_service

router = APIRouter()
security = HTTPBearer()
logger = get_logger(__name__)


@router.post("/chat",
             status_code=HTTPStatus.OK,
             response_model=ReplyResponseModel)
async def chat(
        question_message: UserMessage | list[ChatMessage],
        credentials: HTTPAuthorizationCredentials = Depends(security),
        questions_service: RAGService = Depends(get_rag_service),
        chat_service: ChatService = Depends(get_chat_service),
        # auth_service: AuthService = Depends(get_auth_service),
        # user_agent: Annotated[str | None, Header()] = None
):
    # access_token = credentials.credentials

    # Authorization code can be uncommented if needed
    # if access_token is None or not await auth_service.validate_access_token(access_token):
    #     logger.info("Authorization without a access token or the token is not valid")
    #     raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
    #                         detail="Authorization without a access token or the token is not valid",
    #                         headers={"WWW-Authenticate": "Bearer"})
    #
    # user = await auth_service.get_login_from_access_token(access_token=access_token)
    #
    # if user is None:
    #     logger.info("Authorization of an unknown user")
    #     raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
    #                         detail="Authorization without a access token or the token is not valid",
    #                         headers={"WWW-Authenticate": "Bearer"})

    try:
        messages = await chat_service.get_answer(messages=[question_message], user="ddd")
    except ServiceException as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=HTTPStatus.INTERNAL_SERVER_ERROR.phrase,
        )
    from icecream import ic

    ic(messages)

    return ReplyResponseModel(messages=messages)


    # intent = await questions_service.determine_intent(user_query=question_message.content)
    # logger.info(f"Intent determined: {intent}")


    # if intent in ["get_info_about_person_or_movie", "get_cinema_info"]:
    #     enriched_context = await questions_service.get_enriched_context(user_query=question_message.content)
    #     system_prompt = (
    #         f"Ты ассистент онлайн кинотеатра по имени Бруно. Вот тебе контекст из базы данных кинотеатра, "
    #         f"который поможет тебе ответить на вопрос.\n\n"
    #         f"Контекст:\n{enriched_context}\n\n"
    #     )
    # else:
    #     system_prompt = "Ты ассистент онлайн кинотеатра по имени Бруно."
    # logger.info(system_prompt)
    # #
    # response = await questions_service.get_answer(messages={
    #     "role": Role.user.value,
    #     "content": question_message.content
    # }, system_prompt=system_prompt)
    #
    # logger.info(f"Response generated: {response}")
    return question_message
