#Лабораторна робота 3
#ФБ-24 Савісько Богдан

from spyre import server
import urllib.request
import datetime
import os
import pandas as pd
import matplotlib.pyplot as plt

mapping = {
    1: 22,
    2: 24,
    3: 23,
    4: 25,
    5: 3,
    6: 4,
    7: 8,
    8: 19,
    9: 20,
    10: 21,
    11: 9,
    13: 10,
    14: 11,
    15: 12,
    16: 13,
    17: 14,
    18: 15,
    19: 16,
    21: 17,
    22: 18,
    23: 6,
    24: 1,
    25: 2,
    26: 7,
    27: 5,
}

def download():
    province_ids = range(1, 28)
    base_url = 'https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={}&year1=1981&year2=2024&type=Mean'

    if not os.path.exists('csv_data'):
        os.makedirs('csv_data')

    for province_id in province_ids:
        current_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        expected_filename = 'VHI_{}_{}.csv'.format(province_id, current_datetime)
        filepath = os.path.join('csv_data', expected_filename)
        
        file_exists = any(filename.startswith('VHI_{}'.format(province_id)) for filename in os.listdir('csv_data'))
        
        if file_exists:
            print('Файл VHI_{} вже існує'.format(province_id))
        else:
            url = base_url.format(province_id)
            try:
                urllib.request.urlretrieve(url, filepath)
                print('Файл {} успішно скачано.'.format(expected_filename))
            except Exception as e:
                print('Помилка при скачуванні файлу для provinceID {}: {}'.format(province_id, str(e)))


def process_csv_files():

    all_dfs = []
    dir_path = "csv_data"

    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        print(f"Directory {dir_path} does not exist or is not a directory")
        return None

    files = os.listdir(dir_path)

    for i, file in enumerate(files):
        if file.endswith(".csv"):
            file_path = os.path.join(dir_path, file)
            df = pd.read_csv(file_path, index_col=False, header=1)
            df['ID'] = i + 1
            all_dfs.append(df)

    df = pd.concat(all_dfs).drop_duplicates().reset_index(drop=True)
    df.columns = df.columns.str.replace('<br>', '').str.replace(" ", "")
    df["year"] = df["year"].str.replace("<tt><pre>", "")
    df = df.drop(df.loc[df['VHI'] == -1].index)
    df = df[df['year'] != '</pre></tt>']
    df = df.loc[(df['ID']!=12) &(df['ID']!=20)]
    df['year'] = df['year'].astype(int)

    df["ID"] = df["ID"].replace(mapping)

    return df


class SimpleApp(server.App):
    title = "Simple App"
    inputs = [
        {
            "type": "dropdown",
            "key": "parameter",
            "label": "Parameter",
            "options": [
                {"label": "SMN", "value": "SMN"},
                {"label": "SMT", "value": "SMT"},
                {"label": "VCI", "value": "VCI"},
                {"label": "TCI", "value": "TCI"},
                {"label": "VHI", "value": "VHI"}
            ],
            "action_id": "update_data"
        },
        {
            "type": 'dropdown',
            "key": 'region',
            "label": 'region',
            "options": [
            {'label': 'Вінницька', 'value': 1},
            {'label': 'Волинська', 'value': 2},
            {'label': 'Дніпропетровська', 'value': 3},
            {'label': 'Донецька', 'value': 4},
            {'label': 'Житомирська', 'value': 5},
            {'label': 'Закарпатська', 'value': 6},
            {'label': 'Запорізька', 'value': 7},
            {'label': 'Івано-Франківська', 'value': 8},
            {'label': 'Київська', 'value': 9},
            {'label': 'Кіровоградська', 'value': 10},
            {'label': 'Луганська', 'value': 11},
            {'label': 'Львівська', 'value': 12},
            {'label': 'Миколаївська', 'value': 13},
            {'label': 'Одеська', 'value': 14},
            {'label': 'Полтавська', 'value': 15},
            {'label': 'Рівенська', 'value': 16},
            {'label': 'Сумська', 'value': 17},
            {'label': 'Тернопільська', 'value': 18},
            {'label': 'Харківська', 'value': 19},
            {'label': 'Херсонська', 'value': 20},
            {'label': 'Хмельницька', 'value': 21},
            {'label': 'Черкаська', 'value': 22},
            {'label': 'Чернівецька', 'value': 23},
            {'label': 'Чернігівська', 'value': 24},
            {'label': 'Республіка Крим', 'value': 25}     
            ],
            "action_id": "update_data"
        },
        {   
            "type": 'text',
            "label": 'Years',
            "value" : '1982-2024',   
            "key": 'years',
            "action_id": "update_data"
        },
        {   
            "type": 'text',
            "label": 'Weeks',
            "value" : '1-4',   
            "key": 'weeks',
            "action_id": "update_data"
        }   
    ]

    controls = [{ 
        "type" : "hidden",
        "id" : "update_data"
    }]

    tabs = ["Table","Plot"]

    outputs = [
        {
            "type":"table",
            "id":"table_id",
            'control_id':'update_data',
            "tab":"Table",
            "on_page_load": True
        },
        {
            "type":"plot",
            "id":"plot_id",
            'control_id':'update_data',
            "tab":"Plot",
            "on_page_load": True
        }                
    ]


    def getData(self,params):
        df = process_csv_files()
        parameter = params.get('parameter')  
        print(parameter)
        region_id = params.get('region')  
        years = params.get('years').split('-')
        weeks = params.get('weeks').split('-') 

        df_filtered = df[(df['year'] >= int(years[0])) & (df['year'] <= int(years[1])) & (df['ID'] == int(region_id))]
        df_filtered = df_filtered.astype({'week': int} ) 
        df_filtered = df_filtered[(df_filtered['week'] >= int(weeks[0])) & (df_filtered['week'] <= int(weeks[1]))]

        selected_columns_df = df_filtered[['year', 'week', parameter]].reset_index(drop=True)        
        
        return selected_columns_df
    
    def getPlot(self, params):
        selected_columns_df = self.getData(params)
        parameter = params.get('parameter')
        years = selected_columns_df['year'].unique()
        
        fig, ax = plt.subplots(figsize=(10, 6))  
        
        for year in years:
            year_data = selected_columns_df[selected_columns_df['year'] == year]
            ax.plot(year_data['week'], year_data[parameter], label=str(year))

        ax.set_xlabel('Weeks')
        ax.set_ylabel(parameter)
        ax.set_title('Data for Parameter {} over Weeks'.format(parameter))
        ax.legend()
        ax.grid(True)
        
        return fig  
        




        
download()
app = SimpleApp()
app.launch()
