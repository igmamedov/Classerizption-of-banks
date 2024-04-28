import pandas as pd 
import numpy as np 

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.impute import KNNImputer
from sklearn.cluster import KMeans, DBSCAN, SpectralClustering
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn import metrics
from sklearn.metrics import pairwise_distances 
from scipy.spatial.distance import cdist


class K_means_cluster:
    '''
    K-means кластеризация с разными параметрами: \n
    - `features_table` - данные
    - `num_clusters` - кол-во кластеров список (перебирает все варианты из списка)
    - `bank_name_column` - названия банков для года
    - `scaling` - StandardScaler для фичей
    - `pca_or_tsne` - 'pca', 'tsne' для визуализации
    - `clustering_before_dimreduce` - 1) кластеризация -> 2) пониж. размерности или наоборот
    - `perplexity` - для t-SNE
    '''

    def __init__(self, features_table, 
                 num_clusters: list, 
                 bank_name_column, 
                 scaling = False, 
                 pca_or_tsne = 'pca', 
                 clustering_before_dimreduce = True, 
                 perplexity = 10):
        
        self.features_table = features_table
        self.num_clusters = num_clusters
        self.bank_name_column = bank_name_column
        self.scaling = scaling
        self.describe_list = []
        self.pca_or_tsne = pca_or_tsne
        self.clustering_before_dimreduce = clustering_before_dimreduce
        self.perplexity = perplexity
    
    def k_means_clustering(self):
        df_st = self.features_table[self.features_table.columns]

        #fillna with KNN
        imputer = KNNImputer(n_neighbors=3, missing_values = np.nan, weights = 'distance')
        self.features_table = imputer.fit_transform(self.features_table)

        if self.scaling:
            scaler = StandardScaler()
            self.features_table = scaler.fit_transform(self.features_table)

        for n in self.num_clusters:
            
            if self.pca_or_tsne == 'pca':
                pca = PCA(n_components=2)
                components = pca.fit_transform(self.features_table)
            
            if self.pca_or_tsne == 'tsne':
                tsne = TSNE(n_components=2, learning_rate='auto', init='pca', perplexity=self.perplexity)
                components = tsne.fit_transform(self.features_table)
                
            # кластеризация ДО понижения размерности
            if self.clustering_before_dimreduce == True:
                k_means = KMeans(n_clusters = n)
                k_means = k_means.fit(self.features_table)
                labels = k_means.predict(self.features_table)
                silhouette_score = metrics.silhouette_score(self.features_table, labels)
                ch_score = metrics.calinski_harabasz_score(self.features_table, labels)
                db_score = metrics.davies_bouldin_score(self.features_table, labels)
                

            # понижение размерности ДО кластеризации
            if self.clustering_before_dimreduce == False:
                k_means = KMeans(n_clusters = n)
                k_means = k_means.fit(components)
                labels = k_means.predict(components)
                silhouette_score = metrics.silhouette_score(components, labels, metric='euclidean')
                ch_score = metrics.calinski_harabasz_score(components, labels)
                db_score = metrics.davies_bouldin_score(components, labels)

            print('silhouette_score:', silhouette_score)
            print('calinski_harabasz_score:', ch_score)
            print('davies_bouldin_score:', db_score)
            
            
            fig = px.scatter(components, x=0, y=1, color=labels)
            fig.update_layout(title=f'Number of clusters = {n}')
            fig.show()
            

            df_st['labels'] = labels
            df_st['bank_name'] = self.bank_name_column # dataframe['bank_name']
            
            n_list = []
            for cluster_label in df_st['labels'].value_counts().keys():
                
                bank_list = df_st[df_st['bank_name'].isin(
                    df_st[df_st['labels'] == cluster_label]['bank_name'].values)]['bank_name'].values
                describe_df = df_st[df_st['bank_name'].isin(
                    df_st[df_st['labels'] == cluster_label]['bank_name'].values)].describe().T[['mean', 'std',
                                                                                                'min','max', '25%', '50%', '75%']]    

                n_list.append((cluster_label,bank_list, describe_df))
        
            self.describe_list.append((n, n_list)) 

    def compute_cluster_stats(self, list_index: int, cluster_index: int) -> tuple[list, pd.DataFrame]:
        '''
        - list_index - номер кол-ва кластеров, cluster_index - номер кластера (цвета)
        - Возвращает tuple: (Банки, попавшие в кластер; дескриптивная статистика по кластеру)
        '''
        element = self.describe_list[list_index]
        number_of_clusters = element[0]
        print('Всего кластеров', number_of_clusters)
        tuples_list = element[1]   
        
        banks_names_dct = {}
        banks_tables_dct = {}
        for tup in tuples_list:
            key = tup[0]
            val1 = tup[1]
            val2 = tup[2]
            banks_names_dct[key] = val1
            banks_tables_dct[key] = val2

        names_list = banks_names_dct[cluster_index]
        dataframe = banks_tables_dct[cluster_index]
        print('Банков попало в кластер:', len(names_list))

        return (names_list, dataframe)
            

