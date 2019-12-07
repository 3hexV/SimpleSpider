# coding:utf-8
import os
import configparser
from simple_spider.spider_lib.dataExtractCenter import DataExtractCenter
from simple_spider.sys_func.filePathCalc import FilePathCalc
import logging


class DataHandleCenter:

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
            logging.error('发生异常：{}'.format(e))
            self.abnormalFlag = True

    def _initConfig(self):
        cp = configparser.ConfigParser()
        cp.read(self.fpc.returnFilePath('sysspiderlib', 'spiderBaseConfig.ini'), encoding='utf-8-sig')

        self._dataListToStr = True if cp.get('Data Handle', 'DataListToStr') == 'true' else False
        # self._textSubIncludeSelf = True if cp.get('Data Handle', 'TextSubIncludeSelf') == 'true' else False

        self._dataHandleFuncName = self._iniStrToList(cp.get('Data Handle', 'DataHandleFuncName'))
        self._dataHandleFuncName += [tmp.capitalize() for tmp in self._dataHandleFuncName]
        self._dataHandleFuncName = list(set(self._dataHandleFuncName))

        # print(self._dataHandleFuncName)

    # rule [规则名，规则]
    def handle(self, obj, rule):
        # 初始化是否异常
        if self.abnormalFlag:
            return []

        # 参数是否异常
        if len(obj) == 0 or len(rule) == 0:
            print('[!]参数异常或者待处理数据为空')
            logging.error('参数异常或者待处理数据为空')
            return []

        # 是否支持该函数
        rule_name = rule[0]
        if rule_name not in self._dataHandleFuncName:
            print('[!]未知函数')
            logging.error('未知函数')
            return []

        rule_list = rule.copy()
        rule_list.pop(0)
        # print(rule_list)

        res = self._ctrl(obj, rule_name, rule_list)
        if isinstance(res, list):
            res_tmp = [r for r in res if r != []]
            res = list(set(res))
        return res

    def _ctrl(self, obj, funcName, funcList):
        if funcName in ['text_replace', 'Text_replace']:
            return self._funTextReplace(obj, funcList)
        elif funcName in ['text_sub', 'Text_sub']:
            return self._funTextSub(obj, funcList)
        elif funcName in ['text_strip', 'Text_strip']:
            return self._funTextStrip(obj, funcList)
        elif funcName in ['list_to_str', 'List_to_str']:
            return self._funListToStr(obj, funcList)
        elif funcName in ['re_handle', 'Re_handle']:
            return self._funReHandle(obj, funcList)

    def _funReHandle(self, obj, rule):

        if len(rule) != 2:
            # print('{}参数错误'.format("re_handle"))
            logging.error('{}参数错误'.format("re_handle"))
            return []
        dec = DataExtractCenter()
        res = []

        if isinstance(obj, list) and not self._dataListToStr:
            for o in obj:
                if isinstance(o, str):
                    rule[0] = rule[0].replace('\\\\', '\\')
                    res.append('|'.join(dec.extract(o, ['re', rule[0], rule[1]])))
            return res

        if isinstance(obj, list) and self._dataListToStr:
            tmp = ''.join(obj)
            rule[0] = rule[0].replace('\\\\', '\\')
            return dec.extract(tmp, ['re', rule[0], rule[1]])

        if isinstance(obj, str):
            rule[0] = rule[0].replace('\\\\', '\\')
        return dec.extract(obj, ['re', rule[0], rule[1]])

    # ['text_strip', 'lr']
    def _funTextStrip(self, obj, rule):
        if len(rule) != 1:
            # print('{}参数错误'.format("list_to_str"))
            logging.error('{}参数错误'.format("list_to_str"))
            return []

        res = []
        if isinstance(obj, list) and not self._dataListToStr:
            for o in obj:
                if isinstance(o, str):
                    if rule[0] == 'l':
                        res.append(o.lstrip())
                    elif rule[0] == 'r':
                        res.append(o.rstrip())
                    elif rule[0] == 'lr':
                        res.append(o.strip())
            return res

        tmp = ''
        if isinstance(obj, list) and self._dataListToStr:
            tmp = ''.join(obj)

        if rule[0] == 'l':
            return tmp.lstrip()
        elif rule[0] == 'r':
            return tmp.rstrip()
        elif rule[0] == 'lr':
            return tmp.strip()

    # ['text_sub', '中', '码', 'I']
    def _funTextSub(self, obj, rule):
        if len(rule) != 3:
            # print('{}参数错误'.format("text_sub"))
            logging.error('{}参数错误'.format("text_sub"))
            return []
        res = []
        if isinstance(obj, list) and not self._dataListToStr:
            for o in obj:
                if isinstance(o, str):
                    try:
                        begin_index = 0 if rule[0] == '' else o.index(rule[0])
                        end_index = len(o) if rule[1] == '' else o.index(rule[1]) + len(rule[1])

                        if rule[2] != 'I':
                            begin_index += len(rule[0])
                            end_index -= len(rule[1])
                    except:
                        begin_index = 0
                        end_index = len(o)
                    print(len(o), begin_index, end_index)
                    tmp = o[begin_index:end_index]
                res.append(tmp)
            return res

        if isinstance(obj, list) and self._dataListToStr:
            tmp = ''.join(obj)
        try:
            begin_index = 0 if rule[0] == '' else tmp.index(rule[0])
            end_index = len(tmp) if rule[1] == '' else tmp.index(rule[1]) + len(rule[1])
            if rule[2] != 'I':
                begin_index += len(rule[0])
                end_index -= len(rule[1])
        except:
            begin_index = 0
            end_index = len(tmp)
        tmp = tmp[begin_index:end_index]
        return tmp

    # ['list_to_str', '>']
    @staticmethod
    def _funListToStr(obj, rule):
        if len(rule) != 1:
            # print('{}参数错误'.format("list_to_str"))
            logging.error('{}参数错误'.format("list_to_str"))
            return []

        if isinstance(obj, list):
            return '{}'.format(rule[0]).join(obj)
        elif isinstance(obj, str):
            return obj
        else:
            return []

    # ['text_replace', 'c', '+++']
    def _funTextReplace(self, obj, rule):
        if len(rule) != 2:
            # print('{}参数错误'.format("text_replace"))
            logging.error('{}参数错误'.format("text_replace"))
            return []

        res = []
        if isinstance(obj, list):
            if not self._dataListToStr:
                for o in obj:
                    if isinstance(o, str):
                        res.append(o.replace(rule[0], rule[1]))
                return res
            else:
                return ''.join(obj).replace(rule[0], rule[1])

        return obj.replace(rule[0], rule[1])

    @staticmethod
    def _iniStrToList(strS):
        if len(strS) != 0:
            return strS.replace('[', '').replace(']', '').replace(' ', '').split(',')
        else:
            return []


# def main():
#     dh = DataHandleCenter()
#     # res = dh.handle(['jack','lucy','tim'], ['list_to_str', '>'])
#     # res = dh.handle(['jack','lucy','tim'], ['text_replace', 'c', '+++'])
#     res = dh.handle(['ja13nck 12nc non43n'], ['re_handle', '(\d+)(n)(c)', '[P1]_[P2]+++[P3]'])
#     # res = dh.handle(['你好 中国码，我来','设置中你个，号码。子啊键'], ['text_sub', '中', '码', 'I'])
#     print(res)
#
#
# if __name__ == '__main__':
#     main()
