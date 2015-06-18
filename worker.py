import os

import redis
from rq import Worker, Queue, Connection

from app import make_redis

redis_addr = os.environ.get('REDIS_URL', 'localhost')
r = make_redis(redis_addr)

listen = ['high', 'default', 'low']

if __name__ == '__main__':
    with Connection(r):
        worker = Worker(map(Queue, listen))
        worker.work()