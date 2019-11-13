# coding:utf-8
import re
import time
import os
import datetime

"""
DataHandleC类：数据处理类，处理字段数据 以及创建URL
"""


class DataHandleC:

    def __init__(self):
        pass

    def CreateURL(self, url_rule=[], url=''):
        res_list = []
        url_rule_tmp = url_rule

        rule_count = len(url_rule_tmp)
        url_para_re = re.findall(re.compile(r'\[P\d+\]'), url)
        print('\t\t\t共{}个规则，{}个参数<{}>'.format(str(rule_count), len(url_para_re), url_para_re))

        # 规则只有一个 并且 参数只有一个
        if rule_count == len(url_para_re) == 1:
            # 方法名
            rule_more_func = url_rule_tmp[0]['u_func'][0]
            # 参数表
            rule_more_func_para = url_rule_tmp[0]['u_func'].copy()
            rule_more_func_para.pop(0)
            # print(rule_more_func)
            # print(rule_more_func_para)

            # 如果方法是 NUM_ADD
            if rule_more_func == 'NUM_ADD':
                # 获取构造好的参数列表
                # print('数值改变')
                res_list_tmp = self.CreateURL_FuncNumAdd(str_para_rule=rule_more_func_para)
            elif rule_more_func == 'TEXT_REPLACE':
                # print('文本替换')
                res_list_tmp = self.CreateURL_FuncTextReplace(str_para_rule=rule_more_func_para)
            elif rule_more_func == 'TIME_ADD':
                # print('时间替换')
                res_list_tmp = self.CreateURL_FuncTimeAdd(str_para_rule=rule_more_func_para)
            else:
                print('未知方法')

            # 有数据返回 开始填充
            if len(res_list_tmp) != 0:
                # 将数据填充到返回列表中 （url的参数铆钉符替换为参数）
                for rlt in res_list_tmp:
                    res_list.append(
                        url.replace(''.join(url_para_re), rlt)
                    )
        # 多参数 多规则
        elif rule_count == len(url_para_re) > 1:
            self.TipsFormat(2, '当前版本不支持 URL多参数')

        # 配置不符合要求
        else:
            self.TipsFormat(1, 'URL的模板参数和URL参数数目不相同')
        return res_list

    @staticmethod
    def TipsFormat(grade=0, info='none'):
        """打印有 格式的提示
        :param grade:信息的等级 从告到地 error warn info
        :param info:信息的载荷
        """
        grade = 'error' if grade == 1 else 'warn' if grade == 2 else 'info'
        print('<{}> [{}]---{}'.format(str(time.strftime('%H:%M:%S', time.localtime(time.time()))), grade, info))

    def CreateURL_FuncNumAdd(self, str_para_rule=[]):
        res_list = []
        begin = int(str_para_rule[0])
        step = int(str_para_rule[2])
        end = int(str_para_rule[1])
        completion_num = int(str_para_rule[3])

        # 检查参数是否异常
        if (not ((end > begin and step > 0) or (end < begin and step < 0))) or (0 == 1):
            self.TipsFormat(2, 'URL的模板参数异常 字段<func_para>')
            return res_list

        tmp = 0
        for t in range(begin, end + 1, step):
            if completion_num != 0 and len(str(t)) < completion_num:
                tmp = completion_num - len(str(t))
            res_list.append("{}".format("0" * tmp + str(t)))
            tmp = 0
        return res_list

    def CreateURL_FuncTextReplace(self, str_para_rule=[]):
        txt_path = str_para_rule[0]
        if os.path.isfile(txt_path):
            self.TipsFormat(0, '开始读取 {} 文本'.format(txt_path))
            with open(txt_path, 'r', encoding='utf-8-sig') as f:
                completion_txt_list = f.read().split('\n')
            # print(completion_txt_list)
            self.TipsFormat(0, '完成的文本读入')
            return completion_txt_list
        else:
            self.TipsFormat(2, '<u_func>中指定的文件不存在')

    @staticmethod
    def CreateURL_FuncTimeAdd(str_para_rule=[]):
        res_list = []

        # 开始时间
        begin_time = str_para_rule[0]
        # 时间偏移依据
        offset_set = str_para_rule[1]
        # 时间偏移
        offset = str_para_rule[2]
        # 输出时间 模板
        out_mode_format = str_para_rule[3]

        # print('begin_time', begin_time)
        # print('offset_set', offset_set)
        # print('offset', offset)
        # print('out_mode_format', out_mode_format)

        if offset_set == 'Y':
            # print('Y')
            pass
        elif offset_set == 'm':
            # print('m')
            pass
        elif offset_set == 'd':
            # print('d')
            bt = datetime.datetime.strptime(begin_time, '%Y-%m-%d')
            for t in range(1, int(offset) + 1):
                delta = datetime.timedelta(days=t)
                n_day = (bt + delta).strftime(out_mode_format)
                res_list.append(str(n_day))
        # print(res_list)
        return res_list


def main():
    pass


if __name__ == '__main__':
    main()
