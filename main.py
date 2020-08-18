import os

import cv2
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from requests import get

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/50.0.2661.102 Safari/537.36'}
nPages = 1


def fetchMetadataFreepik():
    if not os.path.exists('freepik'):
        os.makedirs('freepik')

    metadata = open('freepik/metadata.csv', 'w')
    metadata.write('URL,Likes,Downloads,Keyword,Title\n')

    for i in range(1, nPages + 1):
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


def fetchImgsFreepik():
    if not os.path.exists('freepik/img'):
        os.makedirs('freepik/img')
    metadata = pd.read_csv('freepik/metadata.csv')
    for url in metadata['URL']:
        with open(f'freepik/img/{url}', 'wb') as f:
            f.write(get(f'https://image.freepik.com/free-icon/{url}').content)


'''
def flipImgs():
    if not os.path.exists('flipped'):
        os.makedirs('flipped')
    for filename in os.listdir('img'):
        original = cv2.imread(f'img/{filename}')
        cv2.imwrite(f'flipped/flipped{filename}', cv2.flip(original, 1))
'''


def processImgsFreepik():
    #imgs = []
    if not os.path.exists('freepik/processed'):
        os.makedirs('freepik/processed')
    for filename in os.listdir('freepik/img'):
        original = cv2.imread(f'freepik/img/{filename}')

        # Padding
        h_original, w_original, _ = original.shape
        h_desired, w_desired, = 626, 626
        if (h_original, w_original) == (h_desired, w_desired):
            cv2.imwrite(f'freepik/processed/{filename}', original)
            continue

        white = (255, 255, 255)
        padded = np.full((h_desired, w_desired, 3), white, dtype=np.uint8)
        x = (w_desired - w_original) // 2
        y = (h_desired - h_original) // 2
        padded[y:y + h_original, x:x + w_original] = original

        # Grayscaling
        gray = cv2.cvtColor(padded, cv2.COLOR_BGR2GRAY)

        # Quality should be 0 or 100?
        cv2.imwrite(f'freepik/processed/{filename}', gray, [int(cv2.IMWRITE_JPEG_QUALITY ), 100])

        # Most of pixels are either 0 or 255 so
        # normalize them from [0, 255] to [-1, 1]
        gray = gray / 255.0
        gray -= 0.5
        gray *= 2
        gray = gray.astype('float32')
        np.save(f'freepik/processed/{filename}', gray)
        # imgs += [gray]

    # np.savez_compressed('freepik/processedFile', *imgs)


def fetchMetadataFlaticon():
    if not os.path.exists('flaticon'):
        os.makedirs('flaticon')

    metadata = open('flaticon/metadata.csv', 'w')
    metadata.write('URL,Downloads,Name,Keyword,Category_id,Category_name\n')

    for i in range(1, nPages + 1):
        page = get(
            f'https://www.flaticon.com/search/{i}?search-type=icons&license=selection&color=1&stroke=1',
            #f'https://www.flaticon.com/search/{i}?search-type=icons&license=selection&color=1&stroke=2',
            headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        icons = soup.find_all('li', class_='icon')
        for icon in icons:
            try:
                img = '/'.join(icon['data-icon_src'].split('/')[5:])
                img = img.split('.')[0] + '.png'
                downloads = icon['data-downloads']
                name = icon['data-name']
                keyword = icon['data-keyword']
                category_id = icon['data-category_id']
                category_name = icon['data-category_name']

                metadata.write(f'{img},{downloads},{name},{keyword},{category_id},{category_name}\n')
            except:
                break
    metadata.close()

def fetchImgsFlaticon():
    if not os.path.exists('flaticon/img'):
        os.makedirs('flaticon/img')
    metadata = pd.read_csv('flaticon/metadata.csv')
    for url in metadata['URL']:
        filename = '_'.join(url.split('/'))
        with open(f'flaticon/img/{filename}', 'wb') as f:
            f.write(get(f'https://image.flaticon.com/icons/png/512/{url}').content)

def processImgsFlaticon():
    if not os.path.exists('flaticon/processed'):
        os.makedirs('flaticon/processed')
    for filename in os.listdir('flaticon/img'):
        original = cv2.imread(f'flaticon/img/{filename}', cv2.IMREAD_UNCHANGED)

        # gray = 255 - original[:, :, 3]
        # cv2.imwrite(f'flaticon/processed/{filename}', gray)
        # White instead of transparent background
        mask = original[:, :, 3] == 0
        original[mask] = [255, 255, 255, 255]

        # Grayscaling
        gray = cv2.cvtColor(original, cv2.COLOR_BGRA2GRAY)

        # Most of pixels are either 0 or 255 so
        # normalize them from [0, 255] to [-1, 1]
        gray = gray / 255.0
        gray -= 0.5
        gray *= 2
        gray = gray.astype('float32')
        np.save(f'flaticon/processed/{filename}', gray)