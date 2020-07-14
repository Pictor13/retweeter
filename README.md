# retweeter

Search for Twitter mentions containing a specific string and retweet them with a message (picked randomly from the ```retweet_messages.txt```).

## Requirements:

- python >= 3.6
- ```pip install tweepy```
- ```pip install pyyaml```

## Usage:

- ```git clone git@github.com:Pictor13/retweeter.git && cd retweeter```
- duplicate `.dist` config file and customise them
- - ```cp config.yaml.dist config.yaml``` and put your config
- - remember to set the secrets in the *API.authentication* config
- ```python retweet.py --help``` to show available parameters

### Default usage:

- ```python retweet.py --dry-run false``` to run actually performing operations