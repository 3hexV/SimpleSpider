# coding:utf-8
import os
import queue
from simple_spider.spider_lib.superSpider import SuperSpider
from simple_spider.sys_func.filePathCalc import FilePathCalc
from simple_spider.worker.loadDesc import LoadDesc
from simple_spider.save_data.savedata import SaveData
import time
import logging


class SpiderWorker:

    abnormalFlag = False
    _allDesc = []
    _mongodbClient = None

    def __init__(self):
        self.fpc = FilePathCalc(sysPath='../sys_func/syspath.ini')

        logging.basicConfig(level=logging.DEBUG,
                            filename=self.fpc.returnFilePath('syslog', 'log.log'),
                            filemode='a',
                            format=
                            '%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S %p'
                            )

        # 清空临时文件
        tmpFileList = os.listdir(self.fpc.systmp)
        # print(tmpFileList)
        if len(tmpFileList) != 0:
            for tFL in tmpFileList:
                if tFL.split('.')[1] == 'tmp':
                    os.remove(self.fpc.returnFilePath('systmp', tFL))
        logging.debug('清空临时文件完成')

        # 清空缓存文件
        tmpFileList = os.listdir(self.fpc.usercachepage)
        # print(tmpFileList)
        if len(tmpFileList) != 0:
            for tFL in tmpFileList:
                os.remove(self.fpc.returnFilePath('usercachepage', tFL))
        logging.debug('清空缓存文件完成')

        if self._checkIsText() == 0 and not self.abnormalFlag:
            self._run()

    def _run(self):
        print('[~]运行模式')

        logging.debug('运行模式')
        logging.debug('开始加载流程描述文件')

        self.ld = LoadDesc()
        self.ld.load()
        self._allDesc = self.ld.resAllDesc

        self._saveFuncQueue = queue.Queue()
        for tmp in self._allDesc[3].keys():
            self._saveFuncQueue.put(self._allDesc[3][tmp])
        # print(self._saveFuncQueue.queue)

        # print(self._allDesc)
        logging.debug('流程描述加载完成')

        self.QE = self._allDesc[0]
        flowOutput = []

        beginTime = time.clock()

        flowNum = [0, 0]

        while not self.QE.empty():
            tmp = self.QE.get()
            flowNum[0] += 1
            while not tmp.empty():
                flowNum[1] += 1
                print('\n[~~]第{}流程，第{}个爬虫开始运行'.format(str(flowNum[0]), str(flowNum[1])))
                logging.debug('[~]第{}流程，第{}个爬虫开始运行'.format(str(flowNum[0]), str(flowNum[1])))
                configFile = tmp.get()
                configFile = self.fpc.returnFilePath('userconfig', configFile)
                # print(configFile)
                ss = SuperSpider(configPath=configFile, flowInput=flowOutput)
                flowOutput = ss.start(self.fpc.returnFilePath('usertestconfig', 'testRes.json'))
                tmpPath = ss.tmpPath
                logging.debug("临时文件位置：{}".format(tmpPath))
                logging.debug('[~]第{}流程，第{}个爬虫结束'.format(str(flowNum[0]), str(flowNum[1])))
                print('\n[~~]第{}流程，第{}个爬虫结束\n'.format(str(flowNum[0]), str(flowNum[1])))
            SaveData(tmpPath, self._saveFuncQueue.get())

        print("\n<信息>" + '-'*20)
        print('[~]花费时间{}s'.format(str(time.clock() - beginTime)))
        print('[~]日志文件：{}'.format(self.fpc.syslog))
        print("-"*20)

    def _checkIsText(self):
        # 0.清空测试结果文件
        testResFile = self.fpc.returnFilePath('usertestconfig', 'testRes.json')
        if os.path.exists(testResFile):
            os.remove(testResFile)

        # 1.判断test中是否存在 待测试文件
        fileALl = self._fileName(self.fpc.usertestconfig)

        if len(fileALl) == 0:
            # 运行模式
            return 0

        if len(fileALl) != 1:
            logging.warning("使用测试每次只能测试一个网址，只能存在一个json文件")
            print('使用测试每次只能测试一个网址，只能存在一个json文件')
            self.abnormalFlag = True
            return 0

        print('[~]测试模式')
        logging.debug("测试模式")

        # 开始测试
        configFile = fileALl[0]
        print('[~]---测试开始')
        logging.debug("测试开始")
        ss = SuperSpider(configPath=configFile, flowInput=[])
        ss.start(self.fpc.returnFilePath('usertestconfig', 'testRes.json'), isTest=True)
        print('[~]---测试完成')
        logging.debug("测试完成")
        return 1

    @staticmethod
    def _fileName(file_dir):
        FileList = []
        for root, dirs, files in os.walk(file_dir):
            for file in files:
                if os.path.splitext(file)[1] == '.json':
                    FileList.append(os.path.join(root, file))
        return FileList


# def main():
#     SpiderWorker()
#
#
# if __name__ == '__main__':
#     main()