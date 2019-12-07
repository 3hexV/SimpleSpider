# coding:utf-8
from simple_spider.sys_func.datahub import DataHub


class NumAutoChange:
    '''
    数值自动改变
    传入改变的规则和输入模式
    调用runOne 即可获取每次的改变值
    当达到最大值 不会停止 会一直输出最大值
    不支持负数
    '''
    _is_int_flag = True
    _data_id = None

    def __init__(self, rule=[], mode='int'):
        if mode == 'int':
            self._is_int_flag = True
        elif mode == 'str':
            self._is_int_flag = False

        rule.append(rule[0] - rule[2])
        self._dh = DataHub()
        self._data_id = self._dh.put(rule)
        # print(self._dh.showAllDataItem())

    def runOne(self):
        data = self._dh.get(self._data_id)
        if (data[2] > 0 and data[4] < data[1]) or (data[2] < 0 and data[4] > data[1]):
            data[4] += data[2]
            res = data[4]
        else:
            res = data[4]
        self._dh.update(self._data_id, data)
        # print(self._dh.showAllDataItem())

        if self._is_int_flag:
            return res
        else:
            return '{}{}'.format(
                '0' * (data[3] - len(str(res)) if len(str(res)) < data[3] else 0),
                str(res)
            )

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

    def release(self):
        self._dh.clearAll()


# def main():
#     na = NumAutoChange([1, 5, 1, 3], mode='str')
#     print(na.runWhileOver())
#     na.release()
#
#
# if __name__ == '__main__':
#     main()
