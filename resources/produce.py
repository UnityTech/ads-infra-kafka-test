#!/usr/bin/python

import hashlib
import json
import os
import random
import string
import sys

from kafka import KafkaProducer as Producer
from statsd import StatsClient as Statsd

if __name__ == '__main__':

    state = json.loads(''.join(sys.stdin))

    try:

        js = json.loads(os.environ['KONTROL_ANNOTATIONS'])
        broker = random.choice(js['kafka.unity3d.com/brokers'].split(','))
        topic = js['kafka.unity3d.com/topic']
        statsd = Statsd('127.0.0.1', 8125)
        producer = Producer(bootstrap_servers=broker, compression_type='gzip')

        def _token():
            return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(256))

        N = random.randint(1, 32)
        state['batch'] = N
        tokens = ['%d/%d' % (n, N) for n in range(N)]

        for token in tokens:
            producer.send(topic, token)

        producer.flush()
        hasher = hashlib.md5()
        hasher.update(''.join(tokens))
        state['md5'] = ':'.join(c.encode('hex') for c in hasher.digest())
   
    finally:
        print json.dumps(state)