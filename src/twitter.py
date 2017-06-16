"""Stream tweets and write status"""

import csv
import re
import time
from collections import deque
import tweepy
import twitter_auth


TWEET_QUEUE = deque()


class TweetCounter():
    """Class for managing the global tweet count"""

    def __init__(self):
        self.tweet_count = 0

    def increment(self):
        """Bump it up, baby"""
        self.tweet_count = self.tweet_count + 1

    def get_tweet_count(self):
        """Return the tweet count. Duh"""
        return self.tweet_count


class StreamListener(tweepy.StreamListener):
    """Class to listen for twitter streams and handle them"""

    def __init__(self, writerFunction, tweet_counter):
        """Store the function that writes out the tweet data"""
        self.writer = writerFunction
        self.tweet_counter = tweet_counter
        super(StreamListener, self).__init__()

    def on_status(self, status):
        self.writer(status)
        self.tweet_counter.increment()

    def on_error(self, status_code):
        print('hello')
        if status_code == 420:
            return False


def write_status(status, writer):
    """Write the details of the tweet to the csv writer"""
    writer.writerow(status)


def queue_status(status):
    """Queue the status in the tweet_buffer array for writing later"""
    processed_status = {'created_at': status.created_at,
                        'text': str.lower(
                            re.sub(r'\s+', ' ', status.text.strip())),
                        'user_id': status.user.id,
                        'id': status.id}
    TWEET_QUEUE.append(processed_status)


def stream_tweets(keywords, tweet_counter):
    """Stream tweets about bitcoin to csv file"""
    print('stream_tweets() started')
    auth = twitter_auth.authenticate()

    listener = StreamListener(queue_status, tweet_counter)
    stream = tweepy.Stream(auth=auth, listener=listener)
    stream.filter(track=keywords, async=True)


def write_statuses_from_buffer():
    """Take the status objects from the tweet buffer and append them to the csv"""
    print('write_statuses_from_buffer() started')
    while True:
        time.sleep(60)
        with open('data/tweet_stream.csv', 'a') as csv_file:
            field_names = ['created_at', 'text', 'user_id', 'id']
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            while TWEET_QUEUE:
                write_status(TWEET_QUEUE.popleft(), writer)


def monitor_status(tweet_counter):
    """Print a message to the console with queue length and total tweets written"""
    print('monitor_status() started')
    while True:
        time.sleep(1)
        queue_length = len(TWEET_QUEUE)
        print('                                                                ', end='\r')
        print('Queue length: {}\t\tTotal tweets collected: {}'.format(
            queue_length, tweet_counter.get_tweet_count()), end='\r')
