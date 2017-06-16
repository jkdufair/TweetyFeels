"""Create threads to ingest tweets and financial data"""

from concurrent.futures import ThreadPoolExecutor
import twitter


def start():
    """Kick off ingestion process"""
    tweet_counter = twitter.TweetCounter()
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(twitter.stream_tweets, ['bitcoin'], tweet_counter)
        executor.submit(twitter.write_statuses_from_buffer)
        executor.submit(twitter.monitor_status, tweet_counter)


start()
