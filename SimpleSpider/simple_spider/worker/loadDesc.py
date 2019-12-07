# coding:utf-8
from simple_spider.sys_func.filePathCalc import FilePathCalc
import re
import queue


class LoadDesc:
    spiderNameAndConfig = {}
    spiderFlowNameAndFlow = {}
    spiderFlowNameAndSave = {}
    resAllDesc = []

    def __init__(self):
        self.QE = queue.Queue()
        self.fpc = FilePathCalc(sysPath='../sys_func/syspath.ini')

    def load(self):
        descPath = self.fpc.returnFilePath('userconfig', 'proSpider.desc')
        # print(descPath)
        with open(descPath, 'r', encoding='utf-8') as f:
            descStr = f.read()

        # 载入爬虫配置
        spiderInfoTmp = [tmp.replace('newSpider', '').replace('(', '').replace(')', '')
                         for tmp in descStr.split('\n') if re.findall(r'^newSpider.*?$', tmp) != []]
        spiderFlowTmp = [tmp.replace('newDescFlow', '').replace('(', '').replace(')', '')
                         for tmp in descStr.split('\n') if re.findall(r'^newDescFlow.*?$', tmp) != []]
        spiderSaveDataTmp = [tmp.replace('save', '')
                             for tmp in descStr.split('\n') if re.findall(r'^save.*?$', tmp) != []]

        # print(spiderInfoTmp)

        # 构建爬虫名和爬虫配置文件对照表
        for sIT in spiderInfoTmp:
            tmp = sIT.split(',')
            self.spiderNameAndConfig[tmp[0].strip()] = tmp[1].strip()
        # 构建爬虫流程名和流程对照表
        for sFT in spiderFlowTmp:
            tmp = sFT.split(',')
            self.spiderFlowNameAndFlow[tmp[0].strip()] = tmp[1].strip().split('-')
        # 构建爬虫流程名和数据保存方式对照表
        for sSDT in spiderSaveDataTmp:
            tmp = sSDT.split(',')
            self.spiderFlowNameAndSave[tmp[0].strip()[1:]] = tmp[1].strip()[:-1]

        # print(spiderInfoTmp)
        # print(spiderFlowTmp)
        # print(spiderSaveDataTmp)

        # print(self.spiderNameAndConfig)
        # print(self.spiderFlowNameAndFlow)
        # print(self.spiderFlowNameAndSave)

        # 装载流程
        # 不做任何检查 所以一定要遵守基本写法
        for t in self.spiderFlowNameAndFlow.values():
            tmpQe = queue.Queue()
            for tt in t:
                tmpQe.put(self.spiderNameAndConfig[tt])
            self.QE.put(tmpQe)

        # print(self.QE.queue)

        self.resAllDesc.append(self.QE)
        self.resAllDesc.append(self.spiderNameAndConfig)
        self.resAllDesc.append(self.spiderFlowNameAndFlow)
        self.resAllDesc.append(self.spiderFlowNameAndSave)

        # while not self.QE.empty():
        #     tmp = self.QE.get()
        #     print('开始')
        #     while not tmp.empty():
        #         print(tmp.get())
        #     print('结束')


# def main():
#     ld = LoadDesc()
#     ld.load()
#     print(ld.resAllDesc)
#
#
# if __name__ == '__main__':
#     main()