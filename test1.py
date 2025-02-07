import PySimpleGUI as sg
from data_handler import load_and_prehandle_xlsx

# 示例数据

data = {
    "张三": {"年龄": 25, "学历": "本科", "职业": "工程师"},
    "李四": {"年龄": 30, "学历": "硕士", "职业": "教师"},
    "王五": {"年龄": 28, "学历": "博士", "职业": "研究员"},
}
# data = load_and_prehandle_xlsx(
#     r'C:\Users\86781\VS_Code_Project\form_filler_new\assets\xlsx_database.xlsx',
#     'data',
#     r'C:\Users\86781\VS_Code_Project\form_filler_new\assets\xlsx_database.xlsx',
#     'key'
# )[1]

# 获取属性列表（所有人物共享）
attributes = list(next(iter(data.values())).keys())

# 定义布局
layout = [
    [
        sg.Listbox(values=list(data.keys()), size=(15, 10), key="-PEOPLE-", enable_events=True),
        sg.Listbox(values=attributes, size=(15, 10), key="-ATTRIBUTES-", enable_events=True),
        sg.Multiline("", size=(30, 10), key="-VALUE-", enable_events=True)
    ],
    [
        sg.Button("添加人物", key="-ADD_PERSON-"),
        sg.Button("删除人物", key="-REMOVE_PERSON-"),
        sg.Button("添加属性", key="-ADD_ATTRIBUTE-"),
        sg.Button("删除属性", key="-REMOVE_ATTRIBUTE-")
    ],
    [
        sg.Button("更新", key="-UPDATE-")
    ]
]

# 创建窗口
window = sg.Window("字典查看器", layout)

selected_person = None
selected_attribute = None

# 事件循环
while True:
    event, values = window.read()
    
    if event == sg.WINDOW_CLOSED:
        break
    
    if event == "-PEOPLE-":
        selected_person = values["-PEOPLE-"][0] if values["-PEOPLE-"] else None
        if selected_person:
            window["-ATTRIBUTES-"].update(values=attributes)
            selected_attribute = None
            window["-VALUE-"].update("")
    
    if event == "-ATTRIBUTES-" and selected_person:
        selected_attribute = values["-ATTRIBUTES-"][0] if values["-ATTRIBUTES-"] else None
        if selected_attribute:
            window["-VALUE-"].update(data[selected_person][selected_attribute])
    
    if event == "-VALUE-" and selected_person and selected_attribute:
        data[selected_person][selected_attribute] = values["-VALUE-"]
        window["-VALUE-"].update(data[selected_person][selected_attribute])
    
    if event == "-UPDATE-" and selected_person and selected_attribute:
        data[selected_person][selected_attribute] = values["-VALUE-"]
        sg.popup("数据已更新")
        window["-VALUE-"].update(data[selected_person][selected_attribute])
    
    if event == "-ADD_PERSON-":
        new_person = sg.popup_get_text("输入新人物名称：")
        if new_person and new_person not in data:
            data[new_person] = {attr: "" for attr in attributes}
            window["-PEOPLE-"].update(values=list(data.keys()))
    
    if event == "-REMOVE_PERSON-" and selected_person:
        del data[selected_person]
        selected_person = None
        window["-PEOPLE-"].update(values=list(data.keys()))
        window["-ATTRIBUTES-"].update(values=[])
        window["-VALUE-"].update("")
    
    if event == "-ADD_ATTRIBUTE-":
        new_attr = sg.popup_get_text("输入新属性名称：")
        if new_attr and new_attr not in attributes:
            attributes.append(new_attr)
            for person in data:
                data[person][new_attr] = ""
            window["-ATTRIBUTES-"].update(values=attributes)
    
    if event == "-REMOVE_ATTRIBUTE-" and selected_attribute:
        attributes.remove(selected_attribute)
        for person in data:
            del data[person][selected_attribute]
        selected_attribute = None
        window["-ATTRIBUTES-"].update(values=attributes)
        window["-VALUE-"].update("")

# 关闭窗口
window.close()