def preprocess_data_2019_2021(dataframe, df_stdev_roas, year) -> pd.DataFrame:
    '''
    Преобразует исходные данные для кластеризации, делает новые фичи (ratios)
    '''    

    # правильно ли считается debt?
    dataframe['Debt/TotalAssets'] = ((dataframe['Кредиты предприятиям и организациям']                  
                               + dataframe['Кредиты физическим лицам'] 
                              + dataframe['Бумаги переданные в РЕПО']) / dataframe['Активы нетто'])

    # dataframe['Deposits/TotalAssets'] = (dataframe['ФЛ Счета'] + dataframe['ЮЛ Счета']) / dataframe['Активы нетто'] - было
    dataframe['Deposits/TotalAssets'] = (dataframe['Вклады физических лиц'] + dataframe['Средства предприятий и организаций']) / dataframe['Активы нетто']

    dataframe['TotalLoans/TotalAssets'] = (dataframe['Кредиты предприятиям и организациям'] 
                                        + dataframe['Кредиты физическим лицам']
                                        + dataframe['Выданные МБК']) / dataframe['Активы нетто']
    
    # total loans = debt ?

    dataframe['LDR'] = ((dataframe['Кредиты предприятиям и организациям'] #TotLoans/Deposits
                                        + dataframe['Кредиты физическим лицам']
                                        + dataframe['Выданные МБК']) / (dataframe['Вклады физических лиц']          # было (dataframe['ФЛ Счета'] + dataframe['ЮЛ Счета']))
                                                                        + dataframe['Средства предприятий и организаций']))

    dataframe['NPL/TotalLoans'] = ((dataframe['ФЛ Просроченная задолженность'] 
                                + dataframe['ЮЛ Просроченная задолженность']) / (dataframe['Кредиты предприятиям и организациям'] 
                                                                                + dataframe['Кредиты физическим лицам']
                                                                                + dataframe['Выданные МБК']))

    dataframe = dataframe.merge(df_stdev_roas[['bank_name', f'std_ROA_{year}']], how='left', on='bank_name')
    dataframe['Z-score'] = (dataframe['Рентабельность активов-нетто'] + dataframe['Н1'])/dataframe[f'std_ROA_{year}']


    # сравнить
    # dataframe['LiquidAssetsRatio'] = (dataframe['Денежные средства в кассе'] 
    # + dataframe['Размещенные МБК в ЦБ РФ']
    # + dataframe['Бумаги переданные в РЕПО']
    # + dataframe['НОСТРО-счета']) / dataframe['Активы нетто']

    dataframe['LiquidAssetsRatio'] = (dataframe['Высоколиквидные активы']) / dataframe['Активы нетто']

    dataframe = dataframe.rename(columns = {'Рентабельность активов-нетто' : 'ROA',
                          'Рентабельность капитала' : 'ROE', 
                          'Уровень просроченной задолженности по кредитному портфелю' : 'NPL Ratio',
                          'Уровень резервирования по кредитному портфелю' : 'NPL Coverage', 
                          'Н2' : 'Н2 liquidity',
                          'Н3' : 'Н3 liquidity',
                          'Активы нетто': 'Total Assets',
                          'Капитал (по форме 123)' : 'Капитал',
                          'Уровень обеспечения кредитного портфеля залогом имущества' : 'LTV',
                          'Н1' : 'Н1 CAR'})
    
    dataframe['КредитыЮЛ/TotalAssets'] = dataframe['Кредиты предприятиям и организациям'] / dataframe['Total Assets']
    dataframe['КредитыФЛ/TotalAssets'] = dataframe['Кредиты физическим лицам'] / dataframe['Total Assets']
    dataframe['ВыданныеМБК/TotalAssets'] = dataframe['Выданные МБК'] / dataframe['Total Assets']
    dataframe['ПривлеченныеМБК/TotalAssets'] = dataframe['Привлеченные МБК'] / dataframe['Total Assets']
    dataframe['log_TotalAssets'] = np.log1p(dataframe['Total Assets'])
    dataframe['Капитал/Активы'] = dataframe['Капитал'] / dataframe['Total Assets']

    X = dataframe[[
    'Н1 CAR',
    'Н2 liquidity', 
    'Н3 liquidity',
    'ROA',
    'ROE',
    'LTV',
    'NPL Ratio',
    'NPL Coverage',
    
    'Debt/TotalAssets',
    'Deposits/TotalAssets',
    'TotalLoans/TotalAssets',
    'LDR',
    'NPL/TotalLoans',
    'LiquidAssetsRatio',
    'Z-score',
    
    'КредитыЮЛ/TotalAssets',
    'КредитыФЛ/TotalAssets',
    'ВыданныеМБК/TotalAssets',
    'ПривлеченныеМБК/TotalAssets',
    'Капитал/Активы',
    'log_TotalAssets'
    ]]

    if year == 2021:
        X = dataframe[[
        'Н1 CAR',
        'Н2 liquidity', 
        'Н3 liquidity',
        'ROA',
        'ROE',
        'LTV',
        'NPL Ratio',
        'NPL Coverage',
        
        'Debt/TotalAssets',
        'Deposits/TotalAssets',
        'TotalLoans/TotalAssets',
        'LDR',
        'NPL/TotalLoans',
        'LiquidAssetsRatio',
        'Z-score',
        
        'КредитыЮЛ/TotalAssets',
        'КредитыФЛ/TotalAssets',
        'ВыданныеМБК/TotalAssets',
        'ПривлеченныеМБК/TotalAssets',
        'Капитал/Активы',
        'log_TotalAssets',

        'gos_sobstv',
        'foreign',
        'system'
        ]]
    

    for col in X.columns:
        X.loc[X[col] == np.inf, col] = np.nan

    scaler = MinMaxScaler()
    zscore_scaled = scaler.fit_transform(X[['Z-score']])
    npl_scaled = scaler.fit_transform(X[['NPL Ratio']])
    X['Z-score'] = zscore_scaled
    X['NPL Ratio'] = npl_scaled

    return X

