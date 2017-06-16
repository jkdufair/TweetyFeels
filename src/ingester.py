"""Create threads to ingest tweets and financial data"""

from concurrent.futures import ThreadPoolExecutor
import time
import twitter
import bitcoin


def get_stats():
    """Collect stats from each module and display them"""
    print('stats collector started')
    while True:
        print()
        twitter_stats = twitter.get_stats()
        print('twitter: {}'.format(twitter_stats))
        bitcoin_stats = bitcoin.get_stats()
        print('bitcoin: {}'.format(bitcoin_stats))
        time.sleep(5)


def start():
    """Kick off ingestion process"""
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.submit(twitter.stream_tweets, ['bitcoin'])
        executor.submit(twitter.write_statuses_from_buffer)
        executor.submit(bitcoin.stream_bitcoin_data)
        executor.submit(bitcoin.write_bitcoin_data_from_buffer)
        executor.submit(get_stats)

start()
