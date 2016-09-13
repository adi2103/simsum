import json
import tweepy
import datetime
import globals
from tweepy import OAuthHandler
import string
import re
import logging
import os,sys

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

current_path = '/'.join(os.path.realpath(__file__).split('/')[:-1])

consumer_key = 'Ba8b4MiEEcSft5FPeJ9KVA8H5'
consumer_secret = 'kb2tjMKU9Tt0oKfD8KJRinA6BVKhapowBWQrlsDE5rpk0RmH5t'
access_token = '771428457871966209-hGZ8kZje82SlKU4Plji1a9cFWMsc29U'
access_secret = 'FEHtOERMmzafUeNLdwvqfnDUZ1ZdYrgw7dmaVxNqqTrZy'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)

def scrapeTwitterInfo(user, page_id, num_posts):
    page_info = api.get_user(page_id)._json
    def get_field(field):
        if field in page_info:
            return page_info[field]
        else:
            return ''
    user['about'] = get_field('description')
    user['description'] = get_field('description')
    user['birthday'] = get_field('birthday')
    if user['birthday'] == '':
        user['birthday'] = get_field('created_at')
    if 'location' in page_info:
        user['location'].extend([e.lower() for e in map(string.strip, re.split("(\W+)", page_info['location'])) if len(e) > 0 and not re.match("\W",e)])
    user['name'] = get_field('name')
    user['username'] = get_field('screen_name')
    if 'entities' in page_info and 'url'in page_info['entities'] and 'urls' in page_info['entities']['url']:
        for item in page_info['entities']['url']['urls']:
            if 'expanded_url' in item:
                user['website'].append(item['expanded_url'])

    alltweets = []
    new_tweets = api.user_timeline(screen_name = page_id, count=min(num_posts, 200))
    oldest = new_tweets[-1].id - 1
    alltweets.extend([tweet for tweet in new_tweets if tweet.lang == 'en'])
    tweets_till_now = min(len(alltweets), num_posts, 200)
    logging.info("...%s tweets downloaded so far" % (len(alltweets)))
    while tweets_till_now < num_posts and len(new_tweets) > 0:
        print "getting tweets before %s" % (oldest)
        new_tweets = api.user_timeline(screen_name = page_id, count=min(num_posts-tweets_till_now, 200), max_id=oldest)
        if len(new_tweets) == 0:
            break
        oldest = new_tweets[-1].id - 1
        alltweets.extend([tweet for tweet in new_tweets if tweet.lang == 'en'])
        tweets_till_now = len(alltweets)
        logging.info("...%s tweets downloaded so far" % (len(alltweets)))
    for item in alltweets:
        published = item.created_at + datetime.timedelta(hours=-5)  # EST
        published = published.strftime('%Y-%m-%d %H:%M:%S')  # best time format for spreadsheet programs
        tweet = {
            'message': item.text,
            'time': published
                  }
        user['posts'].append(tweet)

def t_info(page_id):
    user = {
        'about': '',
        'description': '',
        'birthday': '',
        'location': [],
        'name': '',
        'username': '',
        'website': [],
        'posts': []
    }
    scrapeTwitterInfo(user, page_id, globals.POSTS)
    with open(current_path+'/json/t_'+page_id+'.json', 'w') as outfile:
        json.dump(user, outfile)
    logging.info(json.dumps(user, indent=4, sort_keys=True))
    outfile.close()


