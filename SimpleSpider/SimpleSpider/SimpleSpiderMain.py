# coding:utf-8
import requests
import os
import time
import json
import re
from lxml import etree
# from .DataHandle import DataHandleC
# from .SaveData import SaveDataC
# from .CheckConfig import CheckConfigC
# from .DataHub import DataHubC
from SimpleSpider.DataHandle import DataHandleC
from SimpleSpider.SaveData import SaveDataC
from SimpleSpider.CheckConfig import CheckConfigC
from SimpleSpider.DataHub import DataHubC

"""
功能：参数的加载和检查，爬虫的任务调度，爬虫的目标字段爬取
"""


class SimpleSpider:
    # 默认config.json的位置
    _str_def_config_json_path = './config.json'
    # 配置异常标志位
    _bool_config_abnormal_flag = False

    # 总字段数目
    _int_field_count = 0
    # 配置描述表
    _res_config_desc_list = []
    # 完整的配置描述
    _raw_config_desc_list = []
    # 自动填充对应的URL
    _bool_auto_add_url = False
    # 是否缓存网页
    _bool_cache_page = False
    # Headers
    _dict_headers_e = {}
    # Post表单
    _dict_post_e = {}
    # 数据池
    _dh = DataHubC()
    # URL列表
    _list_more_url = []

    def __init__(self, str_config_json_path=''):
        try:
            # 判断用户是否自定义配置文件的位置 如果没有自定义配置文件
            if len(str_config_json_path) == 0:
                dict_raw_config = self.ReadConfig(str_config_json_path=self._str_def_config_json_path)
            else:
                if os.path.isfile(str_config_json_path):
                    dict_raw_config = self.ReadConfig(str_config_json_path=str_config_json_path)
                else:
                    self.TipsFormat(2, '{} 文件不存在，请核查'.format(str_config_json_path))

            # 判断读取过程中是否有异常
            if not self._bool_config_abnormal_flag:
                if self.LoadConfig(dict_raw_config=dict_raw_config):
                    self.TipsFormat(0, '所有配置加载完成，等待启动爬虫')
                else:
                    self.TipsFormat(2, '爬虫已经停止')
                    self._bool_config_abnormal_flag = True
            else:
                self.TipsFormat(2, '爬虫已经停止')
                self._bool_config_abnormal_flag = True
        except Exception as e:
            self.TipsFormat(2, '捕获异常 {}'.format(e))

    def ReadConfig(self, str_config_json_path):
        r"""读取json的配置，检查配置的完整性

        :param str_config_json_path config.josn的位置
        :return dict_config 配置字典
        """
        dict_config = {}
        self.TipsFormat(0, '开始读取配置：使用如下配置文件 {}'.format(str_config_json_path))
        # 开始读取配置
        try:
            with open(str_config_json_path, 'r', encoding='utf-8') as f:
                dict_config = json.load(fp=f)
            # 开始检查配置 文件为空 基本配置（url,rule,savedata）为空
            if len(dict_config) == 0:
                self._bool_config_abnormal_flag = True
                self.TipsFormat(2, '配置文件为空。')
            self.TipsFormat(0, '配置读取完成，等待加载配置。')

            # print(dict_config)
        except Exception as e:
            self.TipsFormat(2, '配置读取发生异常！[捕获异常：{}]'.format(e))
            # 配置读取发生异常 取消爬虫任务
            self._bool_config_abnormal_flag = True
        finally:
            return dict_config

    def LoadConfig(self, dict_raw_config={}):
        r"""根据读取的 无误的配置 将配置加载到爬虫上

        :param dict_raw_config 爬虫配置
        :return bool_is_ready 是否可以启动爬虫
        """
        self.TipsFormat(0, '开始加载配置到爬虫上')
        # 完整描述
        self._raw_config_desc_list = dict_raw_config
        # 概要描述
        self._res_config_desc_list = CheckConfigC(config=dict_raw_config).GetResConfig()
        # print(self._res_config_desc_list)

        # 请求头 和 post表单填充
        self._dict_headers_e = {} if self._res_config_desc_list[1] else self._raw_config_desc_list['headers']
        self._dict_post_e = {} if self._res_config_desc_list[2] else self._raw_config_desc_list['post_form']

        # 是否缓存 页面  和 自动添加url
        self._bool_cache_page = self._res_config_desc_list[7]['ex_attr']['cache_page']
        self._bool_auto_add_url = self._res_config_desc_list[7]['ex_attr']['auto_add_url']

        # 总字段数量
        self._int_field_count = len(self._res_config_desc_list[3])

        # 数据保存方式
        self._dict_save_data = self._res_config_desc_list[6]

        # 创建URL列表
        if self._res_config_desc_list[0]:
            self.TipsFormat(0, '开始构造URL列表')
            self._list_more_url = DataHandleC().CreateURL(url_rule=self._res_config_desc_list[8]['url_para_rule'].copy(),
                                                          url=self._raw_config_desc_list['url_rule']['url_base'])
            # print(self._list_more_url)
            if len(self._list_more_url) == 0:
                self.TipsFormat(2, 'URL构造中出现异常')
                return False
            self.TipsFormat(0, 'URL构造完成')
        else:
            self._list_more_url.append(self._raw_config_desc_list['url_rule']['url_base'])

        if len(self._res_config_desc_list) == 0:
            return False
        else:
            return True

    def SpiderWork(self):
        try:
            list_field_data = []
            # 如果爬虫没有异常
            if not self._bool_config_abnormal_flag:
                # 单页面模式
                if not self._res_config_desc_list[0]:
                    # 获取字段和字段数据
                    self.TipsFormat(0, '单个网页请求，启动中...')
                    # print(self._raw_config_desc_list['url_rule']['url_base'])
                    dict_field_data = self.SpiderWork_AnalysisPage(
                        url=self._raw_config_desc_list['url_rule']['url_base'])

                    # return None
                    if dict_field_data is not None or len(dict_field_data) == self._int_field_count:
                        # 数据汇总
                        list_field_data.append(dict_field_data.copy())
                        # 清空临   时数据
                    dict_field_data.clear()

                # 多模板页面模式
                elif self._res_config_desc_list[0]:
                    self.TipsFormat(0, '多个网页请求，启动中...')
                    for i in self._list_more_url:
                        dict_field_data = self.SpiderWork_AnalysisPage(url=i)
                        # print(i, dict_field_data)
                        if dict_field_data is not None or len(dict_field_data) == self._int_field_count:
                            # 数据汇总
                            list_field_data.append(dict_field_data.copy())
                            # 清空临   时数据
                        dict_field_data.clear()
                        time.sleep(1)

                if len(self._dh.ShowDHValues()) != 0:
                    self._dh.ClearDHAll()
                    # print('释放数据池完成')
                    # self._dh.ShowDHValues()
                else:
                    pass
                    # print('未启用数据池')

                # 开始保存数据
                save_data_count_tmp = SaveDataC(func=''.join(self._dict_save_data.keys()),
                                                para=''.join(
                                                    self._dict_save_data[''.join(self._dict_save_data.keys())]),
                                                data=list_field_data,
                                                field_len=self._int_field_count + 1 if self._bool_auto_add_url else self._int_field_count).GetSaveDataCount()
                self.TipsFormat(0,
                                '共{}个目标URL，共成功写入{}个记录'.format(str(len(self._list_more_url)),
                                str(save_data_count_tmp)))
            else:
                return 0
            return 1
        except Exception as e:
            self.TipsFormat(2, '捕获异常 {}'.format(e))
            return 0

    def SpiderWork_GetHtmlPage(self, url):

        str_html_page = 'none'
        if len(list(self._dict_post_e.keys())) != 0:
            # Post请求
            self.TipsFormat(0, '请求网页 {}： {}'.format('Post', url))
            respond = requests.post(url=url, headers=self._dict_headers_e, data=self._dict_post_e)
        else:
            # GET请求
            self.TipsFormat(0, '请求网页 {}： {}'.format('Get', url))
            respond = requests.get(url=url, headers=self._dict_headers_e)

        self.TipsFormat(0, '请求响应码: {}'.format(str(respond.status_code)))
        if respond.status_code in [404, 503]:
            return str_html_page

        encode = respond.apparent_encoding
        str_html_page = respond.content.decode(encode, 'ignore')

        if self._bool_cache_page:
            url_tmp = url.replace('http://', '').replace('https://', '').replace('\\', '_').replace('/', '_')\
                .replace('?', '_').replace('\"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
            path = "./tmp/" + url_tmp + '.html'
            with open(path, 'w', encoding=encode) as f:
                f.write(str_html_page)
                print('\t\t\t{} 缓存完成'.format(path))
        return str_html_page

    def SpiderWork_AnalysisPage(self, url):
        # 每条记录 包含所有字段名 和字段的值
        dict_field_data = {}

        # 拿到可以解析的html
        str_html = self.SpiderWork_GetHtmlPage(url=url)
        if str_html == 'none' and len(str_html) == 4:
            return dict_field_data
        lxml_html = etree.HTML(str_html)

        # 是否自动填充对应的url
        if self._bool_auto_add_url:
            dict_field_data['url'] = url

        # 描述每个目标字段
        aim_field_desc_list = self._res_config_desc_list[3]
        # 描述每个目标字段的数据提取方式
        aim_field_get_data_list = self._res_config_desc_list[4]
        # 描述每个字段的数据处理方式
        aim_field_data_handle_list = self._res_config_desc_list[5]

        # print(aim_field_desc_list)
        # print(aim_field_get_data_list)
        # print(aim_field_data_handle_list)

        for afgdl in aim_field_get_data_list:
            aim_field_name = ''.join(afgdl.keys())
            tmp = afgdl[aim_field_name].copy()
            # 使用Xpath解析
            if tmp[0] == 'Xpath':
                dict_field_data[aim_field_name] = lxml_html.xpath(afgdl[aim_field_name][1])
            # 使用函数
            else:
                func = tmp[0]
                tmp.pop(0)
                dict_field_data[aim_field_name] = self.FuncInDH(field_name=aim_field_name, func=func, data=tmp)
                # 检查是否溢出 或者 出现其他问题
                if dict_field_data[aim_field_name] is None:
                    print("\t\t\t\t\t{}出现异常".format(aim_field_name))
                    dict_field_data.clear()
                    return dict_field_data

            # 判断是否是关键不可为空字段 为空值
            if self.CheckIsPrimaryField(aim_field_desc_list, aim_field_name) and len(
                    dict_field_data[aim_field_name]) == 0 or dict_field_data[aim_field_name] is None:
                print("\t\t\t{}含有空字段<{}>".format(url, aim_field_name))
                dict_field_data.clear()
                return dict_field_data

            # 数据处理
            for afdhl in aim_field_data_handle_list:
                if aim_field_name == ''.join(afdhl.keys()):
                    # print('字段名：', aim_field_name)
                    # print('数据处理方式：', afdhl[''.join(afdhl.keys())])
                    dict_field_data[aim_field_name] = self.FuncDataHandle(
                        handle=afdhl[''.join(afdhl.keys())],
                        data=dict_field_data[aim_field_name])
        if len(dict_field_data) == self._int_field_count:
            print("\t\t\t\t\t解析成功，新增记录")
        # print(dict_field_data)
        return dict_field_data

    def FuncInDH(self, field_name, func, data=[]):
        if self._dh.FlagIsReg(flag=field_name):
            # print("使用过数据池")
            if func == 'AUTO_NUM':
                res = self.FuncInDH_NumAdd(self._dh.GetDataFromDH(flag=field_name))
                return None if res is None else res
            elif func == 'AUTO_NUM_num':
                res = self.FuncInDH_NumAdd(self._dh.GetDataFromDH(flag=field_name))
                return None if res is None else int(res)
        else:
            # print("没有使用过数据池")
            if func == 'AUTO_NUM':
                data.append(str(int(data[0]) - int(data[2])))
                self._dh.RegisterUseDH(flag=field_name, data=data)
                res = self.FuncInDH_NumAdd(self._dh.GetDataFromDH(flag=field_name))
                return None if res is None else res
            elif func == 'AUTO_NUM_num':
                data.append(str(int(data[0]) - int(data[2])))
                self._dh.RegisterUseDH(flag=field_name, data=data)
                res = self.FuncInDH_NumAdd(self._dh.GetDataFromDH(flag=field_name))
                return None if res is None else int(res)
        return None

    def FuncInDH_NumAdd(self, data):
        now = int(data[4]) + int(data[2]) if int(data[4]) < int(data[1]) else None
        # print('now', now)
        data[4] = str(now)
        # print('data', data)
        if now is None:
            self.TipsFormat(2, '达到最大值')
            return None
        p = int(data[3]) - len(data[4]) if len(data[4]) < int(data[3]) else 0
        # print('{}'.format('0'*p + data[4]))
        return '{}'.format('0' * p + data[4])

    def FuncDataHandle(self, handle, data):
        # print(len(handle))
        for i in range(0, len(handle)):
            # print(i)
            func = handle[i][''.join(handle[i].keys())][0]
            para = handle[i][''.join(handle[i].keys())].copy()
            para.pop(0)
            # print('User Func', func, para)
            if func == 'TEXT_REPLACE':
                data = self.FuncDataHandle_TEXT_Replace(data, para)
            elif func == 'TO_STRING':
                data = self.FuncDataHandle_TO_STRING(data)
            elif func == 'TEXT_SUB':
                data = self.FuncDataHandle_TEXT_SUB(data, para)
            elif func == 'RE_GET':
                data = self.FuncDataHandle_RE_GET(data, para)
            elif func == 'TEXT_TRIM':
                data = self.FuncDataHandle_TEXT_TRIM(data)
            elif func == 'TEXT_DEF':
                # 转为Str 并去除两边空格
                data = self.FuncDataHandle_TEXT_TRIM(self.FuncDataHandle_TO_STRING(data))
                # 保留换行分段
                data = self.FuncDataHandle_TEXT_Replace(data, ['\r\n\t', '\n'])
        return data

    @staticmethod
    def FuncDataHandle_TEXT_Replace(data, para=[]):
        res = []
        if isinstance(data, list):
            for d in data:
                res.append(d.replace(para[0], para[1]))
            return res
        elif isinstance(data, str):
            return data.replace(para[0], para[1])

    @staticmethod
    def FuncDataHandle_TO_STRING(data):
        if isinstance(data, list):
            res = ''.join(data)
            return res
        elif isinstance(data, str):
            return data

    def FuncDataHandle_TEXT_SUB(self, data, para=[]):
        try:
            if isinstance(data, list):
                data = self.FuncDataHandle_TO_STRING(data=data)
                begin = data.index(para[0]) if para[0] != '' else 0
                end = data.index(para[1])+len(para[1]) if para[1] != '' else len(data)
                res = data[begin:end]
                return res
            elif isinstance(data, str):
                begin = data.index(para[0]) if para[0] != '' else 0
                end = data.index(para[1])+len(para[1]) if para[1] != '' else len(data)
                res = data[begin:end]
                return res
        except Exception as e:
            print(e)
        finally:
            return data

    def FuncDataHandle_RE_GET(self, data, para=[]):
        if isinstance(data, list):
            data = self.FuncDataHandle_TO_STRING(data=data)
            return re.findall(re.compile(para[0]), data)
        elif isinstance(data, str):
            return re.findall(re.compile(para[0]), data)

    def FuncDataHandle_TEXT_TRIM(self, data):
        if isinstance(data, list):
            data = self.FuncDataHandle_TO_STRING(data=data)
            return data.strip()
        elif isinstance(data, str):
            return data.strip()

    @staticmethod
    def CheckIsPrimaryField(desc_list=[], field_name=''):
        field_name = "*" + field_name
        for tmp in desc_list:
            if field_name == ''.join(tmp.keys()):
                return True
        return False

    @staticmethod
    def TipsFormat(grade=0, info='none'):
        """打印有 格式的提示
        :param grade:信息的等级 从告到地 error warn info
        :param info:信息的载荷
        """
        grade = 'error' if grade == 1 else 'warn' if grade == 2 else 'info'
        print('<{}> [{}]---{}'.format(str(time.strftime('%H:%M:%S', time.localtime(time.time()))), grade, info))


def main():
    ss = SimpleSpider('../new_config.json')
    ss.SpiderWork()


if __name__ == '__main__':
    main()
