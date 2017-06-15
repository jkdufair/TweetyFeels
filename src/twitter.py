"""Functions to fetch or stream tweets"""

import csv
import tweepy
import twitter_auth
import re

tweet_buffer = []


class StreamListener(tweepy.StreamListener):
    """Class to listen for twitter streams and handle them"""

    def __init__(self, writerFunction):
        """Store the function that writes out the tweet data"""
        self.writer = writerFunction
        super(StreamListener, self).__init__()

    def on_status(self, status):
        self.writer(status)

    def on_error(self, status_code):
        if status_code == 420:
            return False


def get_tweets(query):
    """Fetch tweets matching query via twitter API
        query: string
            The Twitter API query
    """
    auth = twitter_auth.authenticate()
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    with open('data/tweets.csv', 'w') as csvfile:
        field_names = ['created_at', 'text', 'user_id', 'id']
        writer = csv.DictWriter(csvfile, fieldnames=field_names)

        for tweet in tweepy.Cursor(api.search,
                                   q=query,
                                   rpp=100,
                                   result_type="recent",
                                   include_entities=False,
                                   lang="en").items():
            writer.writerow({'created_at': tweet.created_at, 'text': tweet.text.encode('utf-8'),
                             'user_id': tweet.user.id, 'id': tweet.id})


def write_status(status, writer):
    """Write the details of the tweet to the csv writer"""
    writer.writerow({'created_at': status.created_at,
                     'text': status.text,
                     'user_id': status.user.id,
                     'id': status.id})


def queue_status(status):
    """Queue the status in the tweet_buffer array for writing later"""
    processed_status = {'created_at': status.created_at,
                        'text': str.lower(
                            re.sub(r'\s+', ' ', status.text.strip())),
                        'user_id': status.user.id,
                        'id': status.id}
    tweet_buffer.append(processed_status)
    print(processed_status)


def stream_tweets(keywords):
    """Stream tweets about bitcoin to csv file"""
    auth = twitter_auth.authenticate()

    # csvfile = open('data/tweet_stream.csv', 'a')
    # field_names = ['created_at', 'text', 'user_id', 'id']
    # writer = csv.DictWriter(csvfile, fieldnames=field_names)

    listener = StreamListener(writerFunction=queue_status)
    stream = tweepy.Stream(auth=auth, listener=listener)
    stream.filter(track=keywords, async=True)


# get_tweets("bitcoin since:2017-06-11 until:2017-06-12")
# executor = ThreadPoolExecutor(max_workers=2)

stream_tweets(['bitcoin'])
