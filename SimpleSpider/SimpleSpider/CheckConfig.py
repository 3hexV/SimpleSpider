# coding:utf-8
import json
import time
import re

'''
功能：检查配置的合法性
'''


class CheckConfigC:
    _demo_url = 'https://github.com/'
    # 配置中基本字段
    _config_dec_all_field = [
        {"url_rule": [
            "url_base",
            "url_para_rule",
            "priority",
            "u_func"
        ]},
        {"headers": []},
        {"post_form": []},
        {"field_rule": [
            "field_name",
            "field_handle_rule",
            "field_data_handle",
            "f_func"
        ]},
        {"save_data": [
            "object", "obj_para"
        ]},
        {"ex_attr": [
            "cache_page",
            "auto_add_url"
        ]},
    ]
    # 配置中的规则
    _config_field_check_rule = {
        # url模板构造规则 和函数
        "url_rule":
            {"NUM_ADD": ['4', r'^\d+$', r'^\d+$', r'^\d+$', r'^\d+$'],
             "TEXT_REPLACE": ['1', r'^[:\.\w/]+\.txt$'],
             "TIME_ADD": ['4', r'\d{4}-\d{1,2}-\d{1,2}', r'[Ymd]', r'[\+-]?\d+', r'[%Ymn_\-]+']
             },
        # 字段提取规则 和函数
        "field_handle":
            {"Xpath": ['1', r"^/[/]?.*?$"],
             "AUTO_NUM": ['4', r'^\d+$', r'^\d+$', r'^\d+$', r'^\d+$'],
             "AUTO_NUM_num": ['4', r'^\d+$', r'^\d+$', r'^\d+$', r'^\d+$'],
             "AUTO_TIME": ['4', r'\d{4}-\d{1,2}-\d{1,2}', r'[Ymd]', r'[\+-]{1}\d+', r'[%Ymn_\-]+'],
             "AUTO_TEXT": ['1', r'^[:\.\w/]+\.txt$'],
             },
        # 字段提取后的 数据处理规则 和函数
        "field_data_handle":
            {"TEXT_REPLACE": "",
             "TEXT_SUB": "",
             "TO_STRING": "",
             "TEXT_DEF": "",
             "RE_GET": "",
             "TEXT_TRIM": ""},
        # 数据存储的 方法
        "save_data":
            {"json": r"^[:\.\w/]+\.json$",
             "mongo": "",
             "mysql": "",
             "txt": r"^[:\.\w/]+\.txt$",
             "diy_desc": ""},
        # url规则
        "url_base": [
            r"^http[s]?://.*?$|^\[P0\]$"
        ],
        # # 布尔规则 添加的字段名 将进行布尔验证
        # "bool_rule": [
        #     "ex_attr>cache_page", "ex_attr>auto_add_url"
        # ]
    }
    # 配置是否 出现异常
    _bool_config_abnormal = False
    # 返回的 数据结构
    # [true,     true,       true,       ["*title":["not null", "title"]], [],          [],          {"json": ["./tt.json"]}, [], [] ]
    # 模板构造URL Hearder为空 Post表单为空 字段模板描述表                     字段提取表    字段数据处理表 数据存储方式              扩展功能表 URL模板函数和参数
    _res_config_list = [False, True, True, [], [], [], {}, [], []]

    def __init__(self, config={}):
        try:
            if self.AutoCheck(config=config) == 0:
                self.TipsFormat(0, '配置加载异常')
            else:
                self.TipsFormat(0, '配置加载完成')
        except Exception as e:
            self.TipsFormat(2, "在配置中的某个地方缺少{}字段".format(e))


    def AutoCheck(self, config=''):
        # 对配置进行分离 分离为 1.url规则 2.有无headers 3.有无post表单 4. 字段规则  5.savadata规则  6. ex（扩展）规则
        # print(config)

        # 1.判断基本描述字段个数
        # print(len(config), len(self._config_dec_all_field))
        if len(self._config_dec_all_field) != len(config):
            self.TipsFormat(2, '检查配置字段合法性出现异常。<描述字段的数目缺少或增加，可能是你的json格式或语法有误导致的。>')
            self._bool_config_abnormal = True
        if self._bool_config_abnormal:
            return 0
        # print('所有数目正确')

        # 2.基本描述字段
        config_base_tmp = self.GetAllKeyName(self._config_dec_all_field)
        for tmp_c in config:
            if tmp_c not in config_base_tmp:
                self.TipsFormat(2, '检查配置字段合法性出现异常。<描述字段{}无法识别，请检查拼写。>'.format(tmp_c))
                self._bool_config_abnormal = True
        if self._bool_config_abnormal:
            return 0
        # print('基本字段名正确')

        # 3.检查每个描述字段的 名是否有误 以及每个规则
        # 3.1 检查每个描述字段名
        config_dec_all_field_list_tmp = []
        for i in self._config_dec_all_field:
            s_key = ''.join(i.keys())
            config_dec_all_field_list_tmp.append(s_key)
            config_dec_all_field_list_tmp += i[s_key]
        headers_post_field_tmp = self.GetAllKeyName(config['headers']) + self.GetAllKeyName(config['post_form'])
        for tmp in self.GetAllKeyName(config):
            if tmp not in config_dec_all_field_list_tmp:
                if tmp not in headers_post_field_tmp:
                    self.TipsFormat(2, '检查配置字段合法性出现异常。<描述字段{}无法识别或者缺少某些必要字段，请检查拼写。>'.format(tmp))
                    self._bool_config_abnormal = True
        if self._bool_config_abnormal:
            return 0
        # print('所有字段名正确')

        # 判断headers 和 post是否为空
        self._res_config_list[1] = False if len((self.GetAllKeyName(config['headers']))) > 0 else True
        self._res_config_list[2] = False if len((self.GetAllKeyName(config['post_form']))) > 0 else True

        # 3.2 检查每个描述字段规则 参数
        # url是否匹配
        if re.search(self._config_field_check_rule['url_base'][0], config['url_rule']['url_base']) is None:
            self._bool_config_abnormal = True
            self.TipsFormat(2, '检查配置字段合法性出现异常。<描述字段url_base不符合规则。>')
        else:
            # 判断是否使用模板配置
            if len(re.findall(r'\[P\d+\]', config['url_rule']['url_base'])) > 0:
                self._res_config_list[0] = True
        if self._bool_config_abnormal:
            return 0
        # print('URL符合规范')

        # 3.3提取url模板规则
        url_para_rule_list = config['url_rule']['url_para_rule'].copy()
        if ''.join(url_para_rule_list.pop(0).keys()) != 'priority':
            self._bool_config_abnormal = True
            self.TipsFormat(2, '检查配置字段合法性出现异常。<描述字段priority应放在url_para_rule中第一个。>')
        if self._bool_config_abnormal:
            return 0
        # print('priority位置正确')

        # 3.4检查url模板字段 函数 的参数合法性
        u_r_tmp = self.GetAllKeyName(self._config_field_check_rule['url_rule'])
        url_para_rule_list_tmp = url_para_rule_list
        for i in range(0, len(url_para_rule_list)):
            # 方法名
            u_func = url_para_rule_list_tmp[i]['u_func'][0]
            # 方法参数
            u_func_para = url_para_rule_list_tmp[i]['u_func'].copy()
            u_func_para.pop(0)

            if u_func in u_r_tmp:
                # 首先验证参数数目
                num = int(self._config_field_check_rule['url_rule'][u_func][0])
                para = self._config_field_check_rule['url_rule'][u_func].copy()
                para.pop(0)
                if num != len(u_func_para):
                    self._bool_config_abnormal = True
                    self.TipsFormat(2, '检查配置字段合法性出现异常。<描述字段url_para_rule中第{}个URL参数u_func为{}，但是其参数数目不合法。>'
                                    .format(str(i + 1), u_func))

                else:
                    for t in range(0, len(u_func_para)):
                        if re.match(re.compile(para[t]), u_func_para[t]) is None:
                            self._bool_config_abnormal = True
                            self.TipsFormat(2,
                                            '检查配置字段合法性出现异常。<描述字段url_para_rule中第{}个URL参数u_func为{}，但是其第{}参数为{}，这个参数是不合法。>'
                                            .format(str(i + 1), u_func, str(t + 1), u_func_para[t]))
            else:
                self._bool_config_abnormal = True
                self.TipsFormat(2, '检查配置字段合法性出现异常。<描述字段url_para_rule中第{}个URL参数规则u_func为{}，是无效。>'
                                .format(str(i + 1), u_func))
        if self._bool_config_abnormal:
            return 0
        # print('URL模板参数检查完成')

        # 3.5检查字段名有无重复
        field_name = []
        for i in config['field_rule']:
            field_name.append(i['field_name'])
            if i['field_name'] == '' or i['field_name'].replace('*', '') == '':
                self._bool_config_abnormal = True
                self.TipsFormat(2, '检查配置字段合法性出现异常。<描述字段field_rule中有field_name为空。>')
        re_field_name = list(set(field_name))
        if len(re_field_name) != len(field_name):
            self._bool_config_abnormal = True
            self.TipsFormat(2, '检查配置字段合法性出现异常。<描述字段field_rule中field_name有重复。>')
        if self._bool_config_abnormal:
            return 0
        # print('字段名检查完成')

        # 添加字段描述表
        for frn in re_field_name:
            # 非空字段
            if frn[0:1] == '*':
                self._res_config_list[3].append({frn: ['not null', frn[1:]]})
            else:
                self._res_config_list[3].append({frn: ['none', frn]})

        # 3.6检查提取数据  字段的合法性
        field_handle_rule_list = config['field_rule']
        f_r_tmp = self.GetAllKeyName(self._config_field_check_rule['field_handle'])
        for i in range(0, len(field_handle_rule_list)):
            f_func = field_handle_rule_list[i]['field_handle_rule'][0]
            f_func_para = field_handle_rule_list[i]['field_handle_rule'].copy()
            f_func_para.pop(0)
            # print(f_func)
            # print(f_func_para)
            # print(f_r_tmp)
            # 函数名存在
            if f_func in f_r_tmp:
                # 首先验证参数数目
                num = int(self._config_field_check_rule['field_handle'][f_func][0])
                para = self._config_field_check_rule['field_handle'][f_func].copy()
                para.pop(0)
                # print(num)
                # print(para)
                if num != len(f_func_para):
                    self._bool_config_abnormal = True
                    self.TipsFormat(2, '检查配置字段合法性出现异常。<描述字段field_rule中第{}个字段，提取参数field_handle_rule为{}，但是其参数数目不合法。>'
                                    .format(str(i + 1), f_func, f_func_para))
                    return 0
                else:
                    for t in range(0, len(f_func_para)):
                        # print(para[t])
                        # print(f_func_para[t])
                        # print(re.search(para[t], f_func_para[t]))
                        if re.search(para[t], f_func_para[t]) is None:
                            self._bool_config_abnormal = True
                            self.TipsFormat(2,
                                            '检查配置字段合法性出现异常。<描述字段field_rule中第{}个字段，提取参数field_handle_rule为{},但是其第{}参数为{}，这个参数是不合法。>'
                                            .format(str(i + 1), f_func, str(t + 1), f_func_para[t]))
                            return 0
            # 函数名不存在
            else:
                self._bool_config_abnormal = True
                self.TipsFormat(2, '检查配置字段合法性出现异常。<描述字段field_rule中第{}个字段，提取参数field_handle_rule为{}，是不合法。>'
                                .format(str(i + 1), f_func))
                return 0
        if self._bool_config_abnormal:
            return 0
        # print('字段提取参数检查完成')

        # 添加字段的提取规则
        for t in range(0, len(field_handle_rule_list)):
            for rcl in self._res_config_list[3]:
                if ''.join(rcl.keys()) == field_handle_rule_list[t]['field_name']:
                    self._res_config_list[4].append(
                        {list(rcl.values())[0][1]:
                             field_handle_rule_list[t]['field_handle_rule']}
                    )

        # 3.7检查数据处理 字段 参数合法性
        field_handle_data_rule_list = []
        for i in config['field_rule']:
            field_handle_data_rule_list.append(i['field_data_handle'])
        f_r_d_tmp = self.GetAllKeyName(self._config_field_check_rule['field_data_handle'])
        for i in range(0, len(field_handle_data_rule_list)):
            for j in range(0, len(field_handle_data_rule_list[i])):
                f_func_data = field_handle_data_rule_list[i][j]['f_func'][0]
                # f_func_data_para = field_handle_data_rule_list[i][j]['f_func'].pop(0)
                if f_func_data not in f_r_d_tmp:
                    self._bool_config_abnormal = True
                    self.TipsFormat(2,
                                    '检查配置字段合法性出现异常。<描述字段field_rule中第{}个字段的数据处理参数field_data_handle的第{}个数据处理方式为{}，但是这个是不合法。>'
                                    .format(str(i + 1), str(j + 1), f_func_data))
        # print(field_handle_data_rule_list)
        # print(f_r_d_tmp)
        if self._bool_config_abnormal:
            return 0

        # 添加字段 数据处理 描述表
        for t in range(0, len(field_handle_rule_list)):
            for rcl in self._res_config_list[3]:
                if ''.join(rcl.keys()) == field_handle_rule_list[t]['field_name']:
                    self._res_config_list[5].append(
                        {list(rcl.values())[0][1]:
                             field_handle_rule_list[t]['field_data_handle']}
                    )

        # 3.8检查保存数据的 参数
        save_data_rule_list = config['save_data']
        s_d_tmp = self.GetAllKeyName(self._config_field_check_rule['save_data'])
        s_d_object = save_data_rule_list['object']
        if s_d_object in s_d_tmp:
            s_d_object_para = ''.join(save_data_rule_list['obj_para'])
            if re.search(re.compile(self._config_field_check_rule['save_data'][s_d_object]), s_d_object_para) is None:
                self._bool_config_abnormal = True
                self.TipsFormat(2, '检查配置字段合法性出现异常。<描述字段save_data中{}的参数{}是不合法>'
                                .format(s_d_object, s_d_object_para))
        else:
            self._bool_config_abnormal = True
            self.TipsFormat(2, '检查配置字段合法性出现异常。<描述字段save_data中{}是不合法。>'
                            .format(s_d_object))
        if self._bool_config_abnormal:
            return 0

        # 添加数据保存方式 描述
        self._res_config_list[6] = {save_data_rule_list['object']: save_data_rule_list['obj_para']}

        # # 3.9布尔检查
        # b_r_tmp = self._config_field_check_rule['bool_rule']
        # for i in range(0, len(b_r_tmp)):
        #     bool_check_path = b_r_tmp[i].split('>')
        #     data = config[bool_check_path[0]]
        #     for j in range(1, len(bool_check_path)):
        #         data = data[bool_check_path[j]]
        #     if not isinstance(data, bool):
        #         self._bool_config_abnormal = True
        #         self.TipsFormat(2, '检查配置字段合法性出现异常。<描述字段save_data中{}值为布尔值。>'
        #                         .format(bool_check_path))
        # if self._bool_config_abnormal:
        #     return 0

        # 添加扩展 功能描述
        self._res_config_list[7] = {'ex_attr': config['ex_attr']}

        # 添加URL模板参数
        if self._res_config_list[0]:
            tmp = config['url_rule']['url_para_rule'].copy()
            tmp.pop(0)
            self._res_config_list[8] = {"url_para_rule": tmp}

        # for s in self._res_config_list:
        #     print(s)
        return 1

    def GetResConfig(self):
        if self._bool_config_abnormal:
            self.TipsFormat(2, '加载过程中出现异常,禁止获取返回的描述表')
            return []
        else:
            return self._res_config_list

    @staticmethod
    def _str_GetDictKey(keys):
        return ''.join(list(keys))

    @staticmethod
    def TipsFormat(grade=0, info='none'):
        """打印有 格式的提示
        :param grade:信息的等级 从告到地 error warn info
        :param info:信息的载荷
        """
        grade = 'error' if grade == 1 else 'warn' if grade == 2 else 'info'
        print('<{}> [{}]---{}'.format(str(time.strftime('%H:%M:%S', time.localtime(time.time()))), grade, info))

    def GetAllKeyName(self, data):
        key_name_list = []
        if isinstance(data, dict):
            tmp = list(data.keys())
            if len(tmp) > 1:
                key_name_list += tmp
                for t in tmp:
                    key_name_list += self.GetAllKeyName(data[t])
            elif len(tmp) == 1:
                tmp = ''.join(tmp)
                key_name_list.append(''.join(tmp))
                key_name_list += self.GetAllKeyName(data[tmp])
            else:
                pass
        elif isinstance(data, list):
            for da in data:
                key_name_list += self.GetAllKeyName(da)
        return list(set(key_name_list))


def main():
    # try:
    with open('../new_config.json', 'r', encoding='utf-8-sig') as f:
        CheckConfigC(json.load(fp=f)).GetResConfig()
    # except Exception as e:
    #     print(e)


if __name__ == '__main__':
    main()
