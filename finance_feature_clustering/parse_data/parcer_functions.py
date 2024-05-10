import pandas as pd
import numpy as np
import re 

import requests
from bs4 import BeautifulSoup

import time

import warnings
warnings.filterwarnings('ignore')


class Download_bank_ids():
    """
    Скачиваем таблицу формата | bank_name | bank_id |
    """
    def __init__(self):
        self.total_table = None
        
    def page_getter(self):
        for p in range(8):
            page = p + 1
            url = f'https://www.banki.ru/banks/ratings/?source=submenu_banksratings&PAGEN_1={page}'
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            yield soup

    def table_creator_page(self, soup) -> pd.DataFrame:
        bank_id_table = pd.DataFrame(columns = ['bank_name', 'id'])
        names_and_ids = soup.find_all('a', {'class': 'widget__link'})
        for row, i in enumerate(names_and_ids):
            bank_id = i.get('href')
            pattern = re.compile(r'\d{1,}')
            match = re.findall(pattern, bank_id)
            bank_id_table.loc[row] = [i.text, match[0]]
        return bank_id_table

    def total_banks_ids_dict_creator(self) -> pd.DataFrame:
        self.total_table = pd.DataFrame(columns = ['bank_name', 'id'])
        for soup in self.page_getter():
            time.sleep(1.5)
            page_bank_id_table = self.table_creator_page(soup)
            self.total_table = pd.concat([self.total_table, page_bank_id_table])
            print('page_dowloaded')
        return self.total_table  


