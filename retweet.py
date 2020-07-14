#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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


CONFIG_DIR = 'config/'
# storage for the last processed id & messages for the retweets.
# location is under CONFIG_PATH.
STORAGE_FILENAME = 'last_seen_id.txt'
RETWEETS_FILENAME = 'retweet_messages.txt'


# Functions definition --------------------------------------

def load_retweet_messages():
    with open(CONFIG_DIR + RETWEETS_FILENAME) as filehandler:
        retweet_messages = []
        # get each line that doesn't start with '//'
        for line in filehandler:
            line = line.strip()
            if line[0:2] != '//' and line != '':
                retweet_messages.append(line);
    return retweet_messages


def get_random_message():
    return random.choice(retweet_messages)


def get_random_trendname():
    return random.choice(localized_trend_names)


def retrieve_last_seen_id():
    f_read = open(CONFIG_DIR + STORAGE_FILENAME, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id


def store_last_seen_id(last_seen_id):
    f_write = open(CONFIG_DIR + STORAGE_FILENAME, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return


def reply(search_text, last_mention_id):
    last_mention_id = last_mention_id if last_mention_id is not None else retrieve_last_seen_id()
    print(f"find mentions (from ID: {last_mention_id}) and reply ...")
    mentions = api_fetch_mentions(last_mention_id)

    if len(mentions) == 0:
        print('no mentions found.')
    for mention in reversed(mentions):
        store_last_seen_id(mention.id)
        if search_text in mention.text.lower():
            print(format('OKBLUE', str(mention.id) + ' - ' + mention.text))
            print(f"found '" + format('BOLD', search_text) + "'. responding back ...")
            status_text = '@{mention.user.screen_name} ' + get_random_message()
            status_text += ' [trend: ' + get_random_trendname() + ']'
            api_retweet(status_text, mention)    # retweet
    print('next check in ' + str(api_rate_limit) + ' seconds')


# text formatting
def format(type, text):
    formats = {
        'HEADER': '\033[95m',
        'OKBLUE': '\033[94m',
        'OKGREEN': '\033[92m',
        'WARNING': '\033[93m',
        'FAIL': '\033[91m',
        'ENDC': '\033[0m',
        'BOLD': '\033[1m'
    }
    return formats.get(type) + text + formats.get('ENDC')


# Twitter API Functions definition --------------------------------------

# print a failure message relative to API call; does not rais any exception
def api_error(message):
    print(format('FAIL', 'API ERROR: ' + message))


# print a success message relative to API call
def api_msg(message):
    print(format('OKGREEN', 'API: ') + message)


def fetch_trend_names():
    api_response = api.trends_place(id=woeid)
    trends = api_response[0]['trends']
    # to debug response format: ``import json`` + ``print(json.dumps(trends))``
    localized_trend_names = []
    for trend in trends:
        localized_trend_names.append(trend['name'])
    return localized_trend_names


def api_fetch_mentions(last_seen_id):
    mentions = []   # in case api call fails
    try:
        mentions = api.mentions_timeline(last_seen_id)
    except tweepy.error.TweepError as err:
        api_error('cannot fetch mentions: ' + str(err))
    return mentions


def api_retweet(status_text, mention, dryrun):
    if not dryrun:
        try:
            api.update_status(status_text, mention.id)
            api.retweet(mention.id)
        except tweepy.error.TweepError as err:
            api_error('cannot retweet: ' + str(err))
    else:
        print(format('WARNING', 'API WOULD:') + ' update the status with "' + status_text + '"')
        print(format('WARNING', 'API WOULD:') + ' retweet to ' + mention.user.screen_name + '')


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
    default='721943'    # WOEID for ROME
)
parser.add_argument(
    '--dry-run',
    type=bool,
    dest='dry_run',
    default='true'
)
parser.add_argument(
    '--last-mention-id',
    type=int,
    dest='last_mention_id',
    default=None
)
args = parser.parse_args()

# assign script arguments
search_text = args.search_text
woeid = args.trend_woeid
dryrun = args.dry_run
last_mention_id = args.last_mention_id


if dryrun:
    print(format('WARNING', 'Running in dry-run mode: no write operation will be performed.'))
print("start replying tweets containing \"" + format('BOLD', search_text) + "\" ...")

# API authentication

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(
    auth,
    retry_count=5,
    retry_delay=10,
    retry_errors=set([401, 404, 500, 503]),
    wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True,
)


# fetching the trends names
api_msg('fetch latest trends')
localized_trend_names = fetch_trend_names()

# load the messages for the retweets
retweet_messages = load_retweet_messages()

# pool requests
while True:
    reply(search_text, last_mention_id)
    time.sleep(api_rate_limit)
