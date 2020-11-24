from collections import Counter
from os import environ

from bs4 import BeautifulSoup
from hashlib import md5
import lxml
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import requests
from requests.exceptions import ConnectionError

cluster = MongoClient(environ.get('MONGO_PW'))
db = cluster['hash_sum']
collection = db['url_hash']


def parser(url):
    try:
        soup = BeautifulSoup(requests.get(url).content, 'lxml')
    except ConnectionError:
        return 'Invalid url'
    return [tag for tag in soup.descendants if tag.name and len(tag.contents) == 0]


def hash_sum(url, parser=parser):
    hash_alg = md5()
    hash_sum_list = []
    for tag in parser(url):
        hash_alg.update(tag.encode())
        hash_sum_list.append({
            'tag': tag.name,
            'tag_hash_sum': hash_alg.hexdigest(),
        })
    return hash_sum_list


def check_hash_sum(url, hash_sum=hash_sum):
    try:
        old_hs_list = collection.find_one({'url': url})['hash_sum_list']
        collection.update_one({'url': url}, {'$set': {'hash_sum_list': hash_sum(url)}})
        new_hs_list = collection.find_one({'url': url})['hash_sum_list']
        diff = []
        [diff.append(new_hs['tag']) for old_hs, new_hs in zip(old_hs_list, new_hs_list) if old_hs != new_hs]
        diff_count = Counter(diff).most_common()
        return 'HTML code hasn\'t changed' if diff == [] else ('The following tags have changed:', *diff_count)
    except TypeError:
        collection.insert_one({
            'url': url,
            'hash_sum_list': hash_sum,
        })
        return 'Hash sum has been added to the database'
    except ServerSelectionTimeoutError:
        return 'Error connecting to database'
