import unittest

import aiohttp


class TestChatCompletion(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.url = "http://assistant_service:8000/api/v1/chat/completion"

    async def test_completion_valid_request(self):
        headers = {'Content-Type': 'application/json'}
        data = {
            "role": "user",
            "content": "Привет!"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=headers, json=data) as response:
                self.assertEqual(response.status, 200)
                content = await response.json()
                self.assertIn("messages", content)
                self.assertEqual(len(content["messages"]), 2)
                self.assertEqual(content["messages"][0]["role"], "user")
                self.assertEqual(content["messages"][0]["content"], "Привет!")
                self.assertEqual(content["messages"][1]["role"], "assistant")
                self.assertTrue(len(content["messages"][1]["content"]) > 0)

    async def test_completion_invalid_request(self):
        headers = {'Content-Type': 'application/json'}
        data = {
            "role": "user",
            "content": ""
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=headers, json=data) as response:
                self.assertEqual(response.status, 422)

    async def test_completion_invalid_role(self):
        headers = {'Content-Type': 'application/json'}
        data = {
            "role": "invalid_role",
            "content": "Some content"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=headers, json=data) as response:
                self.assertEqual(response.status, 422)
