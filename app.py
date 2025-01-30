 
import tweepy
from flask import Flask, jsonify

import sqlite3
from datetime import datetime
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# Twitter API Credentials (Replace with your keys)
API_KEY = "jMyoIJAMdl6ht5j5eR0fBgHhy"
API_SECRET_KEY = "GpipECK8cY89xVmk3ACjYW7be1gGmngu90Yga0g01ZErwriVAH"
ACCESS_TOKEN = "273743541-YwcQtNefysr28qOBnR2pexm3inMVz45weChH5raj"
ACCESS_TOKEN_SECRET = "xNq3J30MDd0iWT81KXz1KvTBGogHIAfE5lfEwwOUZLieU"

# Database file
DB_PATH = "tweets.db"

# Twitter Accounts to Monitor
ACCOUNTS = ["QuiverQuant", "InsiderRadar", "PelosiTracker_"]  # Replace with actual Twitter handles

# Authenticate Twitter API
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

import requests

def fetch_and_store_tweets():
    """Fetch tweets from Twitter API v2 and store in SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS tweets (id INTEGER PRIMARY KEY, account TEXT, tweet TEXT, timestamp TEXT)"
    )

    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAADlaygEAAAAA494OrE2CVQe3AVqGZEhslKhoaRE%3DNAGgrV1qCscihRRoGhqfqk38e5STxJZz8TMlsq3U4NnbFNXKyS"  # Replace with your actual Twitter API v2 Bearer Token

    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

    for account in ACCOUNTS:
        url = f"https://api.twitter.com/2/users/by/username/{account}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data["data"]["id"]
            timeline_url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=5"

            tweet_response = requests.get(timeline_url, headers=headers)

            if tweet_response.status_code == 200:
                tweets = tweet_response.json().get("data", [])
                for tweet in tweets:
                    cursor.execute(
                        "INSERT INTO tweets (account, tweet, timestamp) VALUES (?, ?, ?)",
                        (account, tweet["text"], datetime.now().isoformat()),
                    )

    conn.commit()
    conn.close()

@app.route("/tweets", methods=["GET"])
def get_tweets():
    """Retrieve tweets from the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT account, tweet, timestamp FROM tweets ORDER BY timestamp DESC LIMIT 20")
    tweets = cursor.fetchall()
    conn.close()

    return jsonify([{"account": row[0], "tweet": row[1], "timestamp": row[2]} for row in tweets])

@app.route("/fetch", methods=["GET"])
def fetch_tweets_endpoint():
    """Trigger tweet fetching manually"""
    fetch_and_store_tweets()
    return "Tweets fetched and stored!"

if __name__ == "__main__":
    fetch_and_store_tweets()  # Fetch tweets once at startup
    app.run(debug=True)
