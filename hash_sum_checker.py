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
        return BeautifulSoup(requests.get(url).content, 'lxml')
    except ConnectionError:
        exit('Invalid url')


def hash_sum():
    hash_alg = md5()
    for tag in parser():
        hash_alg.update(tag.encode())
    return hash_alg.hexdigest()


if __name__ == '__main__':
    collection.find_one_and_update({'url': URL}, {'$set': {'hash_sum': hash_sum()}}, upsert=True)
