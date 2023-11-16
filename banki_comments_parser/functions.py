import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import selenium

import time 
from tqdm import tqdm

from fake_useragent import UserAgent

def get_link(year='2023', product='all'):
    link_df = []
    for page in tqdm(range(5)):
        time.sleep(3)
        link = f'https://www.banki.ru/services/responses/?page={page+1}&product={product}&date={year}'
        response = requests.get(link, headers={'User-Agent': UserAgent().chrome})
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        page_links = soup.find_all('tr', {'id':True})
        for link in page_links:
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

def parse_recall_banki(link_data, n_pages=10):    
    bank_recall_data = pd.DataFrame({'bank':[], 'author':[], 'datePublished':[], 'description':[], 'name':[], 'rating':[]})
    for i in tqdm(range(len(link_data))):

        bank_name = link_data.loc[i,:]['name']
        bank_link = link_data.loc[i,:]['href']

        bank_info = pd.DataFrame({'bank':[], 'author':[], 'datePublished':[], 'description':[], 'name':[], 'rating':[]})
        for page in range(n_pages):
            time.sleep(3)
            try:
                link = f'{bank_link}?page={page+1}&is_countable=on'
                response = requests.get(link, headers={'User-Agent': UserAgent().chrome})
                html = response.content
                soup = BeautifulSoup(html, 'html.parser')
                row_json = soup.find('script', {'type':'application/ld+json'})
                string = row_json.string.replace('\r','').replace('\t','').replace('\n','').replace('@','').strip()
                info = json.loads(string)
                data = pd.DataFrame(info['review'])
                data['rating'] = data['reviewRating'].apply(lambda x: x['ratingValue'])
                data = data.drop(columns=['reviewRating', 'type'], axis=1)
                data.loc[:,'bank'] = bank_name
                bank_info = pd.concat([bank_info, data], ignore_index=True)
            except:
                continue
        bank_recall_data = pd.concat([bank_info, bank_recall_data], ignore_index=True)
    return bank_recall_data
