from http import HTTPStatus

import pytest


@pytest.fixture
def user_registration_data():
    return {
        "email": "karimjon@mail.com",
        "password": "inshala",
        "first_name": "karim",
        "last_name": "jon"
    }


@pytest.fixture
def valid_user_credentials():
    return {
        "email": "karimjon@mail.com",
        "password": "inshala"
    }


@pytest.fixture
def invalid_password_credentials():
    return {
        "email": "karimjon@mail.com",
        "password": "wrong_password"
    }


@pytest.fixture
def non_existent_user_credentials():
    return {
        "email": "unknown_user@mail.com",
        "password": "random_password"
    }


async def clear_user_data(db_connection, login):
    user = await db_connection.fetchrow("SELECT id FROM public.users WHERE login = $1", login)

    if user:
        user_id = user["id"]
        await db_connection.execute("DELETE FROM public.user_sessions WHERE user_id = $1", user_id)
        await db_connection.execute("DELETE FROM public.user_roles WHERE user_id = $1", user_id)
        await db_connection.execute("DELETE FROM public.users WHERE login = $1", login)


@pytest.mark.asyncio
async def test_success_registration(make_post_http_request, user_registration_data, db_connection):
    status, body = await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )
    import pdb; pdb.set_trace()
    assert status == HTTPStatus.CREATED

    login = user_registration_data["email"]
    await clear_user_data(db_connection, login)


@pytest.mark.asyncio
async def test_registration_with_duplicate_login(make_post_http_request, user_registration_data, db_connection):
    status, body = await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )
    assert status == HTTPStatus.CREATED, "Первый пользователь должен быть успешно зарегистрирован"
    status, body = await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )
    assert status == HTTPStatus.CONFLICT, "Попытка зарегистрировать второго пользователя с тем же логином должна вернуть 409"

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)


@pytest.mark.asyncio
async def test_successful_login(make_post_http_request, valid_user_credentials, user_registration_data, db_connection):
    await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )
    status, body = await make_post_http_request(
        endpoint='auth/login',
        params=valid_user_credentials,
    )
    assert status == HTTPStatus.OK, "Успешный вход должен вернуть статус 200"
    assert "access_token" in body, "Ответ должен содержать access_token"
    assert "refresh_token" in body, "Ответ должен содержать refresh_token"

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)


@pytest.mark.asyncio
async def test_login_with_wrong_password(make_post_http_request, invalid_password_credentials, user_registration_data,
                                         db_connection):
    await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )

    status, body = await make_post_http_request(
        endpoint='auth/login',
        params=invalid_password_credentials,
    )
    assert status == HTTPStatus.UNAUTHORIZED, "Вход с неправильным паролем должен вернуть статус 401"

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)


@pytest.mark.asyncio
async def test_login_with_non_existent_user(make_post_http_request, non_existent_user_credentials):
    status, body = await make_post_http_request(
        endpoint='auth/login',
        params=non_existent_user_credentials,
    )
    assert status == HTTPStatus.UNAUTHORIZED, "Вход с несуществующим логином должен вернуть статус 401"
    assert body['detail'] == 'The login or password is incorrect.'


@pytest.mark.asyncio
async def test_successful_history(make_get_http_request, make_post_http_request, user_registration_data,
                                  db_connection, valid_user_credentials):
    await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )
    status, body = await make_post_http_request(
        endpoint='auth/login',
        params=valid_user_credentials,
    )
    valid_access_token = body['access_token']

    headers = {
        "access-token": f"{valid_access_token}"
    }
    status, body = await make_get_http_request(
        endpoint='auth/history',
        headers=headers,
    )
    assert status == HTTPStatus.OK, "Успешный запрос должен вернуть статус 200"

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)


@pytest.mark.asyncio
async def test_invalid_token_history(make_get_http_request, make_post_http_request, user_registration_data,
                                     db_connection, valid_user_credentials):
    await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )
    status, body = await make_post_http_request(
        endpoint='auth/login',
        params=valid_user_credentials,
    )
    invalid_access_token = body['access_token'][:-1] + 'бамбуча'
    headers = {
        "access-token": f"{invalid_access_token}"
    }
    status, body = await make_get_http_request(
        endpoint='auth/history',
        headers=headers,
    )
    assert status == HTTPStatus.UNAUTHORIZED, "Использование недействительного токена должно вернуть статус 401"
    assert body['detail'] == "Invalid token"

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)


