from bs4 import BeautifulSoup
from requests import get
import pandas as pd
import numpy as np
import cv2
import os

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
nPages = 1

def fetchMetadata():
    metadata = open('metadata.csv', 'w')
    metadata.write('URL,Likes,Downloads,Keyword,Title\n')
    
    for i in range(1, nPages+1):
        page = get(f'https://www.freepik.com/search?type=icon&page={i}', headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        figures = soup.find_all('figure')
        for figure in figures:
            image = figure['data-image'].split('/')[-1]
            likes = figure['data-likes']
            downloads = figure['data-downloads']
            keyword = figure['data-first-keyword']
            title = figure.find('p', class_='title').text
    
            metadata.write(f'{image},{likes},{downloads},{keyword},{title}\n')
    metadata.close()

def fetchImgs():
    if not os.path.exists('img'):
        os.makedirs('img')
    metadata = pd.read_csv('metadata.csv')
    for url in metadata['URL']:
        with open(f'img/{url}', 'wb') as f:
            f.write(get(f'https://image.freepik.com/free-icon/{url}').content)

def flipImgs():
    if not os.path.exists('flipped'):
        os.makedirs('flipped')
    for filename in os.listdir('img'):
        original = cv2.imread(f'img/{filename}')
        cv2.imwrite(f'flipped/flipped{filename}', cv2.flip(original, 1))

def binarizeImgs():
    if not os.path.exists('binarized'):
        os.makedirs('binarized')
    for filename in os.listdir('img'):
        original = cv2.imread(f'img/{filename}')
        gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        _, blackAndWhite = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        blackAndWhite.dtype = bool
        np.save(f'binarized/{filename}', blackAndWhite)

def grayscaleImgs():
    if not os.path.exists('grayscale'):
        os.makedirs('grayscale')
    for filename in os.listdir('img'):
        original = cv2.imread(f'img/{filename}')
        gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        _, blackAndWhite = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        cv2.imwrite(f'grayscale/{filename}', blackAndWhite)