from http import HTTPStatus

import pytest


@pytest.fixture
def role_data():
    return {
        "name": "bruce",
        "description": "vsemogushiy",
    }


@pytest.fixture
def role_data2():
    return {
        "name": "bruce2",
        "description": "vsemogushiy2",
    }


@pytest.fixture
def role_data3():
    return {
        "name": "bruce3",
        "description": "vsemogushiy3",
    }


@pytest.fixture
def admin_creds():
    return {
        "login": "admin",
        "password": "1234",
    }


@pytest.fixture
def create_role(make_post_http_request, db_connection, admin_creds):
    async def _create_role(role_data):
        status, body = await make_post_http_request(
            endpoint="auth/login",
            params=admin_creds,
        )
        assert status == HTTPStatus.OK
        access_token = body["access_token"]
        headers = {"access-token": f"{access_token}"}
        status, body = await make_post_http_request(
            endpoint="roles", params=role_data, headers=headers
        )
        assert status == HTTPStatus.CREATED, "Role creation failed"
        query = "SELECT * FROM public.roles WHERE name = $1"
        name = role_data["name"]
        role = await db_connection.fetchrow(query, name)
        assert role is not None, f"Role with name '{name}' not found"
        return role

    return _create_role


@pytest.fixture
def cleanup_role(db_connection):
    async def _cleanup_role(role_id):
        await db_connection.execute("DELETE FROM public.roles WHERE id = $1", role_id)

    return _cleanup_role


@pytest.mark.asyncio
async def test_succesful_role_creation(create_role, cleanup_role, role_data):
    role = await create_role(role_data)
    role_id = role["id"]
    assert role["name"] == role_data["name"]
    await cleanup_role(role_id)


@pytest.fixture
async def login_as_admin(make_post_http_request, admin_creds):
    status, body = await make_post_http_request(
        endpoint="auth/login",
        params=admin_creds,
    )
    assert status == HTTPStatus.OK
    access_token = body["access_token"]

    return access_token


@pytest.mark.asyncio
async def test_role_creation_conflict(
    make_post_http_request,
    create_role,
    cleanup_role,
    role_data,
    admin_creds,
    login_as_admin,
):
    role = await create_role(role_data)
    role_id = role["id"]

    access_token = login_as_admin
    headers = {"access-token": f"{access_token}"}
    status, body = await make_post_http_request(
        endpoint="roles", params=role_data, headers=headers
    )
    assert status == HTTPStatus.CONFLICT, "Expected HTTP 409 CONFLICT"

    await cleanup_role(role_id)


@pytest.mark.asyncio
async def test_read_roles(
    make_get_http_request, create_role, cleanup_role, role_data, role_data2, role_data3
):
    role1 = await create_role(role_data)
    role2 = await create_role(role_data2)
    role3 = await create_role(role_data3)

    status, body = await make_get_http_request(endpoint="roles/")
    assert status == HTTPStatus.OK, "Expected HTTP 200 OK"
    assert (
        len(body) == 5
    ), "Expected three roles in response, 3 created 2 admin and guest"

    await cleanup_role(role1["id"])
    await cleanup_role(role2["id"])
    await cleanup_role(role3["id"])


@pytest.mark.asyncio
async def test_read_role(make_get_http_request, create_role, cleanup_role, role_data):
    role = await create_role(role_data)
    role_id = role["id"]

    status, body = await make_get_http_request(endpoint=f'roles/{role_data["name"]}')
    assert status == HTTPStatus.OK, "Expected HTTP 200 OK"

    await cleanup_role(role_id)


@pytest.mark.asyncio
async def test_update_role(
    make_put_http_request,
    create_role,
    cleanup_role,
    role_data,
    role_data2,
    login_as_admin,
):
    role = await create_role(role_data)
    role_id = role["id"]
    access_token = login_as_admin
    headers = {"access-token": f"{access_token}"}
    status, body = await make_put_http_request(
        endpoint="roles/update/",
        json_data={"name": role_data["name"], "description": role_data2["description"]},
        headers=headers,
    )
    assert status == HTTPStatus.OK, "Expected HTTP 200 OK"

    await cleanup_role(role_id)


@pytest.mark.asyncio
async def test_delete_role(
    make_delete_http_request, create_role, cleanup_role, role_data, login_as_admin
):
    role = await create_role(role_data)
    role_id = role["id"]
    access_token = login_as_admin
    headers = {"access-token": f"{access_token}"}
    status, body = await make_delete_http_request(
        endpoint=f'roles/{role_data["name"]}', headers=headers
    )
    assert status == HTTPStatus.OK, "Expected HTTP 200 OK"

    await cleanup_role(role_id)


@pytest.mark.asyncio
async def test_read_role_404(
    make_get_http_request, create_role, cleanup_role, role_data
):
    role = await create_role(role_data)
    role_id = role["id"]

    status, body = await make_get_http_request(endpoint="roles/fake_role")
    assert status == HTTPStatus.NOT_FOUND, "Expected HTTP 404 NOT FOUND"

    await cleanup_role(role_id)


@pytest.fixture
def assign_role():
    return {
        "user_name": "admin",
        "role_name": "bruce",
    }


@pytest.mark.asyncio
async def test_assign_role(
    make_post_http_request,
    create_role,
    role_data,
    admin_creds,
    login_as_admin,
    assign_role,
):
    await create_role(role_data)

    access_token = login_as_admin
    headers = {"access-token": f"{access_token}"}
    status, body = await make_post_http_request(
        endpoint="roles/assign", params=assign_role, headers=headers
    )
    assert status == HTTPStatus.OK, "Expected HTTP 200 OK"


@pytest.mark.asyncio
async def test_revoke_role(
    make_post_http_request, role_data, admin_creds, login_as_admin, assign_role
):
    access_token = login_as_admin
    headers = {"access-token": f"{access_token}"}
    status, body = await make_post_http_request(
        endpoint="roles/revoke", params=assign_role, headers=headers
    )
    assert status == HTTPStatus.OK, "Expected HTTP 200 OK"
