import json
from typing import Dict

import redis
from decouple import config

# Initialize Redis client
redis_client = redis.Redis(host=config('REDIS_HOST'), port=config('REDIS_PORT'), db=0)


def initialize_variables() -> None:
    with open('vars.json', 'r') as file:
        data = json.load(file)
        for key, value in data.items():
            redis_client.set(key, value)


def fetch_variables() -> Dict[str, any]:
    with open('vars.json', 'r') as file:
        data = json.load(file)
    variables = {key: redis_client.get(key).decode('utf-8') for key in data.keys()}
    return variables


def get_variable(key: str) -> str:
    """
    Get a specific variable from Redis.

    :param key: The key of the variable to get.
    """
    return redis_client.get(key).decode('utf-8')


def set_variable(key: str, value: any) -> None:
    """
    Set a specific variable in Redis.

    :param key: The key of the variable to set.
    :param value: The value to set for the variable.
    """
    redis_client.set(key, str(value))


if __name__ == '__main__':
    initialize_variables()
