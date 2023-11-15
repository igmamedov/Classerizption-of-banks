import requests  
from bs4 import BeautifulSoup
import pandas as pd
import time
import numpy as np
from tqdm.notebook import tqdm
import warnings
warnings.filterwarnings('ignore')

#загружаем данные по всем показателям и по всем годам но только для показателей в тыс. руб, не для % показателей
def data_loader_tys(years_list, dates2, dates1, property_ids):  
    '''                                                             
    years_list = ['2015']
    dates2 = ['01','03','05','07','09','11']
    dates1 = ['02','04','06','08','10','12']
    property_ids = ['110', '30']
    '''
    final_table = pd.DataFrame(columns = ['Название банка']) #показательи за год мерджим с исходной табличкой
    final_table['Название банка'] = ['Сбербанк', 'ВТБ', 'Газпромбанк']
    list_for_years = [] #пока будем скачивать все только для одного года
    for year in tqdm(years_list): #для года (сколько лет, такой и счетчик)
        
        prop_table = pd.DataFrame(columns = ['Название банка']) #показательи за год мерджим
        prop_table['Название банка'] = ['Сбербанк', 'ВТБ', 'Газпромбанк']
        
        dataframes_list_prop = []
        for prop_id in property_ids: #для одного показателя внутри года
            

            dataframes_list = [] #собираем таблицу по одному показателю за год сюда
            for d2, d1 in zip(dates2, dates1): #перебираем даты
                data2 = f"{year}-{d2}-01"
                data1 = f"{year}-{d1}-01"

                url = f'https://www.banki.ru/banks/ratings/export.php?SEARCH_NAME=&SEARCH_REGN=&search[type]=name&sort_param=rating&sort_order=ASC&PROPERTY_ID={prop_id}&REGION_ID=0&date1={data1}&date2={data2}&IS_SHOW_GROUP=0&IS_SHOW_LIABILITIES=0' 
                #выгружаем инфу из url
                response = requests.get(url)

                x = BeautifulSoup(response.content, 'html.parser')
                bald_text = x.text
                raw_text = bald_text.split('\r\n')

                pokazatel_raw = raw_text[1]
                _, pokazatel = pokazatel_raw.split(': ') #какой показатель парсим например: Активы нетто 
                pokazatel = pokazatel.replace(' ', '_')

                header_columns = raw_text[3].split(';') #название колонок датасета
                df = pd.DataFrame(columns=header_columns) #
                df_rows = raw_text[4:-1]    #контент датасета

                loc_num = 0
                for i in df_rows:
                    lst_i = i.split(';')
                    df.loc[loc_num] = lst_i
                    loc_num +=1  #index

                # преобразования таблицы
                df = df[df.columns[[2, 5, 6]]] #оставляем только название банка и значение показателя на дату2 и дату1
                df_i = df.to_dict('records')

                dataframes_list.append(df_i)

                time.sleep(np.random.randint(3, 6)) #после прохода по ссылке спим 3 сек

            #цикл завершился  - собираем единую табличку за год внутри одного показателя
            init_table = pd.DataFrame(dataframes_list[0])

            for table in dataframes_list[1:]: #проходимся по всем оставшимся кроме 1 таблички, тк к ней будем все клеить
                table_i = pd.DataFrame(table)
                init_table = init_table.merge(table_i, how = 'outer', on = 'Название банка')

            #обрабатываем таблицу
            init_table.columns = init_table.columns.str.replace(', ', '_')
            init_table.columns = init_table.columns.str.replace(', ', '_')
            init_table.columns = init_table.columns.str.replace('_тыс. рублей', '')

            init_table = init_table.fillna(-1)
            init_table[init_table.columns[1:]] = init_table[init_table.columns[1:]].applymap(
                        lambda x: str(x).replace(",00", '')) #убираем ,00
    
            init_table['pokazatel'] = pokazatel
            pok = '_' + init_table['pokazatel'].loc[0]
            
            total_pokazatel_table = init_table
            
            total_pokazatel_table = total_pokazatel_table.rename(columns = {total_pokazatel_table.columns[1] : total_pokazatel_table.columns[1] + pok,
                                    total_pokazatel_table.columns[2] : total_pokazatel_table.columns[2] + pok,
                                    total_pokazatel_table.columns[3] : total_pokazatel_table.columns[3] + pok,
                                    total_pokazatel_table.columns[4] : total_pokazatel_table.columns[4] + pok,
                                    total_pokazatel_table.columns[5] : total_pokazatel_table.columns[5] + pok,
                                    total_pokazatel_table.columns[6] : total_pokazatel_table.columns[6] + pok,
                                    total_pokazatel_table.columns[7] : total_pokazatel_table.columns[7] + pok,
                                    total_pokazatel_table.columns[8] : total_pokazatel_table.columns[8] + pok,
                                    total_pokazatel_table.columns[9] : total_pokazatel_table.columns[9] + pok,
                                    total_pokazatel_table.columns[10] : total_pokazatel_table.columns[10] + pok,
                                    total_pokazatel_table.columns[11] : total_pokazatel_table.columns[11] + pok,
                                    total_pokazatel_table.columns[12] : total_pokazatel_table.columns[12] + pok})
            total_pokazatel_table = total_pokazatel_table.drop(columns = 'pokazatel') 
            #получили таблицу по показателю за год
            
            dataframes_list_prop.append(total_pokazatel_table) #добавляем ко всем показателям за год
        
        #находимся под циклом для года (написать цикл, который мерджит все элементы в dataframes_list_prop)
        for table in dataframes_list_prop:
            prop_table = prop_table.merge(table, how = 'outer', on = 'Название банка') #получаем таличку по всем показателям за конкретный год

        list_for_years.append(prop_table) #добавляем табличку по всем показателям за конкретный год в таблицу годов

    #выходим из цикла года и мерджим все что внутри list_for_years
    for table in list_for_years:
        final_table = final_table.merge(table, how = 'outer', on = 'Название банка')

    return  final_table # таблица по всем годам и всем параметрам