def preprocess_data2023(dataframe, df_stdev_roas):
    year = 2023
    
    dataframe['Debt/TotalAssets'] = ((dataframe['Кредиты предприятиям и организациям']                  
                               + dataframe['Кредиты физическим лицам']) / dataframe['Total Assets'])
    
    dataframe['Deposits/TotalAssets'] = (dataframe['Вклады физических лиц'] 
                                     + dataframe['Средства предприятий и организаций']) / dataframe['Total Assets']
    
    dataframe['TotalLoans/TotalAssets'] = (dataframe['Кредиты предприятиям и организациям'] 
                                        + dataframe['Кредиты физическим лицам']
                                        + dataframe['Выданные МБК']) / dataframe['Total Assets']
    
    dataframe['LDR'] = ((dataframe['Кредиты предприятиям и организациям'] #TotLoans/Deposits
                                        + dataframe['Кредиты физическим лицам']
                                        + dataframe['Выданные МБК']) / (dataframe['Вклады физических лиц'] 
                                                                         + dataframe['Средства предприятий и организаций']))
    
    dataframe = dataframe.merge(df_stdev_roas[['bank_name', f'std_ROA_{year}']], how='left', on='bank_name')
    dataframe['Z-score'] = (dataframe['ROA'] + dataframe['Н1 CAR'])/dataframe[f'std_ROA_{year}']
    
    dataframe['LiquidAssetsRatio'] = (dataframe['Высоколиквидные активы']) / dataframe['Total Assets']
    
    dataframe['КредитыЮЛ/TotalAssets'] = dataframe['Кредиты предприятиям и организациям'] / dataframe['Total Assets']
    dataframe['КредитыФЛ/TotalAssets'] = dataframe['Кредиты физическим лицам'] / dataframe['Total Assets']
    dataframe['ВыданныеМБК/TotalAssets'] = dataframe['Выданные МБК'] / dataframe['Total Assets']
    dataframe['ПривлеченныеМБК/TotalAssets'] = dataframe['Привлеченные МБК'] / dataframe['Total Assets']
    dataframe['log_TotalAssets'] = np.log1p(dataframe['Total Assets'])
    dataframe['Капитал/Активы'] = dataframe['Капитал'] / dataframe['Total Assets']
    
    X = dataframe[[
    'Н1 CAR',
    'Н2 liquidity', 
    'Н3 liquidity',
    'ROA',
    'ROE',
    #'LTV', # нет данных
    'NPL Ratio',
    #'NPL Coverage',
    
    'Debt/TotalAssets',
    'Deposits/TotalAssets',
    'TotalLoans/TotalAssets',
    'LDR',
    #'NPL/TotalLoans',
    'LiquidAssetsRatio',
    'Z-score',
    
    'КредитыЮЛ/TotalAssets',
    'КредитыФЛ/TotalAssets',
    'ВыданныеМБК/TotalAssets',
    'ПривлеченныеМБК/TotalAssets',
    'Капитал/Активы',
    'log_TotalAssets',
        
    'gos_sobstv',
    'foreign',
    'system'
    ]]
    
    for col in X.columns:
        X.loc[X[col] == np.inf, col] = np.nan

    scaler = MinMaxScaler()
    zscore_scaled = scaler.fit_transform(X[['Z-score']])
    npl_scaled = scaler.fit_transform(X[['NPL Ratio']])
    ldr_scaled = scaler.fit_transform(X[['LDR']])
    
    X['Z-score'] = zscore_scaled
    X['NPL Ratio'] = npl_scaled
    X['LDR'] = ldr_scaled
        
    return X

