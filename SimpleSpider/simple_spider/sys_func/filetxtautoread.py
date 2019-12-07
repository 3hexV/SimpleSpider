# coding:utf-8
from simple_spider.sys_func.datahub import DataHub


class FileTxtAutoRead:
    '''
    文本自动读入
    调用runOne 将数据依据间隔符号 sep_symbol输出
    '''
    _data_id = None
    _data_len = 0
    _now = 0

    def __init__(self, rule=[], sep_symbol='\n'):
        # 自定义编码格式
        encoding_str = rule[1] if rule[1] != 'def' else 'utf-8'
        encoding_str += '-sig' if encoding_str == 'utf-8' else ''

        with open(rule[0], 'r', encoding=encoding_str) as f:
            self._data = f.read().split(sep_symbol)

        self._data_len = len(self._data) - 1

    def runOne(self):
        if self._now >= self._data_len:
            res = self._data[self._data_len]
        else:
            res = self._data[self._now]
            self._now += 1
        return res

    def runWhileOver(self):
        res = []
        last = self.runOne()
        res.append(last)
        this = self.runOne()
        if this == last:
            return res
        res.append(this)
        while last != this:
            last = this
            this = self.runOne()
            if this == last:
                return res
            res.append(this)
        # res = list(set(res))
        return res


# def main():
#    ft = FileTxtAutoRead(['./1.txt', 'def'])
#    print(ft.runOne())
#    print(ft.runOne())
#    print(ft.runOne())
#    print(ft.runOne())
#
#
#
# if __name__ == '__main__':
#     main()
