from data_handler import load_and_prehandle_xlsx

path = r'C:\Users\86781\VS_Code_Project\form_filler_new\assets\xlsx_database.xlsx'
data_sheet = 'data'
key_sheet = 'key'

key_dict, data_dict = load_and_prehandle_xlsx(path, data_sheet, path, key_sheet)
for values in key_dict.values():
    for value in values:
        print(value)
pass