def labels_2021_2023(dataframe) -> pd.DataFrame:
    '''
    Создает 3 фичи:
    - Банк государственный или частный
    - Банк инострынный или отечественный
    - Банк системнозначимый или нет
    '''
    #фича - банк государственный или частный (1 - гос, 0 - частный)
    dataframe['gos_sobstv'] = 0
    dataframe.loc[dataframe['bank_name'].isin(['Ак Барс Банк', 
                                       'АКИБАНК', 
                                       'Алмазэргиэнбанк', 
                                      'Банк ДОМ.РФ',
                                       'Банк «Открытие»',
                                       'БМ-Банк',
                                       'ВБРР',
                                       'ВТБ',
                                       'Газпромбанк',
                                       'Еврофинанс Моснарбанк',
                                       'МСП Банк',
                                       'Новикомбанк',
                                       'Почта Банк',
                                       'Почтобанк',
                                       'Просто|Банк',
                                       'ПСБ',
                                       'РНКБ',
                                       'Россельхозбанк',
                                       'Росэксимбанк',
                                       'Сбербанк',
                                       'Хакасский муниципальный банк']), 'gos_sobstv'] = 1
    
    # банк инострынный или нет (1 - иностранный)
    dataframe['foreign'] = 0
    dataframe.loc[dataframe['bank_name'].isin(['ЮниКредит Банк', 
                                       'Ю Би Эс Банк', 
                                       'Райффайзен Банк', 
                                       'Эм-Ю-Эф-Джи Банк (Евразия)',
                                       'Эйч-Эс-Би-Си Банк (HSBC)',
                                       'Фольксваген Банк РУС',
                                       'Ури Банк',
                                       'Тойота Банк',
                                       'Сумитомо Мицуи Рус Банк',
                                       'Ситибанк',
                                       'ОТП Банк',
                                       'Натиксис Банк',
                                       'Мир Бизнес Банк',
                                       'Мидзухо Банк',
                                       'КЭБ ЭйчЭнБи Банк',
                                       'Кредит Европа Банк',
                                       'Креди Агриколь КИБ',
                                       'Коммерческий Индо Банк',
                                       'Коммерцбанк (Евразия)',
                                       'Ишбанк',
                                       'ИНГ Банк',
                                       'ИК Банк',
                                       'Зираат Банк',
                                       'Еврофинанс Моснарбанк',
                                       'Дойче Банк',
                                       'Дж. П. Морган Банк Интернешнл',
                                       'ДенизБанк Москва',
                                       'Голдман Сакс Банк',
                                       'БНП Париба Банк',
                                       'БМВ Банк',
                                       'Банк «Центр-инвест»',
                                       'Банк «МБА-МОСКВА»',
                                       'Банк Кредит Свисс (Москва)',
                                       'Банк Интеза',
                                       'Америкэн Экспресс Банк',
                                       'Алеф-Банк',
                                       'АКБ «БЭНК ОФ ЧАЙНА»',
                                       'АйСиБиСи Банк',
                                       'Азия-Инвест Банк',
                                       'Азиатско-Тихоокеанский банк (АТБ)',
                                       'SEB',
                                       'SBI Банк']), 'foreign'] = 1
    
    # банк системнозначимый или нет (1 -да) с 2021 года!
    dataframe['system'] = 0
    dataframe.loc[dataframe['bank_name'].isin(['Россельхозбанк', 'Райффайзен Банк', 'ПСБ', 'Тинькофф Банк',
                                      'Росбанк', 'Банк «Открытие»', 'Московский кредитный банк (МКБ)', 
                                       'Сбербанк', 'Альфа-Банк', 'ВТБ', 'Совкомбанк', 'ЮниКредит Банк']), 'system'] = 1
    
    return dataframe

