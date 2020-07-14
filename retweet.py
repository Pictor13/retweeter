#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import tweepy
import time
import random
import argparse
import yaml

#
# Variables definition --------------------------------------
#

# max 5 minutes rate limit
# See docs at: https://developer.twitter.com/ja/docs/basics/rate-limits
API_RATE_LIMIT = 5*60
# storage filename for the last processed id
CONFIG_FILENAME = 'config.yaml'
MENTION_ID_FILENAME = 'last_seen_id'
VAR_DIR = 'var'
# value to initialize the last seen mention id
DEFAULT_MENTION_ID = 1


#
# Functions definition --------------------------------------
#

def reply(search_text, last_mention_id):
    search_text_lower = search_text.lower()
    last_mention_id = last_mention_id if last_mention_id is not None else retrieve_last_seen_id()
    print(F"find mentions (from ID: {last_mention_id}) and reply ...")  # F is for formatted-string-literals
    mentions = api_fetch_mentions(last_mention_id)

    if len(mentions) == 0:
        print('no mentions found.')
    for mention in reversed(mentions):
        store_last_seen_id(mention.id)
        # print(mention.text)
        if search_text_lower in mention.text.lower():
            print(
                "found \"" + format('BOLD', search_text) + "\" into mention: "
                + format('OKBLUE', str(mention.id) + ' - ' + mention.text)
                + ". responding back ..."
            )
            status_text = F"@{mention.user.screen_name} " + get_random_message()  # F is for formatted-string-literals
            status_text += " [trend: " + get_random_trendname() + "]"
            api_retweet(status_text, mention)    # retweet
    print('next check in ' + str(API_RATE_LIMIT) + ' seconds')


def retrieve_last_seen_id():
    try:
        f_handler = open(VAR_DIR + '/' + MENTION_ID_FILENAME, 'r')
    except FileNotFoundError:
        # create default file, if it doesn't exist
        store_last_seen_id(DEFAULT_MENTION_ID)
        f_handler = open(VAR_DIR + '/' + MENTION_ID_FILENAME, 'r')
    # get integer value from the first line of the file
    last_seen_id = int(f_handler.read().strip())
    f_handler.close()
    return last_seen_id


def store_last_seen_id(last_seen_id):
    f_write = open(VAR_DIR + '/' + MENTION_ID_FILENAME, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return f_write


def get_random_message():
    return random.choice(retweet_messages)


def get_random_trendname():
    return random.choice(localized_trend_names)


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


# convert string argument values to true/false boolean
def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


#
# Twitter API Functions definition --------------------------------------
#

# print a failure message relative to API call; does not rais any exception
def api_error(message):
    print(format('FAIL', 'API ERROR: ' + message))


# print a success message relative to API call
def api_msg(message):
    print(format('OKGREEN', 'API: ') + message)


def fetch_trend_names(woeid):
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


def api_retweet(status_text, mention):
    message = 'retweet to ' + mention.user.screen_name + ' with "' + format('OKBLUE', status_text) + '"'
    if not args.dry_run:
        try:
            api.update_status(status_text, mention.id)
            api.retweet(mention.id)
        except tweepy.error.TweepError as err:
            api_error('cannot retweet: ' + str(err))
        api_msg(message)
    else:
        api_msg(format('WARNING', 'would ') + message)


#
# configure program --------------------------------------
#

# environment & config operations

# get environment variables
envs = os.environ

# make var/ folder
if not os.path.exists(VAR_DIR):
    os.makedirs(VAR_DIR)

# load config file
if not os.path.exists(CONFIG_FILENAME):
    error_msg = "No configuration file. Did you forget to create a copy of '" + CONFIG_FILENAME + ".dist' ?"
    raise FileNotFoundError(error_msg)
with open(CONFIG_FILENAME, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except Exception:
        raise ValueError('The YAML config file is not formatted correctly.')


# resolve script arguments and set defaults
parser = argparse.ArgumentParser()
parser.add_argument(
    '--search',
    dest='search_text',
    default=config['mention']['search']
)
parser.add_argument(
    '--trend-woeid',
    dest='trend_woeid',
    default=config['trend']['woeid']
)
parser.add_argument(
    '--dry-run',
    type=str2bool,
    dest='dry_run',
    default='True'
)
parser.add_argument(
    '--last-mention-id',
    type=int,
    dest='last_mention_id',
    default=None
)
args = parser.parse_args()


# get Twitter API secrets from envrironment variables or from config file
secrets = config['API.Twitter']
secrets['CONSUMER_KEY'] = envs['TWITTER_CONSUMER_KEY'] if 'TWITTER_CONSUMER_KEY' in envs else secrets['CONSUMER_KEY']
secrets['CONSUMER_SECRET'] = envs['TWITTER_CONSUMER_SECRET'] if 'TWITTER_CONSUMER_SECRET' in envs else secrets['CONSUMER_SECRET']
secrets['ACCESS_KEY'] = envs['TWITTER_ACCESS_KEY'] if 'TWITTER_ACCESS_KEY' in envs else secrets['ACCESS_KEY']
secrets['ACCESS_SECRET'] = envs['TWITTER_ACCESS_SECRET'] if 'TWITTER_ACCESS_SECRET' in envs else secrets['ACCESS_SECRET']


#
# run program --------------------------------------
#

if args.dry_run:
    print(format('WARNING', 'Running in dry-run mode: no write operation will be performed.'))
print("start replying tweets containing \"" + format('BOLD', args.search_text) + "\" ...")

# API authentication

auth = tweepy.OAuthHandler(secrets['CONSUMER_KEY'], secrets['CONSUMER_SECRET'])
auth.set_access_token(secrets['ACCESS_KEY'], secrets['ACCESS_SECRET'])
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
localized_trend_names = fetch_trend_names(args.trend_woeid)

# load the messages for the retweets
retweet_messages = config['retweet']['with_messages']
if not isinstance(retweet_messages, list) or len(retweet_messages) == 0:
    raise ValueError('The configured `retweet_messages[]` must be a non-empty list')

# pool requests
while True:
    reply(args.search_text, args.last_mention_id)
    time.sleep(API_RATE_LIMIT)
