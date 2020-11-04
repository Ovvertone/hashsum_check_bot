from bs4 import BeautifulSoup
from hashlib import md5
from os.path import abspath
import requests
import sys

FILENAME = abspath('data1.html')


def parser(url):
    return str(BeautifulSoup(requests.get(url=url).content, 'html.parser'))


def hash_sum(filename=FILENAME):
    hash_alg = md5()
    with open(filename, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            hash_alg.update(chunk)
    return hash_alg.hexdigest()


if __name__ == '__main__':
    with open(FILENAME, 'w') as file:
        file.write(parser(sys.argv[1]))
    print(hash_sum())
