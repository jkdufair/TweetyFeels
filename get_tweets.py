import pickle
import webbrowser
import os.path
import csv
import tweepy

def get_token():
	if os.path.exists(".token"):
		the_file = open(".token", "r")
		return pickle.load(the_file)
	else:
			return

def persist_token(token):
	the_file = open(".token", "w")
	pickle.dump(token, the_file)

def authenticate():
	consumer_key = 'aN6bbamocujBEQkTsT4V5Ok36'
	consumer_secret = '5LgoByRZxcQYIW4rumrclYfHqEFUCO5SnYrNFz6O0LyprOvpPs'
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	access_token = get_token()
	if access_token is None:
		webbrowser.open(auth.get_authorization_url())
		pin = raw_input('Verification pin number from twitter.com: ').strip()
		access_token = auth.get_access_token(verifier=pin)
		persist_token(access_token)
	auth.set_access_token(access_token[0], access_token[1])
	return auth

def get_tweets():
	auth = authenticate()
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

	with open('tweets.csv', 'w') as csvfile:
		field_names = ['created_at', 'text', 'user_id', 'id']
		writer = csv.DictWriter(csvfile, fieldnames=field_names)
		writer.writeheader()

		for tweet in tweepy.Cursor(api.search,
				q="bitcoin since:2017-06-11",
				rpp=100,
				result_type="recent",
				include_entities=False,
				lang="en").items():
			writer.writerow({'created_at': tweet.created_at, 'text': tweet.text.encode('utf-8'), 'user_id': tweet.user.id,
				'id': tweet.id})

get_tweets()
