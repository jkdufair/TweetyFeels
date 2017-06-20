"""
Stream tweets and write status
This module buffers the data and writes in bursts so it doesn't keep the file
open indefinitely, allowing for sync via dropbox/iCloud/etc.
"""

import csv
import re
import time
from collections import deque
import tweepy
import twitter_auth


TWEET_QUEUE = deque()
STATS = {'count': 0}


class StreamListener(tweepy.StreamListener):
    """Class to listen for twitter streams and handle them"""

    def __init__(self, writerFunction):
        """Store the function that writes out the tweet data"""
        self.writer = writerFunction
        super(StreamListener, self).__init__()

    def on_status(self, status):
        self.writer(status)
        STATS['count'] = STATS['count'] + 1

    def on_error(self, status_code):
        print("Error: {}".format(status_code))
        if status_code == 420:
            return False


def queue_status(status):
    """Queue the status in the tweet_buffer array for writing later"""
    processed_status = {'created_at': status.created_at,
                        'text': str.lower(
                            re.sub(r'\s+', ' ', status.text.strip())),
                        'user_id': status.user.id,
                        'id': status.id,
                        'source': status.source,
                        'in_reply_to_status_id': status.in_reply_to_status_id,
                        'in_reply_to_user_id': status.in_reply_to_user_id,
                        'in_reply_to_screen_name': status.in_reply_to_screen_name,
                        'is_quote_status': status.is_quote_status,
                        'retweet_count': status.retweet_count,
                        'favorite_count': status.favorite_count,
                        'favorited': status.favorited,
                        'retweeted': status.retweeted}
    TWEET_QUEUE.append(processed_status)


def stream_tweets(keywords):
    """Stream tweets about bitcoin to csv file"""
    print('twitter stream_tweets() started')
    auth = twitter_auth.authenticate()

    listener = StreamListener(queue_status)
    stream = tweepy.Stream(auth=auth, listener=listener)
    stream.filter(track=keywords, async=True)


def write_statuses_from_buffer():
    """Take the status objects from the tweet buffer and append them to the csv"""
    print('twitter write_statuses_from_buffer() started')
    while True:
        time.sleep(60)
        with open('data/tweet_stream.csv', 'a') as csv_file:
            field_names = ['created_at', 'text', 'user_id', 'id',
                           'source', 'in_reply_to_status_id',
                           'in_reply_to_user_id', 'in_reply_to_screen_name',
                           'is_quote_status', 'retweet_count', 'favorite_count',
                           'favorited', 'retweeted']
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            while TWEET_QUEUE:
                writer.writerow(TWEET_QUEUE.popleft())


def get_stats():
    """Return statistics about counts and buffer size"""
    return {
        'count': STATS['count'],
        'buffer_size': len(TWEET_QUEUE)
    }
