import fb_api
import t_api
import os,sys
import json
import logging
import string
import nltk
from nltk.stem.porter import *
from nltk.corpus import stopwords
from pprint import pprint
from gensim import corpora, models, similarities
from collections import defaultdict
from nltk.corpus import sentiwordnet as swn
from nltk.metrics import *

current_path = '/'.join(os.path.realpath(__file__).split('/')[:-1])


def info_filter(fb_data, t_data):
    total = 0.0
    matches = 0
    features = 0
    total += semantic([fb_data['about'], fb_data['description']], [t_data['about'], t_data['description']], 0)
    features+=1
    if fb_data['birthday'] == t_data['birthday']:
        matches+=1
    features+=1
    for item1 in fb_data['location']:
        if item1 in t_data['location']:
            matches += 1
    features += len(fb_data['location']) + len(t_data['location'])
    if fb_data['website'] == t_data['website']:
        matches+=1
    features+=1
    if fb_data['name'] == t_data['name']:
        matches+=1
    features+=1
    if fb_data['username'] == t_data['username']:
        matches+=1
    features+=1

    return  float(total+float(matches))/float(features)


def sentiment(words1, words2):

    tagged1 = nltk.pos_tag(words1)  # for POSTagging
    tagged2 = nltk.pos_tag(words2)

    score1 = 0.0
    score2 = 0.0

    for i in range(0, len(tagged1)):
        pscore1 = 0.0
        nscore1 = 0.0
        if 'NN' in tagged1[i][1] and len(swn.senti_synsets(tagged1[i][0], 'n')) > 0:
            pscore1 += (list(swn.senti_synsets(tagged1[i][0], 'n'))[0]).pos_score()  # positive score of a word
            nscore1 += (list(swn.senti_synsets(tagged1[i][0], 'n'))[0]).neg_score()  # negative score of a word
        elif 'VB' in tagged1[i][1] and len(swn.senti_synsets(tagged1[i][0], 'v')) > 0:
            pscore1 += (list(swn.senti_synsets(tagged1[i][0], 'v'))[0]).pos_score()
            nscore1 += (list(swn.senti_synsets(tagged1[i][0], 'v'))[0]).neg_score()
        elif 'JJ' in tagged1[i][1] and len(swn.senti_synsets(tagged1[i][0], 'a')) > 0:
            pscore1 += (list(swn.senti_synsets(tagged1[i][0], 'a'))[0]).pos_score()
            nscore1 += (list(swn.senti_synsets(tagged1[i][0], 'a'))[0]).neg_score()
        elif 'RB' in tagged1[i][1] and len(swn.senti_synsets(tagged1[i][0], 'r')) > 0:
            pscore1 += (list(swn.senti_synsets(tagged1[i][0], 'r'))[0]).pos_score()
            nscore1 += (list(swn.senti_synsets(tagged1[i][0], 'r'))[0]).neg_score()
        if pscore1 > nscore1:
            score1 += 1.0
        elif pscore1 < nscore1:
            score1 -= 1.0

    for i in range(0, len(tagged2)):
        pscore2 = 0.0
        nscore2 = 0.0
        if 'NN' in tagged2[i][1] and len(swn.senti_synsets(tagged2[i][0], 'n')) > 0:
            pscore2 += (list(swn.senti_synsets(tagged2[i][0], 'n'))[0]).pos_score()  # positive score of a word
            nscore2 += (list(swn.senti_synsets(tagged2[i][0], 'n'))[0]).neg_score()  # negative score of a word
        elif 'VB' in tagged2[i][1] and len(swn.senti_synsets(tagged2[i][0], 'v')) > 0:
            pscore2 += (list(swn.senti_synsets(tagged2[i][0], 'v'))[0]).pos_score()
            nscore2 += (list(swn.senti_synsets(tagged2[i][0], 'v'))[0]).neg_score()
        elif 'JJ' in tagged2[i][1] and len(swn.senti_synsets(tagged2[i][0], 'a')) > 0:
            pscore2 += (list(swn.senti_synsets(tagged2[i][0], 'a'))[0]).pos_score()
            nscore2 += (list(swn.senti_synsets(tagged2[i][0], 'a'))[0]).neg_score()
        elif 'RB' in tagged2[i][1] and len(swn.senti_synsets(tagged2[i][0], 'r')) > 0:
            pscore2 += (list(swn.senti_synsets(tagged2[i][0], 'r'))[0]).pos_score()
            nscore2 += (list(swn.senti_synsets(tagged2[i][0], 'r'))[0]).neg_score()
        if pscore2 > nscore2:
            score2 += 1.0
        elif pscore2 < nscore2:
            score2 -= 1.0

    score1 /= float(len(tagged1))
    score2 /= float(len(tagged2))
    logging.info(score1)
    logging.info(score2)

    total = abs(score1 - score2)
    logging.info(1.00 - total)
    return 1.00 - total


