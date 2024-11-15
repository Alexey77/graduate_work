import asyncio
import logging
import random
import time

import aiohttp


async def fetch(session, url, headers):
    start_time = time.time()
    async with session.get(url, headers=headers) as response:
        end_time = time.time()
        response_time = end_time - start_time
        status_code = response.status
        return status_code, response_time


async def generate_random_headers(user_id):
    random_ip = f"192.168.1.{random.randint(1, 255)}"
    random_user_agent = f"TestAgent/{random.randint(1, 1000)}.{random.randint(1, 1000)}"
    return {
        'X-Forwarded-For': random_ip,
        'User-Agent': random_user_agent,
        'X-User-ID': f"user_{user_id}"
    }


async def make_requests(url, num_users, num_requests_per_user):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for user_id in range(1, num_users + 1):
            for _ in range(num_requests_per_user):
                headers = await generate_random_headers(user_id)
                task = asyncio.ensure_future(fetch(session, url, headers))
                tasks.append(task)
        responses = await asyncio.gather(*tasks)
        for status_code, response_time in responses:
            logging.info(f"Response Status: {status_code}, User ID:{user_id}, Response Time: {response_time:.4f} sec User: {headers['X-Forwarded-For']}")


if __name__ == "__main__":
    url = "http://localhost:81/api/auth/health/v1/healthz/live"

    num_users = 1  # Количество различных пользователей
    num_requests_per_user = 10_000  # Количество запросов от каждого пользователя

    loop = asyncio.get_event_loop()
    loop.run_until_complete(make_requests(url, num_users, num_requests_per_user))
