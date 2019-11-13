# coding:utf-8
import re
import json
import time
'''
SaveDataC类：保存数据的类 其中包含保存数据的各种操作  和 检查保存方法的合法性的字段
'''


class SaveDataC:
    _def_func = ['mongo', 'json', 'mysql', 'txt']
    _save_data_count = 0

    def __init__(self, func='', para='', data=[], field_len=10000):

        if len(data) != 0:
            # 拿到 数据里字段最长的
            field_max_len = len(data[0])
            # for tmp in data:
            #     field_max_len = len(tmp) if field_max_len < len(tmp) else field_max_len

            # print(func, para, data, field_len, field_max_len)

            # 当数据不为空 且数据每条记录的字段数 和实际需求的一样
            if len(func) != 0 and data != [{}] and field_max_len == field_len:
                self._save_data_count = self.ChooseSaveData(func, para, data)
            else:
                self.TipsFormat(1, '方法为空，或者数据为空，以及其他异常')
                self._save_data_count = 0

    def GetSaveDataCount(self):
        return self._save_data_count

    def ChooseSaveData(self, func, para, data):
        if func == 'json':
            return self.WriteDataToJson(path=para, data=data)
        elif func == 'txt':
            return self.WriteDataToTxt(path=para, data=data)
        elif func == 'diy_desc':
            return self.WriteDataToTxt(path=para, data=data)
        else:
            self.TipsFormat(2, '不支持该方法保存 <{}>'.format(func))
            return 0

    def WriteDataToTxt(self, path, data):
        dict_tmp = {}
        moban = ''
        self.TipsFormat(0, '开始写入文件')
        for tmp in range(0, len(data)):
            dict_tmp[tmp] = data[tmp]
        with open(path, 'w', encoding='utf-8') as f:
            for d in data:
                for dd in d.keys():
                    moban += "{}:\n{}\n".format(dd, d[dd])
                f.write(moban+'\n')
                moban = ''
        self.TipsFormat(0, '写入文件完成 {}'.format(path))
        return len(data)

    def WriteDataToDiyDesc(self, path, data):
        dict_tmp = {}
        moban = ''
        self.TipsFormat(0, '开始写入文件')
        for tmp in range(0, len(data)):
            dict_tmp[tmp] = data[tmp]
        with open(path, 'w', encoding='utf-8') as f:
            for d in data:
                for dd in d.keys():
                    moban += "{}:\n{}\n".format(dd, d[dd])
                f.write(moban + '\n')
                moban = ''
        self.TipsFormat(0, '写入文件完成 {}'.format(path))
        return len(data)

    def WriteDataToJson(self, path, data):
        dict_tmp = {}
        self.TipsFormat(0, '开始写入文件')
        for tmp in range(0, len(data)):
            dict_tmp[tmp] = data[tmp]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(fp=f, obj=dict_tmp, ensure_ascii=False)
        self.TipsFormat(0, '写入文件完成 {}'.format(path))
        return len(data)


    @staticmethod
    def TipsFormat(grade=0, info='none'):
        """打印有 格式的提示
        :param grade:信息的等级 从告到地 error warn info
        :param info:信息的载荷
        """
        grade = 'error' if grade == 1 else 'warn' if grade == 2 else 'info'
        print('<{}> [{}]---{}'.format(str(time.strftime('%H:%M:%S', time.localtime(time.time()))), grade, info))


def main():
    pass


if __name__ == '__main__':
    main()