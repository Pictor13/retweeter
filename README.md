# retweeter

Search for Twitter mentions containing a specific string and retweet them with a message (picked randomly from the ```retweet_messages.txt```).

## Requirements:

- python >= 3.6
- tweepy

## Usage:

- ```git clone git@github.com:Pictor13/retweeter.git && cd retweeter```
- duplicate `.dist` files with your custom values, under ```config/```
- - ```cp config/retweet_messages.txt.dist config/retweet_messages.txt``` and then write you custom messages
- use your custom secrets into [```retweet.py```](blob/master/retweet.py#L10)
- ```python retweet.py --help``` to show available parameters

### Default usage:

- ```python retweet.py --dry-run false``` to run actually performing operations