def data_loader_percentages(years_list, dates2, dates1, property_ids):

    # total_pokazatel_table = pd.DataFrame(columns = ['Название банка'])
    # total_pokazatel_table['Название банка'] = ['Сбербанк', 'ВТБ', 'Газпромбанк']
    
    final_table = pd.DataFrame(columns = ['Название банка']) #показательи за год мерджим с исходной табличкой
    final_table['Название банка'] = ['Сбербанк', 'ВТБ', 'Газпромбанк']
    list_for_years = [] #пока будем скачивать все только для одного года

    for year in tqdm(years_list): #для года
        
        prop_table = pd.DataFrame(columns = ['Название банка']) #показательи за год мерджим
        prop_table['Название банка'] = ['Сбербанк', 'ВТБ', 'Газпромбанк']
        
        dataframes_list_prop = []
        for prop_id in property_ids: #для одного показателя внутри года
            

            dataframes_list = [] #собираем таблицы по одному показателю за год сюда
            for d2, d1 in zip(dates2, dates1): #перебираем даты
                data2 = f"{year}-{d2}-01"
                data1 = f"{year}-{d1}-01"

                url = f'https://www.banki.ru/banks/ratings/export.php?SEARCH_NAME=&SEARCH_REGN=&search[type]=name&sort_param=rating&sort_order=ASC&PROPERTY_ID={prop_id}&REGION_ID=0&date1={data1}&date2={data2}&IS_SHOW_GROUP=0&IS_SHOW_LIABILITIES=0' 
                #выгружаем инфу из url
                response = requests.get(url)

                x = BeautifulSoup(response.content, 'html.parser')
                bald_text = x.text
                raw_text = bald_text.split('\r\n')

                pokazatel_raw = raw_text[1]
                _, pokazatel = pokazatel_raw.split(': ') #какой показатель парсим например: Активы нетто 
                pokazatel = pokazatel.replace(' ', '_')

                header_columns = raw_text[3].split(';') #название колонок датасета
                df = pd.DataFrame(columns=header_columns) #
                df_rows = raw_text[4:-1]    #контент датасета

                loc_num = 0
                for i in df_rows:
                    lst_i = i.split(';')[:-1]
                    df.loc[loc_num] = lst_i
                    loc_num +=1  #index

                # преобразования таблицы
                df = df[df.columns[[2, 5, 6]]] #оставляем только название банка и значение показателя на дату2 и дату1
                df_i = df.to_dict('records')

                dataframes_list.append(df_i)

                time.sleep(np.random.randint(3, 6)) #после прохода по ссылке спим 3 сек

            #цикл завершился  - собираем единую табличку за год внутри одного показателя
            init_table = pd.DataFrame(dataframes_list[0])

            for table in dataframes_list[1:]: #проходимся по всем оставшимся кроме 1 таблички, тк к ней будем все клеить
                table_i = pd.DataFrame(table)
                init_table = init_table.merge(table_i, how = 'outer', on = 'Название банка')

            #     #обрабатываем таблицу
            init_table.columns = init_table.columns.str.replace(', %', '')
            init_table.columns = init_table.columns.str.replace(', ', '_')

            init_table = init_table.fillna(-1)
            init_table[init_table.columns[1:]] = init_table[init_table.columns[1:]].applymap(
                        lambda x: str(x).replace(",00", '')) #убираем ,00
    
            init_table['pokazatel'] = pokazatel
            pok = '_' + init_table['pokazatel'].loc[0]
            
            total_pokazatel_table = init_table

            total_pokazatel_table = total_pokazatel_table.rename(columns = {total_pokazatel_table.columns[1] : total_pokazatel_table.columns[1] + pok,
                                    total_pokazatel_table.columns[2] : total_pokazatel_table.columns[2] + pok,
                                    total_pokazatel_table.columns[3] : total_pokazatel_table.columns[3] + pok,
                                    total_pokazatel_table.columns[4] : total_pokazatel_table.columns[4] + pok,
                                    total_pokazatel_table.columns[5] : total_pokazatel_table.columns[5] + pok,
                                    total_pokazatel_table.columns[6] : total_pokazatel_table.columns[6] + pok,
                                    total_pokazatel_table.columns[7] : total_pokazatel_table.columns[7] + pok,
                                    total_pokazatel_table.columns[8] : total_pokazatel_table.columns[8] + pok,
                                    total_pokazatel_table.columns[9] : total_pokazatel_table.columns[9] + pok,
                                    total_pokazatel_table.columns[10] : total_pokazatel_table.columns[10] + pok,
                                    total_pokazatel_table.columns[11] : total_pokazatel_table.columns[11] + pok,
                                    total_pokazatel_table.columns[12] : total_pokazatel_table.columns[12] + pok})
            total_pokazatel_table = total_pokazatel_table.drop(columns = 'pokazatel') 
            

            #получили таблицу по показателю за год
            
            dataframes_list_prop.append(total_pokazatel_table) #добавляем ко всем показателям за год
        
        #находимся под циклом для года (написать цикл, который мерджит все элементы в dataframes_list_prop)
        for table in dataframes_list_prop:
            prop_table = prop_table.merge(table, how = 'outer', on = 'Название банка') #получаем таличку по всем показателям за конкретный год

        list_for_years.append(prop_table) #добавляем табличку по всем показателям за конкретный год в таблицу годов

    #выходим из цикла года и мерджим все что внутри list_for_years
    for table in list_for_years:
        final_table = final_table.merge(table, how = 'outer', on = 'Название банка')

    return final_table # таблица по всем годам и всем параметрам
