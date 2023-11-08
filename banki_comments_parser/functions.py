import pandas as pd
import requests
from bs4 import BeautifulSoup

import selenium

import time 
from tqdm import tqdm

from fake_useragent import UserAgent

def get_link(year='2023', product='all'):
    link_df = []
    for page in range(5):
        time.sleep(3)
        link = f'https://www.banki.ru/services/responses/?page={page+1}&product={product}&date={year}'
        response = requests.get(link, headers={'User-Agent': UserAgent().chrome})
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        page_links = soup.find_all('tr', {'id':True})
        for link in tqdm(page_links):
            bank_info = link.find_all('td')
            link_df.append({
                'position': bank_info[0].text,
                'name': link.get('id'),
                'href': 'https://www.banki.ru' + link.find('a', {'class':'l23f9d1de'}).get('href'),
                'rating':bank_info[2].text,
                'recall_amount':bank_info[3].text,
                'bank_answer': bank_info[4].text,
                'solve_share': bank_info[5].text,
            })
    return pd.DataFrame(link_df)