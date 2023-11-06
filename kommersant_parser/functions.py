import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

import pandas as pd
from tqdm import tqdm

import warnings
warnings.filterwarnings("ignore")

def authorization(personal_login, personal_password):
    driver = webdriver.Chrome()
    auth_link = 'https://www.kommersant.ru/lk/login?from=header'
    driver.get(auth_link)

    login = driver.find_element(by=By.ID, value='email')
    login.send_keys(personal_login)

    login = driver.find_element(by=By.ID, value='password')
    login.send_keys(personal_password)

    submit = driver.find_element(by=By.XPATH, value='//*[@id="user_form"]/button')
    submit.click()
    print('Авторизация успешна!')
    return driver

def parse_page(driver, bank, start_period='2020-11-06', end_period='2023-11-06', page=1):

    page_link_data = pd.DataFrame({'bank':[], 'href':[]})

    bank_link = f'https://www.kommersant.ru/search/results?search_query={bank}&sort_type=0&search_full=2&places=1&time_range=2&dateStart={start_period}&dateEnd={end_period}&page={page}&stamp=638348844803298822'
    driver.get(bank_link)
    bank_soup = BeautifulSoup(driver.page_source, 'html.parser')

    news = bank_soup.find_all('article', {'class':'uho rubric_lenta__item'})
    for new in news:
        try:
            part_link = new.find('h3', {'class':'uho__subtitle rubric_lenta__item_subtitle'}).a.get('href')
            full_link = 'https://www.kommersant.ru' + part_link
            page_link_data.loc[len(page_link_data.index)] = [bank, full_link]
        except:
            continue
    return page_link_data

def news_parser(personal_login, personal_password, banks, n_pages, start, end, auth_type='hand'):
    if auth_type == 'auto':
        diver = authorization(personal_login, personal_password)
    else:
        driver = webdriver.Chrome()
        time.sleep(60)
        link_data = pd.DataFrame({'bank':[], 'href':[]})
        for bank in banks:
            print(f'Ищу статьи для: {bank} ({banks.index(bank) + 1} из {len(banks)})')
            for page in tqdm(range(n_pages)):
                page_links = parse_page(driver, bank, start_period=start, end_period=end, page=page+1)
                link_data = pd.concat([link_data, page_links], ignore_index=True)
                time.sleep(2)

    for i in tqdm(range(len(link_data)), desc='Обработка ссылок'):
        url = link_data.loc[i, 'href']
        driver.get(url)

        new_soup = BeautifulSoup(driver.page_source, 'html.parser')

        paper_text_block = new_soup.find('div', {'class':'article_text_wrapper js-search-mark'})
        link_data.loc[i, 'paper_text'] = str(' '.join([x.text for x in paper_text_block.find_all('p', {'class':'doc__text'})]))

        link_data.loc[i, 'title']  = str(new_soup.find('h1', {'class':'doc_header__name js-search-mark'}).text)
        link_data.loc[i, 'suptitle'] = str(new_soup.find('h2', {'class':'doc_header__subheader'}).text)
        link_data.loc[i, 'datetime']  = str(new_soup.find('time', {'class':'doc_header__publish_time'}).text)

    return link_data