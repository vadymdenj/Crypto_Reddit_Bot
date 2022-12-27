# This function contains Python script for the bot that runs on AWS Lambda
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import time
import json
import praw 

# config.py is a file where credentials are stored
import config

# Creating Reddit instance using bot account credentials
def bot_sign_in():
    r = praw.Reddit(username = config.username,
            password = config.password,
            client_id = config.client_id,
            client_secret = config.client_secret,
            user_agent = "console:CryptoPriceBot:v1.0")

    return r

# Searching for a post to reply 
def bot_search(r):
    btc_key = ["btc","bitcoin"]
    action_key = action_words()
    btc_posts = []

    # Looking through top posts for the day 
    for post in r.subreddit("Bitcoin").top(time_filter = "day"):
        btc_mention = False
        action_mention = False
        for i in range(0, len(btc_key)):
            # Looking for bitcoin mentions 
            if (btc_key[i] in post.title.lower() or btc_key[i] in post.selftext.lower()):
                btc_mention = True
            # Looking for action word mentions 
            for j in range (0, len(action_key)):
                if (action_key[j] in post.title.lower() or action_key[j] in post.selftext.lower()):
                    action_mention = True
        # If both mentions occur, the posts are added to the list for further selection 
        if (btc_mention and action_mention):
            btc_posts.append(post)

    # Finding top score daily post from the list of posts with bitcoin and action word mentions
    max_score_post = None
    for post in btc_posts:
        if (max_score_post != None):

            if (post.score > max_score_post.score ):
                max_score_post = post
        else:
                max_score_post = post

    return max_score_post
    
# Replying to the thread with current Bitcoin price
def bot_reply(r):
    max_score_post = bot_search(r)
    # Checking if the top score post exists
    if (max_score_post != None):
        max_score_post.reply("Bitcoin price on the day this thread was made is $" + str(get_price()) +
        ". This was posted as a reference point to any future thread readers. Upvote if useful!")
        print("The bot replied to a post")
    # Otherwise return this message
    else:
        print("No popular daily posts talked about Bitcoin prices today.")

# Retrieving Bitcoin price from CoinMarketCap RESTful API
def get_price():
    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    parameters = {
        'id': 1 # this id number corresponds to Bitcoin price
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': config.crypto_api_key,
    }

    session = Session()
    session.headers.update(headers)
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        # Navigating to the bitcoin price in JSON
        price = data['data']['1']['quote']['USD']['price']
        # Rounding to two decimal places
        price = round(price, 2)

        return price

    except (ConnectionError, Timeout, TooManyRedirects) as error:
        return error

# Pulling list words used to describe price actions
def action_words():
    # Opening the file and making it into a list
    with open("action_words.txt", "r") as file:
        action_key = file.read()
        action_key = action_key.split("\n")

    return action_key
    
# Gathering all elements needed to run the bot and running it
def lambda_handler(event, context):
    r = bot_sign_in()
    bot_reply(r)
    return "Success"