@pytest.mark.asyncio
async def test_missing_token_history(make_get_http_request):
    status, body = await make_get_http_request(
        endpoint='auth/history',
    )
    assert status == HTTPStatus.UNAUTHORIZED, "Отсутствие токена должно вернуть статус 401"


@pytest.mark.asyncio
async def test_succesful_token_refresh(make_post_http_request, user_registration_data, valid_user_credentials, db_connection):
    await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )
    status, body = await make_post_http_request(
        endpoint='auth/login',
        params=valid_user_credentials,
    )

    valid_refresh_token = body['refresh_token']

    headers = {
        "refresh-token": f"{valid_refresh_token}"
    }
    status, body = await make_post_http_request(
        endpoint='auth/token/refresh',
        headers=headers,
    )
    assert status == HTTPStatus.OK, "Успешный запрос должен вернуть статус 200"
    assert "access_token" in body, "Ответ должен содержать access_token"
    assert "refresh_token" in body, "Ответ должен содержать refresh_token"

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)


@pytest.mark.asyncio
async def test_unsuccesful_token_refresh(make_post_http_request, user_registration_data, db_connection, valid_user_credentials):
    await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )
    status, body = await make_post_http_request(
        endpoint='auth/login',
        params=valid_user_credentials,
    )
    invalid_refresh_token = body['refresh_token'][:-1] + 'бамбуча'

    headers = {
        "refresh-token": f"{invalid_refresh_token}"
    }
    status, body = await make_post_http_request(
        endpoint='auth/token/refresh',
        headers=headers,
    )
    assert status == HTTPStatus.UNAUTHORIZED, "Успешный запрос должен вернуть статус 200"

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)


@pytest.mark.asyncio
async def test_missed_token_refresh(make_post_http_request):
    status, body = await make_post_http_request(
        endpoint='auth/token/refresh',
    )
    assert status == HTTPStatus.UNAUTHORIZED, "Успешный запрос должен вернуть статус 200"


@pytest.mark.asyncio
async def test_succesful_logout(make_post_http_request, user_registration_data, db_connection, valid_user_credentials):
    await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )
    status, body = await make_post_http_request(
        endpoint='auth/login',
        params=valid_user_credentials,
    )
    valid_access_token = body['access_token']

    headers = {
        "access-token": f"{valid_access_token}"
    }
    status, body = await make_post_http_request(
        endpoint='auth/logout',
        headers=headers,
    )
    assert status == HTTPStatus.OK, "Успешный запрос должен вернуть статус 200"

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)


@pytest.fixture
def user_expired_token_data():
    return {
        "access-token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJrYXJpbWpvbiIsImlhdCI6MTcxNTE3OTkxMiwibmJmIjoxNzE1MTc5OTEyLCJqdGkiOiJkN2NhMDA1Yi0xYWYwLTQ2ZTctYmY3Yy02ZGY2MzQ0OGFiNGEiLCJleHAiOjE3MTUxODM1MTIsInR5cGUiOiJhY2Nlc3MiLCJmcmVzaCI6ZmFsc2UsInJvbGUiOltdfQ.51GrTtbTr7SDHp1NDSu2Jr3s1lVG80imEljETz0yK-U"}

@pytest.mark.asyncio
async def test_succesful_logout_with_expired_token(redis_get, redis_del, make_post_http_request, user_registration_data,
                                                   db_connection, user_expired_token_data):
    await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )
    expired_access_token = user_expired_token_data['access-token']

    headers = {
        "access-token": f"{expired_access_token}"
    }
    status, body = await make_post_http_request(
        endpoint='auth/logout',
        headers=headers,
    )
    assert status == HTTPStatus.OK, "Успешный запрос должен вернуть статус 200"
    redis_token_check = await redis_get(expired_access_token)
    assert redis_token_check is not None
    await redis_del(expired_access_token)

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)


@pytest.mark.asyncio
async def test_unsuccesful_logout(make_post_http_request, user_registration_data, db_connection, valid_user_credentials):
    await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )
    status, body = await make_post_http_request(
        endpoint='auth/login',
        params=valid_user_credentials,
    )
    invalid_refresh_token = body['access_token'][:-1] + 'бамбуча'

    headers = {
        "access-token": f"{invalid_refresh_token}"
    }
    status, body = await make_post_http_request(
        endpoint='auth/logout',
        headers=headers,
    )
    assert status == HTTPStatus.OK, "Успешный запрос должен вернуть статус 401"

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)


