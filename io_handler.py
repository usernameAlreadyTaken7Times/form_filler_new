import json
import pandas as pd


def prehandle_xlsx(path: str) -> dict:
    '''Prehandle the .xlsx file as the data source for further use. 
    The .xlsx file should contain two sheets named "key" and "data".
    The content in these two sheets are returned in dicts.'''

    sheets = pd.read_excel(path, sheet_name=['key', 'data'])

    # replace the `_x000D_` in sheets
    df_key = sheets['key'].map(lambda x: x.replace('_x000D_\n', '').strip() if isinstance(x, str) else x)
    df_data = sheets['data'].map(lambda x: x.replace('_x000D_\n', '').strip() if isinstance(x, str) else x)

    key_dict: dict = {}
    df_key.fillna('', inplace=True)
    key_dict = df_key.set_index(df_key.columns[0]).T.to_dict('list')
    for key in key_dict:
        for i in range(len(key_dict[key])):
            if key_dict[key][-1] == '':
                key_dict[key] = key_dict[key][:-1]
            else:
                break
    
    data_dict: dict = {}
    data_dict = {
        row['姓名']: {
            **row.to_dict(),  # 将行数据转为字典
            "姓名": row['姓名'],  # 显式添加姓名字段
        }
        for _, row in df_data.iterrows()
    }
    return key_dict, data_dict

def write_xlsx(key_dict: dict, data_dict: dict):
    '''Write the dicts in Data_Handler back to the .xlsx file. Should be called when terminating the program.'''
    # TODO: the function to write data_dict and key_dict back to .xlsx file after using the app.
    pass

def load_setting_from_json(json_file_path: str) -> str:
    '''This function reads the input json file and retrives .xlsx filepath. '''
    file_path = json_file_path
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    excel_datapath = data.get("xlsx_filepath")
    return excel_datapath


key_dict, data_dict = prehandle_xlsx(r'C:\Users\86781\VS_Code_Project\form_filler_new\assets\xlsx_database.xlsx')
pass