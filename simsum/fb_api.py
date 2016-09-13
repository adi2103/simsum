import urllib2
import json
import datetime
import time
import globals
import string
import re
import os,sys
import logging

current_path = '/'.join(os.path.realpath(__file__).split('/')[:-1])
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

app_id = '782208315215966'
app_secret = 'e3e2f8018eb0b4f1e32e8425d7e478a8'
access_token = app_id + "|" + app_secret

def request_until_succeed(url):
    req = urllib2.Request(url)
    success = False
    while success is False:
        try:
            response = urllib2.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception, e:
            print e
            time.sleep(5)
            print "Error for URL %s: %s" % (url, datetime.datetime.now())
            print "Retrying."
    return response.read()


def unicode_normalize(text):
    return text.translate({ 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22,
                            0xa0:0x20 }).encode('utf-8')


def scrapeFacebookPageInfo(user, page_id):
    base = "https://graph.facebook.com/v2.7"
    node = "/%s" % page_id
    fields = "?limit=100&fields=about,description,birthday,location,name,username,website,screennames"
    parameters = "&access_token=%s" % (access_token)
    url = base + node + fields + parameters
    # retrieve data
    data = json.loads(request_until_succeed(url))

    def get_field(field):
        if field not in data:
            return ''
        else:
            return data[field]

    user['about'] = get_field('about')
    user['description'] = get_field('description')
    user['birthday'] = get_field('birthday')
    if 'location' in data:
        user['location'].extend([e.lower() for e in map(string.strip, re.split("(\W+)", data['location']['city'])) if len(e) > 0 and not re.match("\W",e)])
        user['location'].extend([e.lower() for e in map(string.strip, re.split("(\W+)", data['location']['country'])) if len(e) > 0 and not re.match("\W",e)])
    user['name'] = get_field('name')
    user['username'] = get_field('username')
    user['website'] = get_field('website')
    if 'screennames' in data:
        for item in data['screennames']['data']:
            if item['service_name'].lower() == 'twitter':
                user['twitter_id'] = item['value']


def getFacebookPageFeedData(page_id):
    base = "https://graph.facebook.com/v2.7"
    node = "/%s/posts" % page_id
    fields = "/?fields=message,created_time,type,id,shares,reactions.limit(0).summary(true)"
    parameters = "&access_token=%s" % access_token
    url = base + node + fields + parameters
    data = json.loads(request_until_succeed(url))
    return data


def getReactionsForPost(post_id):

    base = "https://graph.facebook.com/v2.7"
    node = "/%s" % post_id
    reactions = "/?fields=" \
            "reactions.type(LIKE).limit(0).summary(total_count).as(like)" \
            ",reactions.type(LOVE).limit(0).summary(total_count).as(love)" \
            ",reactions.type(WOW).limit(0).summary(total_count).as(wow)" \
            ",reactions.type(HAHA).limit(0).summary(total_count).as(haha)" \
            ",reactions.type(SAD).limit(0).summary(total_count).as(sad)" \
            ",reactions.type(ANGRY).limit(0).summary(total_count).as(angry)"
    parameters = "&access_token=%s" % access_token
    url = base + node + reactions + parameters
    data = json.loads(request_until_succeed(url))
    return data


def processFacebookPageFeedStatus(user, post):

    post_id = post['id']
    post_message = '' if 'message' not in post.keys() else unicode_normalize(post['message'])

    # Time needs special care since a) it's in UTC and
    # b) it's not easy to use in statistical programs.
    published = datetime.datetime.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
    published = published + datetime.timedelta(hours=-5)  # EST
    published = published.strftime('%Y-%m-%d %H:%M:%S')   # best time format for spreadsheet programs

    num_reactions = 0 if 'reactions' not in post else post['reactions']['summary']['total_count']
    num_shares = 0 if 'shares' not in post else post['shares']['count']
    total_responses = num_reactions + num_shares

    # Counts of each reaction separately; good for sentiment
    reactions = getReactionsForPost(post_id)

    def get_num_total_reactions(reaction_type, reactions):
        if reaction_type not in reactions:
            return 0
        else:
            return reactions[reaction_type]['summary']['total_count']

    num_likes = get_num_total_reactions('like', reactions)
    num_loves = get_num_total_reactions('love', reactions)
    num_wows = get_num_total_reactions('wow', reactions)
    num_hahas = get_num_total_reactions('haha', reactions)
    num_sads = get_num_total_reactions('sad', reactions)
    num_angrys = get_num_total_reactions('angry', reactions)

    num_pos = int(float(num_shares + num_likes + num_loves + num_wows + num_hahas)*100/float(total_responses))
    num_neg = int(float(num_sads + num_angrys)*100/float(total_responses))
    user_post = {
        'message': post_message,
        'time': published,
        'pos': num_pos,
        'neg': num_neg
    }
    user['posts'].append(user_post)

    # Record oldest post time
    if globals.OLDEST_TIME > published:
        globals.OLDEST_TIME = published


def scrapeFacebookPageFeed(user, page_id, num_posts):

    has_next_page = True
    num_processed = 0   # keep a count on how many we've processed

    posts = getFacebookPageFeedData(page_id)
    while has_next_page and num_processed < num_posts:
        for post in posts['data']:
            if 'reactions' in post:
                processFacebookPageFeedStatus(user, post)
                num_processed += 1
            if num_processed % 100 == 0:
                print "%s Posts Processed: %s" % \
                    (num_processed, datetime.datetime.now())
            if num_processed == num_posts:
                break
        if 'paging' in posts.keys():
            posts = json.loads(request_until_succeed(posts['paging']['next']))
        else:
            has_next_page = False


def fb_info(page_id):
    user = {
        'about': '',
        'description': '',
        'birthday': '',
        'location': [],
        'name': '',
        'username': '',
        'website': '',
        'twitter_id': '',
        'posts': []
    }
    scrapeFacebookPageInfo(user, page_id)
    scrapeFacebookPageFeed(user, page_id, globals.POSTS)
    with open(current_path+'/json/fb_'+page_id+'.json', 'w') as outfile:
        json.dump(user, outfile)
    logging.info(json.dumps(user, indent=4, sort_keys=True))
    outfile.close()


