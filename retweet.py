#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 17:10:23 2020
@author: @MaryNewsWeb
"""
import tweepy
import time
import random
import argparse


# API configuration

CONSUMER_KEY = 'xxxxxxxxxxxxxxxx'
CONSUMER_SECRET = 'xxxxxxxxxxxxxxxxxxxx'
ACCESS_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
ACCESS_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'


# Variables definition --------------------------------------

# max 5 minutes rate limit
# See docs at: https://developer.twitter.com/ja/docs/basics/rate-limits
api_rate_limit = 5*60

# messages for retweeting
random_messages = [
    ' esempio tweet ',
    ' #iGattiniOdianoSalvini https://imgur.com/0ZlAC0P',
    ' https://imgur.com/miOWDkq',
    ' #iGattiniOdianoSalvini https://imgur.com/0ZlAC0P'
]

# storage for the last processed id
STORAGE_PATH = 'last_seen_id.txt'


# Functions definition --------------------------------------

def fetch_trend_names():
    api_response = api.trends_place(id=woeid)
    trends = api_response[0]['trends']
    # to debug response format: ``import json`` + ``print(json.dumps(trends))``
    trend_names = []
    for trend in trends:
        # print(trend)
        trend_names.append(trend['name'])


def get_random_message():
    random.choice(random_messages)


def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id


def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return


def reply():
    print("replying ...")
    last_seen_id = retrieve_last_seen_id(STORAGE_PATH)
    mentions = api.mentions_timeline(last_seen_id)

    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.text)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, STORAGE_PATH)
        if search_text in mention.text.lower():
            print('found "' + search_text + '". responding back ...')
            status_text = '@{mention.user.screen_name} ' + get_random_message()
            status_text += get_random_trendname()
            # api.update_status(status_text, mention.id)
            # api.retweet(mention.id)


# run program --------------------------------------

# resolve script arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    '--search',
    dest='search_text',
    default='#spininelfianco'
)
parser.add_argument(
    '--trend-woeid',
    dest='trend_woeid',
    default='721943'    # ROME
)
args = parser.parse_args()

# assign script arguments
search_text = args.search_text
woeid = args.trend_woeid


print("start replying tweets containing \"" + search_text + "\" ...")

# API authentication

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(
    auth,
    retry_count = 5,
    retry_delay = 10,
    retry_errors = set([401, 404, 500, 503]),
    wait_on_rate_limit = True,
    wait_on_rate_limit_notify = True,
)


# fetching the trends names
print('fetch latest trends ...')
trend_names = fetch_trend_names()

# pool
while True:
    reply()
    time.sleep(api_rate_limit)
