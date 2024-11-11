import os
import sys
import unittest
from unittest.mock import AsyncMock, patch

from src.services.factory import get_llm_service
from src.services.openai import OpenAIService

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

class TestOpenAIService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.api_key = ""
        self.base_url = ""
        self.service = OpenAIService(self.api_key, self.base_url)
        self.model_name = "gpt-4o-mini"
        self.system_prompt = "test_system_prompt"
        self.max_tokens = 100
        self.messages = [{"role": "user", "content": "test_message"}]

    def test_prepare_headers(self):
        expected_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.assertEqual(self.service.prepare_headers(), expected_headers)

    def test_prepare_messages_with_system_prompt(self):
        expected_messages = [
            {"role": "system", "content": self.system_prompt},
            *self.messages
        ]
        self.assertEqual(
            self.service.prepare_messages(self.system_prompt, self.messages),
            expected_messages
        )

    def test_prepare_messages_without_system_prompt(self):
        self.assertEqual(
            self.service.prepare_messages("", self.messages), self.messages
        )

    def test_prepare_data(self):
        expected_data = {
            "model": self.model_name,
            "messages": self.service.prepare_messages(self.system_prompt, self.messages),
            "max_tokens": self.max_tokens
        }
        self.assertEqual(
            self.service.prepare_data(
                self.model_name, self.system_prompt, self.max_tokens, self.messages
            ),
            expected_data
        )

    @patch("src.services.openai.send_post")
    async def test_send_post(self, mock_send_post):
        mock_response = (200, {"test": "data"})
        mock_send_post.return_value = mock_response
        data = {"key": "value"}
        headers = {"header": "value"}
        status_code, response = await self.service.send_post(data, headers)
        self.assertEqual(status_code, 200)
        self.assertEqual(response, {"test": "data"})
        mock_send_post.assert_awaited_once_with(
            self.base_url, data, headers
        )


    def test_get_reply(self):
        response = {"choices": [{"message": {"content": "test_reply"}}]}
        self.assertEqual(self.service.get_reply(response), "test_reply")

    def test_get_reply_key_error(self):
        response = {"incorrect_key": "value"}
        with self.assertRaises(ValueError):
            self.service.get_reply(response)

    def test_get_reply_index_error(self):
        response = {"choices": []}
        with self.assertRaises(ValueError):
            self.service.get_reply(response)

    @patch("src.services.factory.OpenAIService")
    async def test_get_llm_service_openai(self, mock_openai_service):
        mock_openai_service.return_value = AsyncMock()
        service = get_llm_service("OPENAI")
        self.assertIsInstance(service, AsyncMock)  # Or check for specific mock type

    @patch("src.services.factory.OpenAIService")
    async def test_get_llm_service_proxyapi(self, mock_openai_service):
        mock_openai_service.return_value = AsyncMock()
        service = get_llm_service("PROXYAPI")
        self.assertIsInstance(service, AsyncMock)

    async def test_get_llm_service_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            get_llm_service("unsupported_service")



if __name__ == '__main__':
    unittest.main()