class Download_bank_pages():
    '''
    Выбираем нужный год \n
    Загружаем таблицу с id банков \n
    no_fl_assets - проблемные банки после первого прохода с параметром по умолчанию
    '''
    def __init__(self, year, bank_ids_table, no_fl_assets = False):
        self.year = year
        self.bank_ids_table = bank_ids_table
        self.final_df = pd.DataFrame()
        self.no_fl_assets = no_fl_assets
        self.problem_banks = []

    def bank_page_url_generator(self):
        for _ , row in self.bank_ids_table.iterrows():
            row_id = row['id']
            bank_name = row['bank_name']
            url = f'https://www.banki.ru/banks/ratings/?BANK_ID={row_id}&IS_SHOW_GROUP=0&IS_SHOW_LIABILITIES=0&date1={self.year}-12-01&date2={self.year}-01-01'
            yield bank_name, url

    def extract_bank_table_from_url(self, bank_name, url):    #показатели на конец года
        response = requests.get(url)
        time.sleep(2)
        soup = BeautifulSoup(response.content, 'html.parser')

        #таблица 1
        table1 = soup.find_all('table', {'class' : 'standard-table'})[0]   #ключевые показатели
        df = pd.read_html(str(table1))[0]
        df = df.set_axis(['место_по_России', 'место_в_регионе','Показатель', 'дек_тыс_руб', 'янв_тыс_руб', 'изм', 'процент'], axis=1)
        df = df[['Показатель', 'дек_тыс_руб']]
        df['дек_тыс_руб'] = df['дек_тыс_руб'].apply(lambda x: x.replace(' ', '')).astype(float)
        df = df.pivot_table(columns = 'Показатель', values='дек_тыс_руб')
        df_1 = df.reset_index().drop(columns='index')

        if self.no_fl_assets:
            df_1 = df_1.drop(columns = ['Активы нетто','Капитал (по форме 123)','Чистая прибыль'])
        else:
            df_1 = df_1.drop(columns = ['Активы нетто','Вклады физических лиц','Капитал (по форме 123)','Чистая прибыль'])
        
        #таблица 2
        table2 = soup.find_all('table', {'class' : 'standard-table'})[1] #абсолютные показатели
        df = pd.read_html(str(table2))[0]
        df = df.set_axis(['место_по_России', 'место_в_регионе','Показатель', 'дек_тыс_руб', 'янв_тыс_руб', 'изм', 'процент'], axis=1) 
        df = df[['Показатель', 'дек_тыс_руб']]
        df['дек_тыс_руб'] = df['дек_тыс_руб'].apply(lambda x: x.replace(' ', '')).astype(float)

        if self.year == 2023:
            df.iloc[15, df.columns.get_loc('Показатель')] = 'ФЛ Счета'
        else:
            df.iloc[6, df.columns.get_loc('Показатель')] = 'КрФЛ Сроком до 180 дней'
            df.iloc[7, df.columns.get_loc('Показатель')] = 'КрФЛ Сроком от 181 дня до 1 года'
            df.iloc[8, df.columns.get_loc('Показатель')] = 'КрФЛ Сроком от 1 года до 3 лет'
            df.iloc[9, df.columns.get_loc('Показатель')] = 'КрФЛ Сроком более 3 лет'
            df.iloc[11, df.columns.get_loc('Показатель')] = 'ФЛ Просроченная задолженность'

            df.iloc[17, df.columns.get_loc('Показатель')] = 'КрЮЛ Сроком до 180 дней'
            df.iloc[18, df.columns.get_loc('Показатель')] = 'КрЮЛ Сроком от 181 дня до 1 года'
            df.iloc[19, df.columns.get_loc('Показатель')] = 'КрЮЛ Сроком от 1 года до 3 лет'
            df.iloc[20, df.columns.get_loc('Показатель')] = 'КрЮЛ Сроком более 3 лет'
            df.iloc[22, df.columns.get_loc('Показатель')] = 'ЮЛ Просроченная задолженность'

            df.iloc[32, df.columns.get_loc('Показатель')] = 'ФЛ Счета'
            df.iloc[33, df.columns.get_loc('Показатель')] = 'ФЛ Счета оборот'
            df.iloc[34, df.columns.get_loc('Показатель')] = 'ФЛ Счета Сроком до 90 дней'
            df.iloc[35, df.columns.get_loc('Показатель')] = 'ФЛ Счета Сроком до 90 дней оборот'
            df.iloc[36, df.columns.get_loc('Показатель')] = 'ФЛ Счета Сроком от 91 до 180 дней'
            df.iloc[37, df.columns.get_loc('Показатель')] = 'ФЛ Счета Сроком от 91 до 180 дней оборот'
            df.iloc[38, df.columns.get_loc('Показатель')] = 'ФЛ Счета Сроком от 181 дня до 1 года'
            df.iloc[39, df.columns.get_loc('Показатель')] = 'ФЛ Счета Сроком от 181 дня до 1 года оборот'
            df.iloc[40, df.columns.get_loc('Показатель')] = 'ФЛ Счета Сроком от 1 года до 3 лет'
            df.iloc[41, df.columns.get_loc('Показатель')] = 'ФЛ Счета Сроком от 1 года до 3 лет оборот'
            df.iloc[42, df.columns.get_loc('Показатель')] = 'ФЛ Счета Сроком более 3 лет'
            df.iloc[43, df.columns.get_loc('Показатель')] = 'ФЛ Счета Сроком более 3 лет оборот'

            df.iloc[46, df.columns.get_loc('Показатель')] = 'ЮЛ Счета'
            df.iloc[47, df.columns.get_loc('Показатель')] = 'ЮЛ Счета оборот'
            df.iloc[48, df.columns.get_loc('Показатель')] = 'ЮЛ Счета Сроком до 90 дней'
            df.iloc[49, df.columns.get_loc('Показатель')] = 'ЮЛ Счета Сроком до 90 дней оборот'
            df.iloc[50, df.columns.get_loc('Показатель')] = 'ЮЛ Счета Сроком от 91 до 180 дней'
            df.iloc[51, df.columns.get_loc('Показатель')] = 'ЮЛ Счета Сроком от 91 до 180 дней оборот'
            df.iloc[52, df.columns.get_loc('Показатель')] = 'ЮЛ Счета Сроком от 181 дня до 1 года'
            df.iloc[53, df.columns.get_loc('Показатель')] = 'ЮЛ Счета Сроком от 181 дня до 1 года оборот'
            df.iloc[54, df.columns.get_loc('Показатель')] = 'ЮЛ Счета Сроком от 1 года до 3 лет'
            df.iloc[55, df.columns.get_loc('Показатель')] = 'ЮЛ Счета Сроком от 1 года до 3 лет оборот'
            df.iloc[56, df.columns.get_loc('Показатель')] = 'ЮЛ Счета Сроком более 3 лет'
            df.iloc[57, df.columns.get_loc('Показатель')] = 'ЮЛ Счета Сроком более 3 лет оборот'

        df = df.pivot_table(columns = 'Показатель', values='дек_тыс_руб')
        df_2 = df.reset_index().drop(columns='index')

        #таблица 3
        table3 = soup.find_all('table', {'class' : 'standard-table'})[2]    #относительные показатели
        df = pd.read_html(str(table3))[0]
        df = df.set_axis(['место_по_России', 'место_в_регионе','Показатель', 'дек_процент', 'янв_процент', 'изм', 'процент'], axis=1) 
        df = df[['Показатель', 'дек_процент']]

        if self.year == 2019:
            df = df.drop(index=6)
            
        df['дек_процент'] = df['дек_процент'].astype(float) / 100
        df = df.pivot_table(columns = 'Показатель', values='дек_процент')
        df_3 = df.reset_index().drop(columns='index')

        merged_row = pd.concat([df_1, df_2, df_3], axis = 1)
        merged_row['bank_name'] = bank_name

        return merged_row
    
    def parce_year_table(self) -> pd.DataFrame:
        cnt = 1
        for bank_name, url in self.bank_page_url_generator():
            try:
                row = self.extract_bank_table_from_url(bank_name, url)
                self.final_df = pd.concat([self.final_df, row])   #собираем итоговую табличку по строкам
                print('bank row downloaded', cnt)
                cnt += 1
            except:
                print(bank_name, url)
                self.problem_banks.append(bank_name)
                continue
    
    @staticmethod
    def prettify_final_df(df):
        df.columns.name = 0
        df = df.reset_index().drop(columns = 'index')

        df = df[['bank_name','Вложения в ценные бумаги', 'Кредитный портфель',
       'Просроченная задолженность в кредитном портфеле', 'Активы нетто',
       'Бумаги переданные в РЕПО', 'Векселя', 'Вклады физических лиц',
       'Вклады физических лиц оборот', 'Вложения в акции',
       'Вложения в векселя', 'Вложения в капиталы других организаций',
       'Вложения в облигации', 'Выданные МБК', 'Выданные МБК оборот всего',
       'Выпущенные облигации и векселя', 'Высоколиквидные активы',
       'Денежные средства в кассе', 'Денежные средства в кассе оборот',
       'Капитал (по форме 123)', 'КрФЛ Сроком более 3 лет',
       'КрФЛ Сроком до 180 дней', 'КрФЛ Сроком от 1 года до 3 лет',
       'КрФЛ Сроком от 181 дня до 1 года', 'КрЮЛ Сроком более 3 лет',
       'КрЮЛ Сроком до 180 дней', 'КрЮЛ Сроком от 1 года до 3 лет',
       'КрЮЛ Сроком от 181 дня до 1 года',
       'Кредиты предприятиям и организациям', 'Кредиты физическим лицам',
       'ЛОРО-счета', 'НОСТРО-счета', 'Облигации', 'Овердрафты',
       'Овердрафты и прочие предоставленные средства',
       'Основные средства и нематериальные активы', 'Привлеченные МБК',
       'Привлеченные МБК оборот', 'Привлеченные от ЦБ РФ',
       'Привлеченные от ЦБ РФ оборот', 'Прочие активы',
       'Размещенные МБК в ЦБ РФ', 'Размещенные МБК в ЦБ РФ оборот',
       'Средства предприятий и организаций',
       'Средства предприятий и организаций оборот',
       'ФЛ Просроченная задолженность', 'ФЛ Счета',
       'ФЛ Счета Сроком более 3 лет', 'ФЛ Счета Сроком более 3 лет оборот',
       'ФЛ Счета Сроком до 90 дней', 'ФЛ Счета Сроком до 90 дней оборот',
       'ФЛ Счета Сроком от 1 года до 3 лет',
       'ФЛ Счета Сроком от 1 года до 3 лет оборот',
       'ФЛ Счета Сроком от 181 дня до 1 года',
       'ФЛ Счета Сроком от 181 дня до 1 года оборот',
       'ФЛ Счета Сроком от 91 до 180 дней',
       'ФЛ Счета Сроком от 91 до 180 дней оборот', 'ФЛ Счета оборот',
       'Чистая прибыль', 'ЮЛ Просроченная задолженность', 'ЮЛ Счета',
       'ЮЛ Счета Сроком более 3 лет', 'ЮЛ Счета Сроком более 3 лет оборот',
       'ЮЛ Счета Сроком до 90 дней', 'ЮЛ Счета Сроком до 90 дней оборот',
       'ЮЛ Счета Сроком от 1 года до 3 лет',
       'ЮЛ Счета Сроком от 1 года до 3 лет оборот',
       'ЮЛ Счета Сроком от 181 дня до 1 года',
       'ЮЛ Счета Сроком от 181 дня до 1 года оборот',
       'ЮЛ Счета Сроком от 91 до 180 дней',
       'ЮЛ Счета Сроком от 91 до 180 дней оборот', 'ЮЛ Счета оборот', 'Н1',
       'Н2', 'Н3', 'Рентабельность активов-нетто', 'Рентабельность капитала',
       'Уровень обеспечения кредитного портфеля залогом имущества',
       'Уровень просроченной задолженности по кредитному портфелю',
       'Уровень резервирования по кредитному портфелю']]
        return df







        



