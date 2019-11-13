# coding:utf-8


class DataHubC:
    # DH的最大数据条数
    _max_id = 20
    _com_data_hub = []
    _surplus_id = _max_id
    _flag_list = []

    def __init__(self):
        pass

    # 注册使用DH
    def RegisterUseDH(self, flag, data=[]):
        if self._surplus_id > 0:
            self._com_data_hub.append({str(flag): data})
            self._flag_list.append(flag)
            self._surplus_id -= 1
            return True
        else:
            print('DataHub已经满了')
            return False

    # 根据flag获取 数据
    def GetDataFromDH(self, flag):
        for tmp in self._com_data_hub:
            if ''.join(tmp.keys()) == str(flag):
                return list(tmp.values())[0]
        return None

    # 显示DH中的所有值
    def ShowDHValues(self):
        # print(self._com_data_hub)
        return self._com_data_hub

    # 释放DH中所有的数据
    def ClearDHAll(self):
        self._com_data_hub.clear()
        self._flag_list.clear()
        self._surplus_id = self._max_id

    # 判断是否注册过
    def FlagIsReg(self, flag):
        if flag in self._flag_list:
            return True
        else:
            return False


def main():
    dh = DataHubC()
    # dh.RegisterUseDH('title')
    # dh.RegisterUseDH('title')
    # dh.RegisterUseDH('title')
    # dh.RegisterUseDH('title')
    # dh.ShowDHValues()
    # dh.ClearDHAll()
    # dh.ShowDHValues()




if __name__ == '__main__':
    main()