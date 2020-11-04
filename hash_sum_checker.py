from bs4 import BeautifulSoup
from hashlib import md5
import requests
import sys


def parser(url: str) -> str:
    return str(BeautifulSoup(requests.get(url=url).content, 'html.parser'))


def hash_sum(filename: str) -> str:
    hash_alg = md5()
    with open(filename, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            hash_alg.update(chunk)
    return hash_alg.hexdigest()


if __name__ == '__main__':
    with open('data.html', 'w') as file:
        file.write(parser(sys.argv[1]))
    print(hash_sum('data.html'))
