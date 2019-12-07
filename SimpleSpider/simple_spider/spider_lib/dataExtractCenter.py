# coding:utf-8
import re
import configparser
import os
from lxml import etree
import json
from simple_spider.sys_func.filePathCalc import FilePathCalc
import logging


'''
数据提取中心
通过传入的提取对象 和提取规则 提取数据
'''


class DataExtractCenter:

    def __init__(self):
        self.fpc = FilePathCalc(sysPath='../sys_func/syspath.ini')
        logging.basicConfig(level=logging.DEBUG,
                            filename=self.fpc.returnFilePath('syslog', 'log.log'),
                            filemode='a',
                            format=
                            '%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S %p'
                            )
        try:
            self._initConfig()
            self.abnormalFlag = False
        except Exception as e:
            self.abnormalFlag = True
            logging.error('发生异常：{}'.format(e))

    def _initConfig(self):
        cp = configparser.ConfigParser()

        cp.read(self.fpc.returnFilePath('sysspiderlib', 'spiderBaseConfig.ini'), encoding='utf-8-sig')

        self._reDefLinkSymbol = cp.get('Data Extract', 'ReDefLinkSymbol')

        self._extractFuncName = self._iniStrToList(cp.get('Data Extract', 'ExtractFuncName'))
        self._extractFuncName += [tmp.capitalize() for tmp in self._extractFuncName]
        # self._extractFuncName += [tmp.upper() for tmp in self._extractFuncName]
        # self._extractFuncName += [tmp.lower() for tmp in self._extractFuncName]
        self._extractFuncName = list(set(self._extractFuncName))

        # print(self._extractFuncName, type(self._extractFuncName))
        # print(self._reDefLinkSymbol)

    # rule [规则名，规则]
    def extract(self, obj, rule):
        # 初始化是否异常
        if self.abnormalFlag:
            return []

        # 参数是否异常
        if not isinstance(obj, str) or (not isinstance(rule, list) or len(rule) == 0):
            print('[!]参数异常')
            logging.error("参数异常")
            return []

        # 是否支持该函数
        rule_name = rule[0]
        if rule_name not in self._extractFuncName:
            print('[!]未知函数')
            logging.error("未知函数")
            return []

        rule_list = rule.copy()
        rule_list.pop(0)
        # print(rule_list)

        res = self._ctrl(obj, rule_name, rule_list)
        return res

    def _ctrl(self, obj, funcName, funcList):
        if funcName in ['xpath','Xpath']:
            return self._funXpath(obj, funcList)
        elif funcName in ['re','Re']:
            return self._funRe(obj, funcList)
        elif funcName in ['json','Json']:
            return self._funJson(obj, funcList)
        elif funcName in ['css_select','Css_select']:
            return []
        elif funcName in ['bs4','Bs4']:
            return []

    @staticmethod
    def _funXpath(obj, rule):
        if len(rule) != 1:
            logging.error('{}参数错误'.format("xpath"))
            return []
        # print(rule[0], obj)
        try:
            res = etree.HTML(obj).xpath(rule[0])
        except:
            res = None
            logging.error('Xpath解析中出现错误')
        return [] if res is None else res

    # ['re',"j(.*?)ck(.*?)>", '[P1]-[P2]=[P1]']
    def _funRe(self, obj, rule):
        if len(rule) != 2:
            logging.error('{}参数错误'.format("re"))
            return []
        try:
            res = re.findall(re.compile(rule[0]), obj)
            para_list = re.findall(re.compile(r'\[P\d+\]'), rule[1])
            res_tmp = []
            if len(rule[1]) != 0 and para_list != []:
                for tmp in res:
                    rs = [i for i in re.split(r'\[P\d+\]', rule[1])]
                    rs.pop(0)
                    t = ''
                    if isinstance(tmp, tuple):
                        length = len(tmp)
                        for pl in para_list:
                            index = int(''.join(re.findall(r'\d+', pl)))
                            index = index - 1 if index - 1 < length else -1
                            # print(index, length)
                            if index == -1:
                                t += '' + (rs[index] if index < len(rs) else '')
                            else:
                                t += tmp[index] + (rs[index] if index < len(rs) else '')
                    else:
                        t = tmp
                    res_tmp.append(t)
            else:
                for tmp in res:
                    rs = [i for i in re.split(r'\[P\d+\]', rule[1])]
                    rs.pop(0)
                    t = ''
                    if isinstance(tmp, tuple):
                        t = '{}'.format(self._reDefLinkSymbol).join(tmp)\
                            .replace('\sp', ' ').replace('\\n', '\n').replace('\\t', '\t').replace('\\N', '')
                    else:
                        t = tmp
                    res_tmp.append(t)
            res = res_tmp
        except:
            res = None
            logging.error('re(正则)解析中出现错误')
        return [] if res is None else res

    # ['json','how', 2]
    @staticmethod
    def _funJson(obj, rule):
        if len(rule) == 0:
            logging.error('{}参数错误'.format("Json"))
            return []
        for r in rule:
            if not isinstance(r, str) and not isinstance(r, int):
                logging.error('{}参数错误'.format("Json"))
                return []
        # print(rule[0], obj)
        try:
            if isinstance(obj, str):
                obj_json = json.loads(obj)
            elif isinstance(obj, dict):
                obj_json = obj
            else:
                return []

            r = obj_json[rule[0]]
            for i in range(1, len(rule)):
                r = r[rule[i]]
            if isinstance(r, list):
                res = r
            else:
                res = [r]
        except:
            res = None
            logging.error('Json解析中出现错误')
        return [] if res is None else res

    @staticmethod
    def _iniStrToList(strS):
        if len(strS) != 0:
            return strS.replace('[', '').replace(']', '').replace(' ', '').split(',')
        else:
            return []


# def main():
#     dec = DataExtractCenter()
#     # with open('./config.json', 'r', encoding='utf-8') as f:
#     #     res = f.read()
#     r = dec.extract('{"name":"jackt", "how":["lucy", "tom"]}', ['re',"j(.*?)c(.*?)\"", '[P1]_[P2]'])
#     print(r)
#     # dec.extract(res, ['json','url','url_rule', 1, 2])
#
#
# if __name__ == '__main__':
#     main()