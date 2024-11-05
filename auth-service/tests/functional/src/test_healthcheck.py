from http import HTTPStatus

import pytest


@pytest.mark.parametrize("expected_answer", [({"status": HTTPStatus.OK})])
async def test_healthcheck(make_get_http_request, expected_answer):
    status, body = await make_get_http_request(endpoint="healthcheck", params=None)
    assert status == expected_answer["status"]
