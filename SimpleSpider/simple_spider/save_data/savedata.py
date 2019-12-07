# coding: utf-8
import configparser
import pymongo
from simple_spider.sys_func.filePathCalc import FilePathCalc
import json
import shutil
import logging


class SaveData:
    mongodbClient = None
    collection = None

    def __init__(self, tmpPath='', saveRule=[]):
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

        self.ctrl(tmpPath=tmpPath, saveRule=saveRule)

    def ctrl(self, tmpPath='', saveRule=[]):
        if self.abnormalFlag:
            return 0

        saveFunc = saveRule.split('(')[0]
        savePara = saveRule.split('(')[1].replace(')', '').split('.')
        print("[~]保存方法：{}\n[~]保存参数：{}".format(saveFunc, savePara))
        logging.debug("保存方法：{}".format(saveFunc))
        logging.debug("保存参数：{}".format(savePara))
        logging.debug("临时文件位置：{}".format(tmpPath))
        if saveFunc == 'mongo':
            self._MongoDBInsert(tmpPath=tmpPath, savePara=savePara)
        elif saveFunc == 'json':
            self._JsonSaveData(tmpPath=tmpPath, savePara=savePara)

    def _JsonSaveData(self, tmpPath='', savePara=[]):
        savePath = self.fpc.returnFilePath('userresdata', '.'.join(savePara))

        print("\n[~]保存位置：{}".format(savePath))
        logging.debug("保存位置：{}".format(savePath))

        shutil.copyfile(tmpPath, savePath)

        print('[~]json保存完成')
        logging.debug('json保存完成')

    def _initConfig(self):
        cp = configparser.ConfigParser()
        cp.read(self.fpc.returnFilePath('sysspiderlib', 'spiderBaseConfig.ini'), encoding='utf-8-sig')
        self.mongodbHost = cp.get('MongoDB', 'mongodbHost')
        self.mongodbPort = int(cp.get('MongoDB', 'mongodbPort'))

        print("<数据保存>" + "-"*20)

    # 初始化mongodb
    def _MongoDBInit(self, savePare):
        self.mongodbClient = pymongo.MongoClient(host=self.mongodbHost, port=self.mongodbPort)
        self.collection = self.mongodbClient[savePare[0]][savePare[1]]
        print('[~]MongoDB连接地址：{}\n\t连接端口：{}'.format(self.mongodbHost, self.mongodbPort))
        logging.debug('MongoDB连接地址：{}\n连接端口：{}'.format(self.mongodbHost, self.mongodbPort))
        logging.debug('MongoDB连接已经建立')
        print('[~]MongoDB建立连接成功。连接位置：{}.{}'.format(savePare[0], savePare[1]))

    def _MongoDBInsert(self, tmpPath, savePara):
        self._MongoDBInit(savePara)

        with open(tmpPath, 'r', encoding='utf-8-sig') as f:
            dataList = f.read().split('\n')

        for i, dL in enumerate(dataList):
            if len(dL) != 0:
                dataList[i] = json.loads(s=dL)
            else:
                dataList.pop(i)

        # print(type(dataList), len(dataList))
        for dL in dataList:
            self.collection.insert(dL, check_keys=False)
        print('[~]数据插入MongoDB完成')
        logging.debug('数据插入MongoDB完成')

    def __del__(self):
        if self.mongodbClient is not None:
            self.mongodbClient.close()
            print('[~]MongoDB已经断开连接')
            logging.debug('MongoDB已经断开连接')
        else:
            # print('没有使用mongodb')
            pass
        print("-" * 20)

# def main():
#     sd = SaveData()
#     # sd.MongoDBInit()
#     # sd.MongoDBInsert()
#
#
# if __name__ == '__main__':
#     main()