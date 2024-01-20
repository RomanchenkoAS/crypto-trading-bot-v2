import json

import redis

r = redis.Redis(host='localhost', port=6379, db=0)


def initialize_vars():
    with open('vars.json', 'r') as file:
        data = json.load(file)
        for key, value in data.items():
            r.set(key, value)