def knn_nan_inputer(dataframe):
    imputer = KNNImputer(n_neighbors=3, missing_values=np.nan, weights = 'distance')
    df_transformed = imputer.fit_transform(dataframe)
    return df_transformed
                


def visuals_boxplot(dataframe, year = None):
    plt.figure(figsize=(24,28))
    for i in range(0, dataframe.shape[1]):
        plt.subplot(10,4,i+1)
        sns.boxplot(x=dataframe[dataframe.columns[i]], palette='viridis')
        plt.title(dataframe.columns[i], fontsize=20)
        plt.xlabel(' ')
        plt.tight_layout()
        plt.suptitle(f'Year: {year}', fontsize=30)
        plt.subplots_adjust(top=0.88)

def visuals_kdeplot(dataframe, hue = False, hue_col = None, year = None):
    plt.figure(figsize=(24,28))
    for i in range(0, dataframe.shape[1]):
        plt.subplot(10,4,i+1)
        if hue == True:
            sns.kdeplot(x=dataframe[dataframe.columns[i]], palette='viridis', shade=True, hue = dataframe[hue_col])
        else:
            sns.kdeplot(x=dataframe[dataframe.columns[i]], palette='viridis', shade=True)
        plt.title(dataframe.columns[i], fontsize=20)
        plt.xlabel(' ')
        plt.tight_layout()
        plt.suptitle(f'Year: {year}', fontsize=30)
        plt.subplots_adjust(top=0.88)

def visuals_violinplot(dataframe, year = None):
    plt.figure(figsize=(24,28))
    for i in range(0, dataframe.shape[1]):
        plt.subplot(10,4,i+1)
        sns.violinplot(x=dataframe[dataframe.columns[i]], palette='viridis', shade=True)
        plt.title(dataframe.columns[i], fontsize=20)
        plt.xlabel(' ')
        plt.tight_layout()
        plt.suptitle(f'Year: {year}', fontsize=30)
        plt.subplots_adjust(top=0.88)
