#!/usr/bin/python

import hashlib
import json
import os
import random
import string
import sys

from kafka import KafkaConsumer as Consumer, TopicPartition as Partition
from statsd import StatsClient as Statsd

if __name__ == '__main__':

    state = json.loads(''.join(sys.stdin))
    
    try:

        js = json.loads(os.environ['KONTROL_ANNOTATIONS'])
        broker = random.choice(js['kafka.unity3d.com/brokers'].split(','))
        topic = js['kafka.unity3d.com/topic']
        statsd = Statsd('127.0.0.1', 8125)
        consumer = Consumer(bootstrap_servers=broker)
        partition = Partition(topic, 0)
        consumer.assign([partition])

        if not state['last']:
           
            #
            # - the produce/consume loop has just started
            # - reset to the head
            #
            consumer.seek_to_end()

        else:

            #
            # - start from where we consumed last
            # - read up to N records
            # - make sure the MD5 digests match
            #
            tokens = []
            consumer.seek(partition, state['last'])
            print >> sys.stderr, 'expecting #%d records @ %d' % (state['batch'], state['last'])
            while len(tokens) < state['batch']:
                raw = next(consumer).value
                tokens.append(raw)
    
            hasher = hashlib.md5()
            hasher.update(''.join(tokens))
            md5 = ':'.join(c.encode('hex') for c in hasher.digest())
            assert md5 == state['md5'], 'producer/consumer mismatch (kafka bug ?)'
               
        state['last'] = consumer.position(partition)
           
    finally:
        print json.dumps(state)
