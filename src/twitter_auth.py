"""Twitter authentication functions"""

import pickle
import webbrowser
import os.path
import tweepy


def deserialize_token():
    """Get token from file if it exists"""
    if os.path.exists(".token"):
        the_file = open(".token", "rb")
        return pickle.load(the_file)
    else:
        return


def serialize_token(token):
    """Save token to file"""
    the_file = open(".token", "wb")
    pickle.dump(token, the_file)


def authenticate():
    """Create tweepy auth object and return"""
    consumer_key = 'aN6bbamocujBEQkTsT4V5Ok36'
    consumer_secret = '5LgoByRZxcQYIW4rumrclYfHqEFUCO5SnYrNFz6O0LyprOvpPs'
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    # "17417157-dlWa8vJCGGIXtCmvuxNQ3hRYcpCM4YnJWpNvGGLSO"
    access_token = deserialize_token()
    if access_token is None:
        url = auth.get_authorization_url()
        webbrowser.open(url, new=1, autoraise=True)
        pin = input('Verification pin number from twitter.com: ').strip()
        access_token = auth.get_access_token(verifier=pin)
        serialize_token(access_token)
    auth.set_access_token(access_token[0], access_token[1])
    return auth
