from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError
from requests.exceptions import ConnectionError
from collections import Counter
from pymongo import MongoClient
from bs4 import BeautifulSoup
from sys import argv, exit
from hashlib import md5
from os import environ
import requests
import lxml

try:
    URL = argv[1]
except IndexError:
    exit('Missing url')

try:
    cluster = MongoClient(environ.get('MONGO_PW'))
    db = cluster['hash_sum']
    collection = db['url_hash']
except ConfigurationError:
    exit('No internet connection')


def parser(url=URL):
    try:
        soup = BeautifulSoup(requests.get(url).content, 'lxml')
    except ConnectionError:
        exit('Invalid url')
    return [tag for tag in soup.descendants if tag.name and len(tag.contents) == 0]


def hash_sum(content=parser()):
    hash_alg = md5()
    hash_sum_list = []
    for tag in content:
        hash_alg.update(tag.encode())
        hash_sum_list.append({
            'tag': tag.name,
            'tag_hash_sum': hash_alg.hexdigest(),
        })
    return hash_sum_list


def check_hash_sum(hash_sum=hash_sum()):
    try:
        old_hs_list = collection.find_one({'url': URL})['hash_sum_list']
        collection.update_one({'url': URL}, {'$set': {'hash_sum_list': hash_sum}})
        new_hs_list = collection.find_one({'url': URL})['hash_sum_list']
        diff = []
        [diff.append(new_hs['tag']) for old_hs, new_hs in zip(old_hs_list, new_hs_list) if old_hs != new_hs]
        diff_count = Counter(diff)
        print('HTML code hasn\'t changed') if diff == [] else print('The following tags have changed:', diff_count)
    except TypeError:
        collection.insert_one({
            'url': URL,
            'hash_sum_list': hash_sum,
        })
        print('Hash sum has been added to the database')
    except ServerSelectionTimeoutError:
        exit('Error connecting to database')
    return


if __name__ == '__main__':
    check_hash_sum()
