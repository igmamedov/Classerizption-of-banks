import pandas as pd 
import numpy as np 

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn import metrics 
from scipy.spatial.distance import cdist


class K_means_cluster:
    def __init__(self, features_table, num_clusters: list, bank_name_column, scaling = False):
        self.features_table = features_table
        self.num_clusters = num_clusters
        self.bank_name_column = bank_name_column
        self.scaling = scaling
        self.describe_list = []
    
    def k_means_clustering(self):
        df_st = self.features_table[self.features_table.columns]

        #fillna with KNN
        imputer = KNNImputer(n_neighbors=2, missing_values = np.nan, weights = 'distance')
        self.features_table = imputer.fit_transform(self.features_table)

        if self.scaling:
            scaler = StandardScaler()
            self.features_table = scaler.fit_transform(self.features_table)

        #clustering
        for n in self.num_clusters:
            n_list = []
            k_means = KMeans(n_clusters = n)
            k_means = k_means.fit(self.features_table)
            labels = k_means.predict(self.features_table)

            pca = PCA(n_components=2)
            components = pca.fit_transform(self.features_table)
            
            fig = px.scatter(components, x=0, y=1, color=labels)
            fig.update_layout(title=f'Num of clusters = {n}')
            # fig.add_annotation(
            #     xref="x domain",
            #     yref="y domain",
            #     # The arrow head will be 25% along the x axis, starting from the left
            #     x=0.25,
            #     # The arrow head will be 40% along the y axis, starting from the bottom
            #     y=0.1,
            #     text="An annotation referencing the axes",
            #     arrowhead=2,
            # )
            fig.show()


            df_st['labels'] = labels
            df_st['bank_name'] = self.bank_name_column # df_2019['bank_name']
            
            for cluster_label in df_st['labels'].value_counts().keys():
                
                bank_list = df_st[df_st['bank_name'].isin(
                    df_st[df_st['labels'] == cluster_label]['bank_name'].values)]['bank_name'].values
                describe_df = df_st[df_st['bank_name'].isin(
                    df_st[df_st['labels'] == cluster_label]['bank_name'].values)].describe().T[['mean', 'std','min','max', '25%', '50%', '75%']]                                                                                                              
                
                n_list.append((n, cluster_label,bank_list, describe_df))
        
            self.describe_list.append(n_list) 

    def show_analytics(self, list_index, cluster_index):
        print('Всего кластеров:', self.describe_list[3][cluster_index][0])
        print('Номер кластера:', self.describe_list[3][cluster_index][1])
        print('Банков попало в кластер:',len(self.describe_list[3][cluster_index][2]))
        return self.describe_list[list_index][cluster_index][2:]




                