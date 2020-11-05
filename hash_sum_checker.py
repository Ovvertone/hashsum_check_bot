from requests.exceptions import ConnectionError
from pymongo.errors import ConfigurationError
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
    return [str(tag) for tag in soup('html')]


def hash_sum(data=parser()):
    hash_alg = md5()
    [hash_alg.update(tag.encode()) for tag in data]
    return hash_alg.hexdigest()


def check_hash_sum(hash_sum=hash_sum()):
    try:
        old_hash_sum = collection.find_one({'url': URL})['hash_sum']
        collection.update_one({'url': URL}, {'$set': {'hash_sum': hash_sum}})
        new_hash_sum = collection.find_one({'url': URL})['hash_sum']
        print('HTML code hasn\'t changed') if old_hash_sum == new_hash_sum else print('HTML code has changed!')
    except TypeError:
        collection.insert_one({
            'url': URL,
            'hash_sum': hash_sum,
        })
        print('Hash sum has been added to the database')
    return


if __name__ == '__main__':
    check_hash_sum()
