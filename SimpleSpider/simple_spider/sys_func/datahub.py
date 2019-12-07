# coding:utf-8
import hashlib
import time
import math
import platform


class DataHub:

    # 数据存放出
    _tmpData = {}
    # -1为无限制
    _size_max = -1
    _regID = []

    '''
    数据中心
    临时存放数据的位置
    '''
    def __init__(self, size_max=0):
        # 获取数据中心最大值 默认无限制
        self._size_max = size_max if size_max != 0 else -1

    def put(self, data):
        if self._size_max != -1 and len(self._regID) >= self._size_max:
            print('DataHub中已经达到最大值，无法继续添加')
            return 0
        # 创建ID
        ID = self._createID()

        # 注册添加ID
        beforeLen = len(self._regID)
        self._regID.append(ID)
        self._regID = list(set(self._regID))
        afterLen = len(self._regID)
        if beforeLen == afterLen:
            print('插入时间间隔太短，或者发生哈希碰撞')
            return 0

        # 添加数据
        self._tmpData[ID] = [data]

        return ID

    def get(self, ID):
        if ID in self._regID:
            return self._tmpData[ID][0]
        else:
            print('没有这个ID对于的数据')
            return 0

    def update(self, ID, data):
        if ID in self._regID:
            self._tmpData[ID] = [data]
            return 1
        else:
            print('没有这个ID对于的数据')
            return 0

    def dele(self, ID):
        if len(self._regID) == 0:
            print('DataHub中已经没有数据了')
            return 0

        if ID in self._regID:
            self._tmpData.pop(ID)
            self._regID.pop(self._regID.index(ID))
            return 1
        else:
            print('没有这个ID对于的数据')
            return 0

    def _createID(self):
        return hashlib.md5(
            str(hashlib.md5(self._NowTime().encode('utf-8')).hexdigest() + str(time.clock()) +
                platform.platform().replace('-', '').replace('.', '')).encode('utf-8')
            ).hexdigest()

    def showAllDataItem(self):
        return self._tmpData

    def showDataItem(self):
        return len(self._regID)

    def clearAll(self):
        self._tmpData.clear()
        self._regID.clear()

    @staticmethod
    def _NowTime():
        return str(time.asctime()).replace(':', '').replace(' ', '').upper()


# def main():
#     DH = DataHub(size_max=1)
#     i = DH.put([1, 2, 3])
#     data = DH.get(i)
#     print(data)
#     data[0] = data[1] + data[2]
#     DH.update(i, data)
#     j = DH.put([5, 5, 444])
#     print(DH.showDataItem())
#     print(DH.showAllDataItem())
#
#     DH.dele(i)
#     print(DH.showDataItem())
#     print(DH.showAllDataItem())
#
#     DH.dele(j)
#     print(DH.showDataItem())
#     print(DH.showAllDataItem())
#
#
# if __name__ == '__main__':
#     main()