@pytest.mark.asyncio
async def test_missed_token_logout(make_delete_http_request):
    status, body = await make_delete_http_request(
        endpoint='auth/logout',
    )
    assert status == HTTPStatus.UNAUTHORIZED, "Успешный запрос должен вернуть статус 200"


@pytest.mark.asyncio
async def test_succesful_logout_all(
    make_post_http_request,
    make_delete_http_request,
    user_registration_data,
    db_connection,
    valid_user_credentials
):
    await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )

    for i in range(0, 5):
        status, body = await make_post_http_request(
            endpoint='auth/login',
            params=valid_user_credentials,
        )
        valid_access_token = body['access_token']
    headers = {
        "access-token": f"{valid_access_token}"
    }
    status, body = await make_delete_http_request(
        endpoint='auth/logout_all',
        headers=headers,
    )
    assert status == HTTPStatus.OK, "Успешный запрос должен вернуть статус 200"

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)


@pytest.mark.asyncio
async def test_missed_token_logout_all(make_delete_http_request):
    status, body = await make_delete_http_request(
        endpoint='auth/logout_all',
    )
    assert status == HTTPStatus.UNAUTHORIZED, "Успешный запрос должен вернуть статус 401"


@pytest.mark.asyncio
async def test_unsuccesful_logout_all_with_expired_token(
    redis_get,
    redis_del,
    make_post_http_request,
    make_delete_http_request,
    user_expired_token_data,
    user_registration_data,
    db_connection
):
    await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )
    expired_access_token = user_expired_token_data['access-token']

    headers = {
        "access-token": f"{expired_access_token}"
    }
    status, body = await make_delete_http_request(
        endpoint='auth/logout_all',
        headers=headers,
    )
    assert status == HTTPStatus.UNAUTHORIZED, "Успешный запрос должен вернуть статус 401"
    redis_token_check = await redis_get(expired_access_token)
    assert redis_token_check is not None
    await redis_del(expired_access_token)

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)


@pytest.mark.asyncio
async def test_successful_validate(make_post_http_request, user_registration_data, db_connection,valid_user_credentials):
    await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )
    status, body = await make_post_http_request(
        endpoint='auth/login',
        params=valid_user_credentials,
    )
    valid_access_token = body['access_token']

    headers = {
        "access-token": f"{valid_access_token}"
    }
    status, body = await make_post_http_request(
        endpoint='auth/token/validate',
        headers=headers,
    )
    assert status == HTTPStatus.OK, "Успешный запрос должен вернуть статус 200"

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)


@pytest.mark.asyncio
async def test_invalid_token_validate(make_post_http_request, user_registration_data, db_connection,valid_user_credentials):
    await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )
    status, body = await make_post_http_request(
        endpoint='auth/login',
        params=valid_user_credentials,
    )
    invalid_access_token = body['access_token'][:-1] + 'бамбуча'
    headers = {
        "access-token": f"{invalid_access_token}"
    }
    status, body = await make_post_http_request(
        endpoint='auth/token/validate',
        headers=headers,
    )
    assert status == HTTPStatus.UNAUTHORIZED, "Использование недействительного токена должно вернуть статус 401"

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)


@pytest.mark.asyncio
async def test_missing_token_validate(make_post_http_request):
    status, body = await make_post_http_request(
        endpoint='auth/token/validate',
    )
    assert status == HTTPStatus.UNAUTHORIZED, "Отсутствие токена должно вернуть статус 401"


@pytest.fixture
def user_pass_credentials():
    return {
        "email": "karimjon@mail.com",
        "old_password": "inshala",
        "new_password": "salamolekyla",
    }


@pytest.mark.asyncio
async def test_successful_pass_change(make_patch_http_request, make_post_http_request, user_registration_data,
                                      user_pass_credentials, db_connection):
    status, body = await make_post_http_request(
        endpoint='auth/register',
        params=user_registration_data,
    )

    status, body = await make_patch_http_request(
        endpoint='auth/password_change',
        json_data=user_pass_credentials,
    )
    assert status == HTTPStatus.OK, "Успешный запрос должен вернуть статус 200"

    login = user_registration_data["login"]
    await clear_user_data(db_connection, login)
