# retweeter

Search for Twitter mentions containing a specific string and retweet them with a message (picked randomly from the ```retweet_messages.txt```).

## Requirements:

- python >= 3.6
- tweepy

## Usage:

- duplicate `.dist` files with your custom values, under ```config/```
- ```python retweet.py --help``` to show available parameters
- ```python retweet.py --dry-run false``` to run actually performing operations