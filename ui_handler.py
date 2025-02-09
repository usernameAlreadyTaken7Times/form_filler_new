import PySimpleGUI as sg
from error_list import Errors
from config_handler import ConfigSingleton

import threading
from shared_queue import broadcaster

import time
import copy
from deepdiff import DeepDiff
import queue

from queue import Queue # only for ide's static analysis


class UI_Handler(threading.Thread):
    '''This UI_Handler deals with interacting with Users directly, including receiving graphic rendering commands.
    It should be in the same layer as keyboard & business module.
    Meantime, the config file is also loaded here, from ui interface. It can then be used in other modules.
    '''
    def __init__(self, config_filepath: str): 
        
        # vairables
        self.config_filepath = config_filepath
        self.window_running = False
        

        self.data_dict: dict[str, dict]
        self.key_dict: dict[str, list]
        self.data_dict, self.key_dict = self.get_dicts_content_from_data_handler()

        # define main GUI window
        main_window_layout = [
            [sg.Text("Form_Filler v0.3", font=("Arial", 12, "bold"), text_color="white")],
            [sg.Text("an extended copy/paste service", font=("Arial", 9), text_color="white")],
            [sg.HorizontalSeparator()],
            
            [sg.Text("Run/Terminate", font=("Arial", 9), text_color="white")],
            [sg.Button("Run", size=(8, 1), font=("Arial", 8), key="KEY_run"), 
              sg.Button("Terminate", size=(8, 1), font=("Arial", 8), key="KEY_terminate")],
            [sg.Text("or Ctrl+R / Ctrl+T", font=("Arial", 8), text_color="white")],
            [sg.HorizontalSeparator()],

            [sg.Text("Modifier", font=("Arial", 9), text_color="white")],
            [sg.Button("Data", size=(8, 1), font=("Arial", 8), key="KEY_main_data_modifier"),
             sg.Button("Alias", size=(8, 1), font=("Arial", 8), key="KEY_main_alias_modifier")],
            [sg.HorizontalSeparator()], 

            [sg.Text("test test", font=("Arial", 8), text_color="blue")]
        ]

        self.window = sg.Window("FFv0.3", main_window_layout, resizable=True, keep_on_top=True, finalize=True)
        self.window.refresh()

        # window init setting
        self.queue_ui: Queue = broadcaster.register('ui')

    # start/stop functions
    def start_GUI(self):
        '''starts the GUI program and show the window'''
        if not self.window_running:
            self.window_running = True
        else:
            raise Errors.ServiceStatusError('GUI status error')
        
    def stop_GUI(self):
        '''stops the GUI program and hide the window'''
        if self.window_running:
            self.window_running = False
            self.window.close()

    # ui main thread
    def run_ui(self):
        '''ui main thread, controls the ui logic.'''
        
        while True:
            event, values = self.window.read()
            # TODO: change ui_handler into new process, instead of thread, cause PySimpleGUI
            # is not allowed running in a sub thread!
            
            try:
                tmp_news = self.poll_messages()
            except:
                tmp_news = None

            # send signals
            # if event == xx: # ui butten to get ecp value
            #     pass # send queue info

            # receive signals
            if tmp_news and tmp_news['soruce'] == 'keyboard' and tmp_news['command'] == 'set_ecp_value':
                # TODO: set ecp value on gui
                pass

            # confirm/load config file related
            if event == 'KEY_main_data_modifier':
                self.popup_data_dict_modifier()
                self.set_data_dict_content_to_data_handler() # sync the data_dict and key_dict with updates
            
            if event == 'KEY_main_alias_modifier':
                self.popup_alias_dict_modifier()
                # self.set_key_dict_content_to_data_handler() # sync
                pass

            # terminate GUI program
            if event == 'KEY_terminate' or event == sg.WINDOW_CLOSED:
                self.stop_GUI()
                print('call stop_gui function and stop')
                break
 

            # mark queue task as done, as long as tmp_news is not None
            if isinstance(tmp_news, Queue):
                tmp_news.task_done()
                print('task done')


    # thread related functions
    def get_dicts_content_from_data_handler(self):
        '''use queue to request data_dict and key_dict from data_handler, should be called by init'''
        # shared_queue.put({{'source':'ui','command':'get_dicts', 'content': ''}})
        # while True:
        #     tmp_news = shared_queue.get()
        #     if tmp_news['source'] == 'business' and tmp_news['command'] == 'send_dicts':
        #         break
        # return tmp_news['content']

        # for test only
        data = {'王萍': {'姓名': '王萍',
                  '英文姓名': 'Wang, Ping',
                    '性别': '女', '年龄': 'xx',
                      '出生日期': 'xxxx-xx-xx',
                        '邮箱': 'nefuwangping@outlook.com',
                          '职务': '讲师 (未来的大教授)',
                            '研究方向': '多糖基荧光、磷光碳点的制备与应用；生物质基光敏剂在原子转移自由基聚合中的应用；生物质基光响应性功能材料的构筑与应用',
                              '经历': '2024.03-至今，西南林业大学，材料与化学工程学院，讲师 2017.09-2023.12，东北林业大学，林业工程，工学博士 2021.10-2023-08，德国下莱茵应用...究所，联合培养博士 2013.09-2017.06，北华大学，木材科学与工程，工学学士',
                                '学术成果': '近年来的研究围绕着林木资源化学转化与高值化利用，生物质基光响应性材料的构筑与应用等方面。与国内外知名高校、研究所具有密切的交流与合作。累计发表 sci 论文 6 篇，授权发明专利 1 项，主持项目 1 项。'},
                '高伟': {'姓名': '高伟',
                '英文姓名': 'Gao, Wei',
                    '性别': '男',
                    '年龄': 'xx',
                        '出生日期': 'xxxx-xx-xx',
                        '邮箱': 'weigao@swfu.edu.cn',
                            '职务': '教授',
                            '研究方向': '木质先进功能材料、木材胶黏剂功能化、木文化产业',
                                '经历': '2019 年 - 至今      西南林业大学，教授 2012 年 -2019 年   西南林业大学，副教授 2010 年 -2012 年   西南林业大学，讲师 2007 年 -2010 年   北...年   北京林业大学，获硕士学位 2000 年 -2004 年   北京林业大学，获学士学位',
                                '学术成果': '西南林业大学木材科学与工程系主任，林业工程一级学科博士点、木材科学与技术二级学科硕士点负责人。主要从事木质先进功能材料、木材胶黏剂功能化、木文化产业研究。主持完成/在研国...人获得 2023 年云南省优秀硕士学位论文；年均 1-2 人获得校级或院级优秀本科毕业论文。'},
                 '杨龙': {'姓名': '杨龙', '英文姓名': 'Yang, Long', '性别': '男', '年龄': 'xx', '出生日期': 'xxxx-xx-xx', '邮箱': 'long133109070@126.com', '职务': '研究员', '研究方向': '木竹生物基复合材料/超分子杂化新材料', '经历': '2019.08-至今       西南林业大学，材料与化学工程学院，研究员 2018.05-2019.08    西南林业大学，材料科学与工程学院，研究员 (特聘)2017....士学位 2008.09-2012.07    云南大学，化学科学与工程学院，获学士学位', '学术成果': '近年来主要从事木竹生物基复合材料、超分子杂化新材料方面的研究。主持国家自然科学基金面上项目和地区项目、云南省基础研究计划重点和优青项目、云南省农业联合重点项目等 10 余项；...南省高层次人才培养支持计划“青年拔尖人才”、云南省中青年学术和技术带头人后备人才等。'}, '吴章康': {'姓名': '吴章康', '英文姓名': 'Wu, Zhangkang', '性别': '男', '年龄': 'xx', '出生日期': 'xxxx-xx-xx', '邮箱': '764430266@qq.com', '职务': '教授', '研究方向': '木质复合材料', '经历': '2005 年 - 至今      西南林业大学，教授\n\n2000 年 -2005 年    西南林业大学，副教授\n\n1999 年 -2002 年    南京林业大学，获木材科学与技术博士学...技术硕士学位\n\n1984 年 -1988 年    南京林业大学，获木材科学与工程学士学位', '学术成果': '主持完成国家自然科学基金项目 1 项，主持完成云南省应用基础研究基金项目 2 项，参与完成包括国家自然科学基金项目在内的省部级以上科研项目数十项；以第一/通讯作者在行业代表性的知名期刊发表论文 50 余篇。'}, '邱坚': {'姓名': '邱坚', '英文姓名': 'Qiu, Jian', '性别': '男', '年龄': 'xx', '出生日期': 'xxxx-xx-xx', '邮箱': 'qiujian@swfu.edu.cn', '职务': '教授', '研究方向': '木材解剖与保护', '经历': '1987 年 - 至今       西南林业大学，二级教授 2001 年 -2004 年    东北林业大学，获博士学位 1997 年 -2000 年    西南林业大学，获硕士学位 1983 年...验室访问学者 2022.12-2023.2       荷兰自然多样性中心高级访问学者', '学术成果': '近年来主要从事木材解剖与保护及木材生物学研究。主持国家自然科学基金面上项目 5 项，云南省自然科学基金重点项目 2 项，面上项目 2 项，国家十三五重点研发项目子课题 1 项，参与国家自...究生出国留学获得博士学位，指导国外留学研究生 1 名，12 名研究生获得国家和省级奖学金。'}, '周晓剑': {'姓名': '周晓剑', '英文姓名': 'Zhou, Xiaojian', '性别': '男', '年龄': 'xx', '出生日期': 'xxxx-xx-xx', '邮箱': 'xiaojianzhou@hotmail.com', '职务': '研究员', '研究方向': '木材胶黏剂及树脂材料', '经历': '2014 年 - 至今       西南林业大学，研究员\n\n2014 年 -2016 年    瑞典吕勒奥理工大学，生物质复合材料，博士后\n\n2010 年 -2013 年        法...科学与技术，硕士\n\n2002 年 -2006 年    南京林业大学，木材科学与工程，学士', '学术成果': '周晓剑博士主要从事木材胶黏剂及树脂复合材料的应用基础研究，践行将论文写在大地、写在生产一线，为合作企业研发能力和员工技术水平提升，实现技术脱贫和为乡村振兴建设做出贡献，累...本科生，年均有 1-2 名本科生获得校级优秀毕业论文，多名研究生获得国家和省政府奖学金。'}, '罗蓓': {'姓名': '罗蓓', '英文姓名': 'Luo, Pei', '性别': '女', '年龄': 'xx', '出生日期': 'xxxx-xx-xx', '邮箱': 'beiluoswfu@qq.com', '职务': '副教授', '研究方向': '木材科学与技术', '经历': '2004 年 - 至今       西南林业大学，材料与化学工程学院\n\n2007 年 -2013 年    北京林业大学，获博士学位\n\n2001 年 -2004 年    中国林业科学研究院，获硕士学位\n\n1997 年 -2001 年    北京林业大学大学，获学士学位', '学术成果': '申报人近 5 年来主要从事木材科学与技术方向的研究，具体研究内容涉及木质资源材料的构造与材性、木质资源材料的功能性改良、木结构建筑的保护与改性。'}}
        key = {'姓名': ['名称', '名字', '称号', 'Name'],
          '英文姓名': ['英文名称', '英文', '外语称号', 'English name'],
            '性别': ['Gender', 'Sex'], '年龄': ['岁数', '寿数', 'Age'],
              '出生日期': ['出生年月日', 'Birth date'],
                '邮箱': ['电子邮箱', '电子邮箱地址', '邮件地址', '电子邮件'],
                  '职务': ['头衔', '职责'], '研究方向': ['科研主题', '科研方向'],
                    '经历': ['简历'], '学术成果': ['学术成就', '学术荣誉', '成就', '荣誉', '论文', '专利']}
        return data, key

    def set_dicts_content_to_data_handler(self):
        '''use queue to send data_dict and key_dict to data_handler, should be called every time the dicts are changed from modifier'''
        # shared_queue.put({'source': 'ui', 'coommand': 'set_dicts', 'content': (self.data_dict, self.key_dict)})

        # for test only
        pass

    def set_data_dict_content_to_data_handler(self):
        '''use queue to send data_dict to data_handler, should be called every time the dict changed from modifier'''
        # shared_queue.put({'source': 'ui', 'coommand': 'set_data_dict', 'content': self.data_dict})

        # for test only
        pass

    def set_key_dict_content_to_data_handler(self):
        '''use queue to send key_dict to data_handler, should be called every time the dict changed from modifier'''
        # shared_queue.put({'source': 'ui', 'coommand': 'set_key_dict', 'content': self.key_dict})

        # for test only
        pass


    def popup_data_dict_modifier(self):
        '''pop up a new data_dict modifier window'''

        tmp_data_dict: dict[str, dict]
        tmp_data_dict = copy.deepcopy(self.data_dict) # create a deepcopy of data_dict for in-function use
        selected_character = None
        selected_key = None
        key = list(next(iter(tmp_data_dict.values())).keys())

        # popup data_dict modifier window layout
        popup_data_window_layout = [
            [sg.Text("characters", font=("Arial", 9), text_color="white", size=(10, 1)),
             sg.Text("keys", font=("Arial", 9), text_color="white", size=(12, 1)),
             sg.Text("values", font=("Arial", 9), text_color="white", size=(16, 1))],
            [sg.Listbox(values=list(tmp_data_dict.keys()), size=(8, 10), key="KEY_data_modifier_character", enable_events=True),
             sg.Listbox(values=key, size=(8, 10), key="KEY_data_modifier_key", enable_events=True),
             sg.Multiline("", size=(24, 10), key="KEY_data_modifier_value", enable_events=True)],
            [sg.Button("character_add", key="KEY_add_character"),
             sg.Button("character_del", key="KEY_del_character"),
             sg.Button("key_add", key="KEY_add_key"),
             sg.Button("key_del", key="KEY_del_key")],
            [sg.Button("update", key="KEY_data_modifier_update"), 
             sg.Button('exit', key='KEY_data_modifier_exit')]
         ]
        
        data_window = sg.Window('data_dict modifier', popup_data_window_layout, keep_on_top=True, finalize=True)
        data_window.force_focus()

        # run loop
        while True:
            event, values = data_window.read()
            
            if event == sg.WINDOW_CLOSED or event == 'KEY_data_modifier_exit':
                if tmp_data_dict == self.data_dict:
                    data_window.close()
                    break
                else:
                    response = sg.popup_yes_no("data not updated. continue to exit?", keep_on_top=True)
                    if response == 'Yes' or response is None:
                        data_window.close()
                        break
            
            if event == "KEY_data_modifier_character":
                selected_character = values["KEY_data_modifier_character"][0] if values["KEY_data_modifier_character"] else None
                if selected_character:
                    data_window["KEY_data_modifier_key"].update(values=key)
                    selected_key = None
                    data_window["KEY_data_modifier_value"].update("")
            
            if event == "KEY_data_modifier_key" and selected_character:
                selected_key = values["KEY_data_modifier_key"][0] if values["KEY_data_modifier_key"] else None
                if selected_key:
                    data_window["KEY_data_modifier_value"].update(tmp_data_dict[selected_character][selected_key])
            
            if event == "KEY_data_modifier_value" and selected_character and selected_key:
                tmp_data_dict[selected_character][selected_key] = values["KEY_data_modifier_value"]
                data_window["KEY_data_modifier_value"].update(tmp_data_dict[selected_character][selected_key])
            
            if event == "KEY_data_modifier_update":
            # if event == "KEY_data_modifier_update" and selected_character and selected_key: # two selected items necessary?
                # tmp_data_dict[selected_character][selected_key] = values["KEY_data_modifier_value"]
                # data_window["KEY_data_modifier_value"].update(tmp_data_dict[selected_character][selected_key])

                # test weather all character has value for the new added key
                is_perfect_dict = True
                for character in tmp_data_dict:
                    if '' in tmp_data_dict[character].values():
                        sg.popup('Some character\'s key has empty value, please check', keep_on_top=True)
                        is_perfect_dict = False
                        break
                
                if is_perfect_dict: # then save the current dict into self.data_dict, and use queue sync to data_handler
                    self.data_dict = tmp_data_dict
                    sg.popup("data updated", keep_on_top=True)
                    

            if event == "KEY_add_character":
                new_character = sg.popup_get_text("new character:", keep_on_top=True)
                if new_character and new_character not in tmp_data_dict:
                    tmp_data_dict[new_character] = {attr: "" for attr in key}
                    data_window["KEY_data_modifier_character"].update(values=list(tmp_data_dict.keys()))
            
            if event == "KEY_del_character" and selected_character:
                del tmp_data_dict[selected_character]
                selected_character = None
                data_window["KEY_data_modifier_character"].update(values=list(tmp_data_dict.keys()))
                data_window["KEY_data_modifier_key"].update(values=[])
                data_window["KEY_data_modifier_value"].update("")
            
            if event == "KEY_add_key":
                new_key = sg.popup_get_text("new key:", keep_on_top=True)
                if new_key and new_key not in key:
                    key.append(new_key)
                    for person in tmp_data_dict:
                        tmp_data_dict[person][new_key] = ""
                    data_window["KEY_data_modifier_key"].update(values=key)
            
            if event == "KEY_del_key" and selected_key:
                key.remove(selected_key)
                for person in tmp_data_dict:
                    del tmp_data_dict[person][selected_key]
                selected_key = None
                data_window["KEY_data_modifier_key"].update(values=key)
                data_window["KEY_data_modifier_value"].update("")

    def popup_alias_dict_modifier(self):
        '''pop up a new key_dict modifier window'''

        tmp_key_dict: dict[str, list]
        tmp_key_dict = copy.deepcopy(self.key_dict) # create a copy of key_dict for in-function use
        selected_key = None
        selected_alias = None

        # popup key_dict modifier window layout
        popup_key_window_layout = [
            [sg.Text("keys", font=("Arial", 9), text_color="white", size=(10, 1)),
             sg.Text("alias", font=("Arial", 9), text_color="white", size=(10, 1))],
            [sg.Listbox(values=list(tmp_key_dict.keys()), size=(10, 10), key="KEY_alias_modifier_key", enable_events=True), 
             sg.Listbox(values=tmp_key_dict[list(tmp_key_dict.keys())[0]], size=(10, 10), key="KEY_alias_modifier_alias", enable_events=True)],
            [sg.Button("alias_add", key="KEY_add_alias"),
             sg.Button("alias_del", key="KEY_del_alias")],
            [sg.Button("update", key="KEY_alias_modifier_update"), 
             sg.Button('exit', key='KEY_alias_modifier_exit')]
         ]
        
        key_window = sg.Window('key_dict modifier', popup_key_window_layout, keep_on_top=True, finalize=True)
        key_window.force_focus()

        # run loop
        while True:
            event, values = key_window.read()
            
            if event == sg.WINDOW_CLOSED or event == 'KEY_alias_modifier_exit':
                if tmp_key_dict == self.key_dict:
                    key_window.close()
                    break
                else:
                    response = sg.popup_yes_no("data not updated. continue to exit?", keep_on_top=True)
                    if response == 'Yes' or response is None:
                        key_window.close()
                        break
                    
            
            if event == "KEY_alias_modifier_key":
                selected_key = values["KEY_alias_modifier_key"][0] if values["KEY_alias_modifier_key"] else None
                if selected_key:
                    key_window["KEY_alias_modifier_alias"].update(values=tmp_key_dict[selected_key])
            
            if event == "KEY_alias_modifier_alias":
                selected_alias = values["KEY_alias_modifier_alias"][0] if values["KEY_alias_modifier_alias"] else None
            
            
            if event == "KEY_alias_modifier_update":

                # verify if deplicate in alias
                has_deplica = False
                seen = set()
                for values in tmp_key_dict.values():
                    for value in values:
                        if value in seen:
                            has_deplica = True
                        else:
                            seen.add(value)
                if has_deplica:
                    sg.popup('deplication in alias. please check.', keep_on_top=True)
                else:
                    self.key_dict = tmp_key_dict
                    sg.popup("data updated", keep_on_top=True)
                    key_window["KEY_alias_modifier_alias"].update(tmp_key_dict[selected_key])
                    
            
            if event == "KEY_add_alias" and selected_key:
                new_alias = sg.popup_get_text("new alias:", keep_on_top=True)
                if new_alias and new_alias not in tmp_key_dict[selected_key]:
                    tmp_key_dict[selected_key].append(new_alias)
                    selected_alias = new_alias
                    key_window["KEY_alias_modifier_alias"].update(values=tmp_key_dict[selected_key])
            
            elif event == "KEY_add_alias" and not selected_key:
                sg.popup("please choose a key to add alias", keep_on_top=True)
            
            if event == "KEY_del_alias" and selected_alias:
                tmp_key_dict[selected_key].remove(selected_alias)
                selected_alias = None
                key_window["KEY_alias_modifier_alias"].update(values=tmp_key_dict[selected_key])
            
            elif event == "KEY_del_alias" and not selected_alias:
                sg.popup("please choose an alias to delete", keep_on_top=True)
        


    # comm functions
    def send_message(self, command: str, content: str):
        '''send a message from ui subfunction to broadcast queue'''
        broadcaster.broadcast({'source': 'ui', 'command': command, 'content': content})
    
    def poll_messages(self):
        """ues another way to check news list to avoid high calling"""
        try:
            while not self.queue_ui.empty():
                news = self.queue_ui.get_nowait()
                # self.queue_ui.task_done()
        except queue.Empty:
            pass
        return news



A = UI_Handler(r'C:\Users\86781\VS_Code_Project\form_filler_new\config.json')
A.start_GUI()
A.run_ui()
pass
