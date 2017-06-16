"""
Get bitcoin prices
This module buffers the bitcoin data and writes in bursts so it doesn't keep the file
open indefinitely, allowing for sync via dropbox/iCloud/etc.
"""

import json
import ssl
import csv
import time
from collections import deque
import urllib.request

BITCOIN_DATA_QUEUE = deque()
STATS = {'count': 0}


def get_bitcoin_data():
    """Get price and volume, etc. from Cryptonator API"""
    url = 'https://api.cryptonator.com/api/ticker/btc-usd'
    fix_this_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request, context=fix_this_context).read()
    STATS['count'] = STATS['count'] + 1
    return json.loads(response.decode('utf-8'))


def queue_bitcoin_data(bitcoin_data):
    """Queue the bitcoin data for writing later"""
    processed_bitcoin_data = {
        'price': bitcoin_data['ticker']['price'],
        'volume': bitcoin_data['ticker']['volume'],
        'timestamp': bitcoin_data['timestamp']
    }
    BITCOIN_DATA_QUEUE.append(processed_bitcoin_data)


def write_bitcoin_data_from_buffer():
    """Take the status objects from the bitcoin data buffer and append them to the csv"""
    print('bitcoin write_bitcoin_data_from_buffer() started')
    while True:
        time.sleep(60)
        with open('data/bitcoin_stream.csv', 'a') as csv_file:
            field_names = ['price', 'volume', 'timestamp']
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            while BITCOIN_DATA_QUEUE:
                bitcoin_data = BITCOIN_DATA_QUEUE.popleft()
                writer.writerow(bitcoin_data)


def stream_bitcoin_data():
    """Poll the bitcoin data every 60 seconds and persist"""
    print('bitcoin stream_bitcoin_data() started')
    while True:
        queue_bitcoin_data(get_bitcoin_data())
        time.sleep(60)


def get_stats():
    """Return statistics about counts and buffer size"""
    return {
        'count': STATS['count'],
        'buffer_size': len(BITCOIN_DATA_QUEUE)
    }
