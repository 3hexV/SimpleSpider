# coding:utf-8
from simple_spider.spider_lib.requestSite import RequestSite
from simple_spider.spider_lib.dataExtractCenter import DataExtractCenter
from simple_spider.spider_lib.dataHandleCenter import DataHandleCenter
from simple_spider.sys_func.numberautochange import NumAutoChange
from simple_spider.sys_func.filetxtautoread import FileTxtAutoRead
from simple_spider.sys_func.filePathCalc import FilePathCalc
import queue
import configparser
import os
import threading
import time
import json
import re
import tempfile
import logging


# noinspection PyTypeChecker
class SuperSpider:
    _threadList = []
    _endFlag = False
    _dataCollect = {}
    _fieldDescDict = {}
    _fieldAutoChange = {}
    flowOutputData = None
    _urlList = []
    _cp = None
    _ex = None

    def __init__(self, configPath, flowInput=[]):
        self.fpc = FilePathCalc(sysPath='../sys_func/syspath.ini')

        # 日志文件
        logging.basicConfig(level=logging.DEBUG,
                            filename=self.fpc.returnFilePath('syslog', 'log.log'),
                            filemode='a',
                            format=
                            '%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S %p'
                            )

        # 临时文件
        self.tmpFile = tempfile.NamedTemporaryFile(mode='a+',
                                                   delete=False,
                                                   dir=self.fpc.systmp,
                                                   suffix='.tmp',
                                                   encoding='utf-8-sig')
        self.tmpPath = self.tmpFile.name

        # 初始化配置 和加载配置
        try:
            self._initConfig()
            self.abnormalFlag = False
            self._loadConfig(configPath=configPath, flowInput=flowInput)
        except Exception as e:
            self.abnormalFlag = True
            logging.error('发生异常：{}'.format(e))

        # 没有出现配置异常 开始任务的装载 等待start启动
        if not self.abnormalFlag:
            # 构建任务队列
            self._Locker = threading.Lock()
            self._url_queue = queue.Queue(maxsize=0)

            for tmp in self._urlList:
                self._url_queue.put(tmp)

            logging.debug("爬虫队列初始化完成")
            self.Print("[~]爬虫队列初始化完成")
        else:
            logging.error("爬虫配置异常，请确认使用专用爬虫的特殊字段名或者字段数")

    def _loadConfig(self, configPath, flowInput=[]):
        with open(configPath, 'r', encoding='utf-8-sig') as f:
            self._config = json.load(fp=f)
        # 加载爬虫类型
        self._Stype = self._config['Stype']

        # 加载headers
        self._headers = self._config['headers']

        # 加载post data
        self._post_data = self._config['post_data']

        # 加载 爬虫输入 输出流
        self._flowInput = self._config['flow_input']
        # self.Print('flow_input', self._flowInput)
        if self._flowInput == 'link':
            if len(flowInput) == 0:
                self.abnormalFlag = True
                logging.error("输入流启动，但是传入的数据为空")
                return 0
            else:
                self._urlList = flowInput
                logging.debug("输入流数据，已经加载")
        else:
            # 加载url规则
            if len(self._config['url']) == 1 or len(self._config['url'][1]) == 0:
                self._urlList.append(self._config['url'][0])
            elif len(self._config['url'][1]) != 0:
                self._urlList = self._urlCreate(urlBase=self._config['url'])

        self._flowOutput = self._config['flow_output']

        # 加载目标数据 和解析方式 处理方式
        self._fieldDict = self._config['field']
        # self.Print('_fieldDict', self._fieldDict.keys())

        # 获取字段描述
        for tmp in list(self._fieldDict.keys()):
            # 非空字段
            if tmp[:1] == '*':
                self._fieldDescDict[tmp] = ['not null', tmp[1:]]
            else:
                self._fieldDescDict[tmp] = ['none', tmp]

        if self._Stype not in ['f_file', 'f_img', 'url', 'text']:
            # self.Print(self._fieldDescDict)
            for fDD in list(self._fieldDescDict.keys()):
                if self._fieldDict[fDD][0][0] == 'num_change':
                    rule = self._fieldDict[fDD][0]
                    rule.pop(0)
                    self._fieldAutoChange[fDD] = NumAutoChange(rule=rule, mode='int')
                elif self._fieldDict[fDD][0][0] == 'text_read':
                    rule = self._fieldDict[fDD][0]
                    rule.pop(0)
                    rule[0] = '../../user_config/res/{}'.format(rule[0])
                    self._fieldAutoChange[fDD] = FileTxtAutoRead(rule=rule)

        # 加载扩展配置描述
        self._ex = self._config['ex']

        if self._Stype == 'general':
            logging.debug("通用爬虫")
            self.flowOutputData = []
        if self._Stype == 'url':
            logging.debug("专用爬虫_URL爬虫")
            self.flowOutputData = []
            if len(list(self._fieldDict.keys())) != 1 or ''.join(list(self._fieldDict.keys())) != 'URL':
                self.abnormalFlag = True
        if self._Stype == 'f_file':
            logging.debug("专用爬虫_文件爬虫")
            self.flowOutputData = {}
            if len(list(self._fieldDict.keys())) != 1 or ''.join(list(self._fieldDict.keys())) != 'F_FILE':
                self.abnormalFlag = True
        if self._Stype == 'f_img':
            logging.debug("专用爬虫_图片爬虫")
            self.flowOutputData = {}
            if len(list(self._fieldDict.keys())) != 1 or ''.join(list(self._fieldDict.keys())) != 'F_IMG':
                self.abnormalFlag = True
        if self._Stype == 'text':
            logging.debug("专用爬虫_文本爬虫")
            self.flowOutputData = []
            if len(list(self._fieldDict.keys())) != 1 or ''.join(list(self._fieldDict.keys())) != 'TEXT':
                self.abnormalFlag = True

        # self.Print(self._Stype)
        # self.Print(self._headers)
        # self.Print(self._post_data)
        # self.Print(self._urlList)
        # self.Print(self._fieldDict)
        # self.Print(self._fieldDescDict)
        # self.Print(self._fieldAutoChange)

    def _urlCreate(self, urlBase):
        resList = []
        urlM = urlBase[0]
        urlRName = urlBase[1][0]
        urlRRule = urlBase[1].copy()
        urlRRule.pop(0)

        resTmp = []
        if urlRName == 'num_change' and len(urlRRule) == 4:
            resTmp = NumAutoChange(urlRRule, mode='str').runWhileOver()
            logging.debug("URL构建_数值改变")
            self.Print("[~]URL构建_数值改变")
        elif urlRName == 'text_read' and len(urlRRule) == 2:
            logging.debug("URL构建_文本替换")
            self.Print("[~]URL构建_文本替换")
            urlRRule[0] = self.fpc.returnFilePath('userres', urlRRule[0])
            resTmp = FileTxtAutoRead(urlRRule, sep_symbol='\n').runWhileOver()
        else:
            logging.error("参数异常")

        para = re.findall(re.compile(r'\[P\d+\]'), urlM)
        if len(para) == 1:
            para = ''.join(para)
        else:
            logging.warning("现在仅支持一个参数")
            return []

        for nr in resTmp:
            resList.append(urlM.replace(para, nr))

        return resList

    def _initConfig(self):
        self._cp = configparser.ConfigParser()
        # self.Print(self.fpc.returnFilePath('sysspiderlib', 'spiderBaseConfig.ini'))
        # self.Print(os.path.isfile(self.fpc.returnFilePath('sysspiderlib', 'spiderBaseConfig.ini')))
        self._cp.read(self.fpc.returnFilePath('sysspiderlib', 'spiderBaseConfig.ini'), encoding='utf-8-sig')

        self._threadNumber = int(self._cp.get('Spider Work', 'ThreadNumber'))
        self._noSpiderTip = True if self._cp.get('Spider Work', 'NoSpiderTip') == 'true' else False
        self._threadNumber = 2 if self._threadNumber <= 2 else self._threadNumber if self._threadNumber <= 128 else 64

        self._threadSleepTime = int(self._cp.get('Spider Work', 'ThreadSleepTime')) / 1000

        logging.debug("线程数:{}".format(self._threadNumber))
        logging.debug("线程休眠时间:{}s".format(self._threadSleepTime))

    # 通用爬虫任务
    def _generalWork(self, tName=''):
        fieldNullFLag = False
        dataTmp = {}
        while not self._endFlag and not self._url_queue.empty():
            # 获取URL
            self._Locker.acquire()
            data = self._url_queue.get()
            self._Locker.release()

            # 请求网页
            logging.debug("线程：{} 开始运行".format(tName))
            logging.debug('开始请求: {}'.format(data))
            self.Print('\n[!]开始请求: {}'.format(data))
            res = RequestSite().request(url=data,
                                        headers=self._headers,
                                        post_data=self._post_data,
                                        forceEncoding=self._ex[2])

            # 开始解析网页
            dec = DataExtractCenter()
            dhc = DataHandleCenter()

            for fDD in self._fieldDescDict.keys():
                # 判断是函数控制输出 还是从源码中提取
                if fDD not in list(self._fieldAutoChange.keys()):
                    r = dec.extract(res, self._fieldDict[fDD][0])
                    # 处理数据
                    for fD in self._fieldDict[fDD][1]:
                        # 爬取数据为空 不进行数据处理了
                        if len(r) != 0:
                            logging.debug("{} 处理数据中：{}".format(fDD, fD))
                            r = dhc.handle(r, fD)

                    if len(r) == 0 or r == '':
                        if self._fieldDescDict[fDD][0] == 'not null':
                            fieldNullFLag = True
                        else:
                            logging.warning("{} 数据为空，已经忽略".format(fDD))
                            self.Print("[!]{} 数据为空，已经忽略".format(fDD))
                else:
                    logging.debug("{} 自动获取值".format(fDD))
                    r = self._fieldAutoChange[fDD].runOne()
                if fieldNullFLag:
                    logging.error('{}发现{}为空字段'.format(data, self._fieldDescDict[fDD][1]))
                    return {}
                if self._flowOutput == self._fieldDescDict[fDD][1]:
                    self.flowOutputData.append(r)
                dataTmp[self._fieldDescDict[fDD][1]] = r

            dataTmp['_URL'] = data
            self._dataCollect[data] = dataTmp.copy()
            # 写入到临时文件中
            self.tmpFile.write(json.dumps(obj=dataTmp, ensure_ascii=False) + '\n')

            time.sleep(self._threadSleepTime)

    # 专用爬虫任务 url任务
    def _urlWork(self, tName=''):
        # fieldNullFLag = False
        dataTmp = {}
        while not self._endFlag and not self._url_queue.empty():
            # 获取URL
            self._Locker.acquire()
            data = self._url_queue.get()
            self._Locker.release()

            # 请求网页
            logging.debug("线程：{} 开始运行".format(tName))
            logging.debug('开始请求: {}'.format(data))
            self.Print('\n[!]开始请求: {}'.format(data))
            res = RequestSite().request(url=data,
                                        headers=self._headers,
                                        post_data=self._post_data,
                                        forceEncoding=self._ex[2])

            # 1.开始解析网页
            dec = DataExtractCenter()
            dhc = DataHandleCenter()

            # 2.采集URL
            # 如果没有规则 则采集所有的URL
            if len(self._fieldDict["URL"][0]) == 0:
                self._fieldDict["URL"][0] = ["xpath", "//a/@href"]
            r = dec.extract(res, self._fieldDict["URL"][0])

            r = self._urlAnalysisHandle(data, r, 'url', self._ex[0], self._ex[1])

            # 3.处理数据
            for fD in self._fieldDict["URL"][1]:
                logging.debug("处理数据中：{}".format(fD))
                r = dhc.handle(r, fD)

            r = list(set(r))
            # 4.添加到输出流中
            self.flowOutputData = r

            # 5.添加返回数据中
            dataTmp['_URL'] = data
            dataTmp["URL"] = r
            self._dataCollect = dataTmp.copy()

            self.Print('[~]获取到{}个相关URL'.format(len(r)))
            logging.debug('获取到{}个相关URL'.format(len(r)))

            # 写入到临时文件中
            self.tmpFile.write(json.dumps(obj=dataTmp, ensure_ascii=False) + '\n')

            time.sleep(self._threadSleepTime)

    # 专用爬虫任务 text任务 文本任务
    def _textWork(self, tName=''):
        fieldNullFLag = False
        dataTmp = {}
        while not self._endFlag and not self._url_queue.empty():
            # 获取URL
            self._Locker.acquire()
            data = self._url_queue.get()
            self._Locker.release()

            # 请求网页
            logging.debug("线程：{} 开始运行".format(tName))
            logging.debug('开始请求: {}'.format(data))
            self.Print('\n[!]开始请求: {}'.format(data))
            res = RequestSite().request(url=data,
                                        headers=self._headers,
                                        post_data=self._post_data,
                                        forceEncoding=self._ex[2])

            # 1.开始解析网页
            dec = DataExtractCenter()
            dhc = DataHandleCenter()

            # 2.采集URL
            # 如果没有规则 则采集所有的URL
            if len(self._fieldDict["TEXT"][0]) == 0:
                self._fieldDict["TEXT"][0] = ["xpath", "//text()"]
            r = dec.extract(res, self._fieldDict["TEXT"][0])

            # 3.处理数据
            for fD in self._fieldDict["TEXT"][1]:
                logging.debug("处理数据中：{}".format(fD))
                r = dhc.handle(r, fD)

            # 4.添加到输出流中
            self.flowOutputData = r

            # 5.添加返回数据中
            dataTmp['_URL'] = data
            dataTmp["TEXT"] = r
            self._dataCollect[data] = dataTmp.copy()
            # 写入到临时文件中
            self.tmpFile.write(json.dumps(obj=dataTmp, ensure_ascii=False) + '\n')

            time.sleep(self._threadSleepTime)

    # 专用爬虫任务 文件任务 文件下载
    def _fFileWork(self, tName=''):
        while not self._endFlag and not self._url_queue.empty():
            # 获取URL
            self._Locker.acquire()
            data = self._url_queue.get()
            self._Locker.release()

            # 请求网页
            logging.debug("线程：{} 开始运行".format(tName))
            logging.debug('开始请求: {}'.format(data))
            self.Print('\n[!]开始请求: {}'.format(data))
            rs = RequestSite()
            try:
                res = rs.request(url=data,
                                 headers=self._headers,
                                 post_data=self._post_data,
                                 forceEncoding=self._ex[2])
            except:
                res = ''
            if res != '':
                # 1.开始解析网页
                dec = DataExtractCenter()

                # 2.采集
                # 如果没有规则 则采集所有的URL
                if len(self._fieldDict["F_FILE"][0]) == 0 or self._fieldDict["F_FILE"][0] == ['', '']:
                    self._fieldDict["F_FILE"][0] = ["xpath", "//a/@href"]

                imgUrl = dec.extract(res, self._fieldDict["F_FILE"][0])

                # 3.分析出文的url
                fileTmp = self._urlAnalysisHandle(data, imgUrl, 'file', suffixList=self._ex[0], urlMixRule=self._ex[1])
                fileTmp = list(set(fileTmp))

                logging.debug('一个发现{}个文件'.format(len(fileTmp)))
                self.Print('[\]一个发现{}个文件'.format(len(fileTmp)))

                for ft in fileTmp:
                    content = rs.download(url=ft)
                    domainName = ''.join(re.findall(r'http[s]?://([\w+\.]+)/.*?', ft))
                    FileName = ''.join(re.findall(r'^.*/(.*?)$', ft))
                    if not os.path.exists('{}FILE_{}'.format(self.fpc.userresdata, domainName)):
                        os.makedirs('{}FILE_{}'.format(self.fpc.userresdata, domainName))
                    with open('{}FILE_{}/{}'.format(self.fpc.userresdata, domainName, FileName), 'wb') as f:
                        f.write(content)
            else:
                fileTmp = []
                logging.warning('站点请求失败')
                self.Print('[!]站点请求失败')
            # 写入到临时文件中
            self.flowOutputData[data] = len(fileTmp)
            self.tmpFile.write(json.dumps(obj={data: len(fileTmp)}, ensure_ascii=False) + '\n')

            time.sleep(self._threadSleepTime)

    # 专用爬虫任务 文件任务 图片下载
    def _fImgWork(self, tName=''):
        while not self._endFlag and not self._url_queue.empty():
            # 获取URL
            self._Locker.acquire()
            data = self._url_queue.get()
            self._Locker.release()

            # 请求网页
            logging.debug("线程：{} 开始运行".format(tName))
            logging.debug('开始请求: {}'.format(data))
            self.Print('\n[!]开始请求: {}'.format(data))
            rs = RequestSite()
            try:
                res = rs.request(url=data,
                                 headers=self._headers,
                                 post_data=self._post_data,
                                 forceEncoding=self._ex[2])
            except:
                res = ''

            if res != '':
                # 1.开始解析网页
                dec = DataExtractCenter()

                # 2.采集图片的可能URL
                # 如果没有规则 则采集所有的URL
                if len(self._fieldDict["F_IMG"][0]) == 0 or self._fieldDict["F_IMG"][0] == ['', '']:
                    self._fieldDict["F_IMG"][0] = ["xpath", "//img/@src"]

                imgUrl = dec.extract(res, self._fieldDict["F_IMG"][0])

                # 3.分析出图片的url
                fileTmp = self._urlAnalysisHandle(data, imgUrl, 'img', suffixList=self._ex[0], urlMixRule=self._ex[1])

                fileTmp = list(set(fileTmp))

                logging.debug('一个发现{}个图片'.format(len(fileTmp)))
                self.Print('[\]一个发现{}个图片'.format(len(fileTmp)))

                for ft in fileTmp:
                    content = rs.download(url=ft)
                    domainName = ''.join(re.findall(r'http[s]?://([\w+\.]+)/.*?', ft))
                    ImgName = ''.join(re.findall(r'^.*/(.*?)$', ft))
                    if not os.path.exists('{}IMG_{}'.format(self.fpc.userresdata, domainName)):
                        os.makedirs('{}IMG_{}'.format(self.fpc.userresdata, domainName))
                    with open('{}IMG_{}/{}'.format(self.fpc.userresdata, domainName, ImgName), 'wb') as f:
                        f.write(content)
            else:
                fileTmp = []
                logging.warning('站点请求失败')
                self.Print('[!]站点请求失败')

            self.flowOutputData[data] = len(fileTmp)
            self.tmpFile.write(json.dumps(obj={data: len(fileTmp)}, ensure_ascii=False) + '\n')

            time.sleep(self._threadSleepTime)

    def start(self, tmp='./tmpRes.json', isTest=False):
        if self.abnormalFlag:
            return {}

        for i in range(0, self._threadNumber):
            if self._Stype == 'general':
                # 通用爬虫
                t = threading.Thread(target=self._generalWork('<Currency_T{}>'.format(str(i))),
                                     name='<Currency_T{}>'.format(str(i)))
            elif self._Stype == 'url':
                # url爬虫
                t = threading.Thread(target=self._urlWork('<Currency_T{}>'.format(str(i))),
                                     name='<URL_T{}>'.format(str(i)))
            elif self._Stype == 'f_file':
                # 文件爬虫
                t = threading.Thread(target=self._fFileWork('<Currency_T{}>'.format(str(i))),
                                     name='<F_FILE_T{}>'.format(str(i)))
            elif self._Stype == 'f_img':
                # 图片爬虫
                t = threading.Thread(target=self._fImgWork('<Currency_T{}>'.format(str(i))),
                                     name='<F_IMG_T{}>'.format(str(i)))
            elif self._Stype == 'text':
                # 文本爬虫
                t = threading.Thread(target=self._textWork('<Currency_T{}>'.format(str(i))),
                                     name='<Text_T{}>'.format(str(i)))
            self._threadList.append(t)
            t.setDaemon(True)
            t.start()

        # 停止线程
        self._endFlag = True
        for tl in self._threadList:
            tl.join()

        # 关闭临时文件
        self.tmpFile.close()

        # 如果是测试启动 打印测试数据
        if isTest:
            # 完成爬取
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(fp=f, obj=self._dataCollect, ensure_ascii=False)
            self.Print('-------------------------------')
            self.Print('[~]字段基本信息：')
            for fDD in self._fieldDescDict.keys():
                self.Print('\t字段名：{}\n\t字段属性：{}\n\t字段真实保存的名字：{}\n'.format(fDD,
                                                                          self._fieldDescDict[fDD][0],
                                                                          self._fieldDescDict[fDD][1]))

            self.Print('[~]字段提取规则和数据处理规则描述：')
            for fD in self._fieldDict.keys():
                self.Print('\t字段名：{}\n\t字段提取规则：{}\n\t字段数据处理规则：{}\n'.format(fD,
                                                                           self._fieldDict[fD][0],
                                                                           self._fieldDict[fD][1]))

            self.Print('[~]返回数据已经写入：\n\t{}'.format(tmp))

            self.Print('[~]输入流参数：\n\t{}'.format(self._flowInput))
            self.Print('[~]输出流参数：\n\t{}'.format(self._flowOutput))
            self.Print('[~]输出流输出的数据为：\n\t{}'.format(self.flowOutputData))
            self.Print('-------------------------------')

        self.clearAll()
        return self.flowOutputData

    def clearAll(self):
        self._Stype = ''
        self._config.clear()
        self._post_data.clear()
        self._headers.clear()
        self._fieldDescDict.clear()
        self._fieldDict.clear()
        self._ex.clear()
        self._urlList.clear()
        self._fieldAutoChange.clear()
        self._dataCollect.clear()

    @staticmethod
    def _iniStrToList(strS):
        if len(strS) != 0:
            return strS.replace('[', '').replace(']', '').replace(' ', '').split(',')
        else:
            return []

    # url处理
    def _urlAnalysisHandle(self, aimUrl, urlList, Stype, suffixList, urlMixRule='@DN'):
        resList = []
        if len(suffixList) == 0:
            if Stype == 'file':
                suffix = self._iniStrToList(self._cp.get('Spider Work', 'F_FILE_Spider_Suffix'))
            elif Stype == 'img':
                suffix = self._iniStrToList(self._cp.get('Spider Work', 'F_IMG_Spider_Suffix'))
            elif Stype == 'url':
                suffix = self._iniStrToList(self._cp.get('Spider Work', 'F_URL_Spider_Suffix'))
            else:
                domainName = ''.join(re.findall(r'(http[s]?://[\w+\.]+)/.*?', aimUrl))
                for uL in urlList:
                    if re.search(re.compile('^http[s]?.*$'), uL) is not None:
                        resList.append(uL)
                    else:
                        if urlMixRule == '@DN':
                            resList.append(domainName + uL)
                        elif urlMixRule == '@NP':
                            resList.append(aimUrl + uL)
                        else:
                            rule = urlMixRule.split('+')
                            if rule[0] == '@L':
                                resList.append(rule[1] + uL)
                            if rule[0] == '@R':
                                resList.append(uL + rule[1])
                return resList
        else:
            suffix = suffixList
        domainName = ''.join(re.findall(r'(http[s]?://[\w+\.]+)/.*?', aimUrl))
        for uL in urlList:
            for s in suffix:
                if re.search(re.compile(r'^.*?\.{}$'.format(s)), uL) is not None:
                    if re.search(re.compile('^{}.*$'.format(domainName)), uL) is not None:
                        resList.append(uL)
                    else:
                        if urlMixRule == '@DN':
                            resList.append(domainName + uL)
                        elif urlMixRule == '@NP':
                            resList.append(aimUrl + uL)
                        else:
                            rule = urlMixRule.split('+')
                            if rule[0] == '@L':
                                resList.append(rule[1] + uL)
                            if rule[0] == '@R':
                                resList.append(uL + rule[1])
        self.Print('[~]检索后缀名: {}'.format(suffix))
        self.Print('[~]拼接规则: {}'.format(urlMixRule))

        logging.debug('检索后缀名: {}'.format(suffix))
        logging.debug("拼接规则: {}".format(urlMixRule))
        return resList

    def Print(self, info):
        if self._noSpiderTip:
            pass
        elif not self._noSpiderTip:
            print(info)

# def main():
#     fpc = FilePathCalc(sysPath='../sys_func/syspath.ini')
#     # SuperSpider(fpc.returnFilePath('usertestconfig', 'config_1.json'), flowInput=[]).start()
#     SuperSpider(fpc.returnFilePath('userconfig', 'config_1.json'), flowInput=[]).start()
#
#
# if __name__ == '__main__':
#     main()