def semantic(DOCS1, DOCS2, sentiment_flag):
    docs1 = DOCS1
    docs2 = DOCS2
    total = 0.0
    docs1 = [doc.encode('utf-8') for doc in docs1]
    docs1 = [[e.lower() for e in map(string.strip, re.split("(\W+)", doc)) if len(e) > 0 and not re.match("\W", e)] for doc in docs1]
    #docs1 = [doc.translate(None, string.punctuation).lower().split() for doc in docs1 ]
    stops = set(stopwords.words('english'))
    new_docs1 = []
    for doc in docs1:
        words = []
        for w in doc:
            if w not in stops:
                words.append(w)
        new_docs1.append(words)

    stemmer = PorterStemmer()
    docs1 = [[stemmer.stem(word) for word in doc] for doc in new_docs1]
    pprint(docs1)

    frequency = defaultdict(int)
    for doc in docs1:
        for token in doc:
            frequency[token] += 1
    # docs = [[token for token in text if frequency[token] > 1] for text in docs]
    pprint(frequency)

    dictionary = corpora.Dictionary(docs1)
    dictionary.save('/tmp/facebook.dict')
    dictionary = corpora.Dictionary.load('/tmp/facebook.dict')
    print(dictionary.token2id)

    corpus = [dictionary.doc2bow(text) for text in docs1]
    corpora.MmCorpus.serialize('/tmp/facebook.mm', corpus)
    corpus = corpora.MmCorpus('/tmp/facebook.mm')
    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=400)
    print(corpus)

    index = similarities.MatrixSimilarity(lsi[corpus])
    index.save('/tmp/facebook.index')
    index = similarities.MatrixSimilarity.load('/tmp/facebook.index')

    sim_matrix = []

    total = 0.0
    for i in range(0, len(docs2)):
        doc = docs2[i]
        words = [e.lower() for e in map(string.strip, re.split("(\W+)", doc)) if len(e) > 0 and not re.match("\W", e)]
        #words = doc.translate(None, string.punctuation).lower().split()
        new_words = []
        for w in words:
            if w not in stops:
                new_words.append(w)
        doc = [stemmer.stem(word) for word in new_words]
        vec_bow = dictionary.doc2bow(doc)
        vec_lsi = lsi[vec_bow]
        print(vec_lsi)

        sims = index[vec_lsi]
        sim_matrix.append(list(enumerate(sims)))

        max_val = 0.0
        max_ind = -1
        least_neg = -1.0
        for j, val in list(enumerate(sims)):
            if val > max_val:
                max_val = val
                max_ind = j
            elif val > least_neg:
                least_neg = val

        if max_ind != -1 and sentiment_flag and max_val > 0.5:
            total += max_val * sentiment(docs1[max_ind], doc)
        elif max_ind != -1 and sentiment_flag != 1:
            total += max_val
        else:
            total += least_neg
        logging.info(docs1[max_ind])
        logging.info(doc)
        logging.info(max_val)
    if float(total) < 0.0:
        return 0.0
    logging.info(float(total)/float(len(DOCS2)))
    return float(total)/float(len(DOCS2))


def similarity(fb_username, t_username):

    if not os.path.exists(current_path+"/json/fb_"+fb_username+".json"):
        fb_api.fb_info(fb_username)

    if not os.path.exists(current_path+"/json/t_"+t_username+".json"):
        t_api.t_info(t_username)

    with open(current_path+"/json/fb_"+fb_username+".json") as infile:
        fb_data = json.load(infile)
    infile.close()

    with open(current_path+"/json/t_"+t_username+".json") as infile:
        t_data = json.load(infile)
    infile.close()

    if t_username in fb_data['twitter_id'].split('/'):
        return 100

    sim_total = info_filter(fb_data, t_data)
    levenshtein = 1.0 - float(edit_distance(fb_username.lower(), t_username.lower()))/float(max(len(fb_username), len(t_username)))
    sim_total = sim_total * 0.1 + levenshtein * 0.3 + semantic([item['message'] for item in fb_data['posts']], [item['message'] for item in t_data['posts']], 1) * 0.6
    logging.info(levenshtein)
    logging.info(sim_total)
    if sim_total < 0.2:
        sim_total = 1.0
    elif sim_total > 0.85:
        sim_total = 99.0
    else:
        sim_total = 1.0 + (sim_total*100-20.0)*98.0/65.0
    return sim_total