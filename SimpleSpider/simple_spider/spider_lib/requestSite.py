# coding:utf-8
import requests
import fake_useragent
import configparser
import os
from lxml import etree
import re
import random
from simple_spider.sys_func.filePathCalc import FilePathCalc
import logging


class RequestSite:
    _uaFrom = 1

    def __init__(self):
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
            logging.error('发生异常：{}'.format(e))
            self.abnormalFlag = True

    def download(self, url, headers={}):
        if self.abnormalFlag:
            return 0
        # 处理headers
        headers = self._handleHeaders(headers)

        respond = requests.get(url=url,
                               headers=headers)
        return respond.content

    def request(self, url, headers={}, post_data={}, rendering_mode='S', forceEncoding=""):
        if self.abnormalFlag:
            return 0

        # 加载强制编码规则
        self.forceEncoding = forceEncoding

        # 判断是否渲染 和渲染模式
        self._isRendering(rendering_mode)
        # self.Print(self.rendering_mode)

        # 处理headers
        headers = self._handleHeaders(headers)

        # 判断请求类型
        # 静态请求使用request库
        if self.rendering_mode == 'S':
            typeTmp = self._requestType(post_data=post_data)
            if typeTmp == 1:
                respond = requests.get(url=url,
                                       headers=headers)
            elif typeTmp == 2:
                respond = requests.post(url=url,
                                        headers=headers,
                                        data=post_data)
            # 判断是否使用强制编码
            if len(self.forceEncoding) == 0:
                encoding = self._analysisPageEncoding(respond.text)
            else:
                encoding = self.forceEncoding
                self.Print('[~]使用强制编码规则 {}'.format(self.forceEncoding))

            res = respond.content.decode(encoding=encoding)

            # 判断是否缓存网页
            if self._cacheSitePage:
                self._cachePage(url=url, pageStr=res, encoding=encoding)

            return res

    # 初始化配置
    def _initConfig(self):
        # 读取配置
        cp = configparser.ConfigParser()
        cp.read(self.fpc.returnFilePath('sysspiderlib', 'spiderBaseConfig.ini'), encoding='utf-8-sig')

        # 提取UA来源
        self._uaFrom = int(cp.get('Spider RequestSite', 'UA'))

        self._noSpiderTip = True if cp.get('Spider Work', 'NoSpiderTip') == 'true' else False

        # 默认强制使用的编码格式
        self._encodingNoFound = cp.get('Spider RequestSite', 'DefEncodingNoFound')

        # 是否缓存网页
        self._cacheSitePage = True if cp.get('Spider RequestSite', 'CacheSitePage') == 'true' else False

        # 常见网页后缀名
        self._defPageSuffix = self._iniStrToList(cp.get('Spider RequestSite', 'DefPageSuffix'))

        # 提取默认网页编码 并加入大写 小写 标题格式
        self._encodingList = self._iniStrToList(cp.get('Spider RequestSite', 'DefEncoding'))

        self._encodingList += [tmp.capitalize() for tmp in self._encodingList]
        self._encodingList += [tmp.upper() for tmp in self._encodingList]
        self._encodingList += [tmp.lower() for tmp in self._encodingList]
        self._encodingList = list(set(self._encodingList))

        # self.Print(self._uaFrom)
        # self.Print(self._encodingList, type(self._encodingList))
        # self.Print(self._defPageSuffix, type(self._defPageSuffix))

    # 判断是否 进行渲染 以及渲染模式  默认不进行渲染
    # S: static 静态请求 不进行渲染
    # D_0: 使用chrome_driver 驱动谷歌浏览器 进行渲染
    # D_1: 使用firefox_driver 驱动火狐浏览器 进行渲染
    # D_2: 使用phantomJS 驱动无头浏览器 进行渲染
    # D_3: 使用request_html 进行渲染
    def _isRendering(self, rendering_mode):
        if rendering_mode == 'S' or len(rendering_mode) == 0:
            self.rendering_mode = 'S'
        elif rendering_mode[:2] == 'D_':
            self.rendering_mode = 'D'

    # 判断请求类型 根据传入的post_data产生是否为空 默认为get方式
    # 1:get 2:post
    @staticmethod
    def _requestType(post_data={}):
        if len(post_data) == 0:
            return 1
        else:
            return 2

    # 检查headers
    # 1.headers是否为空 为空时加入UA（随机生成的）
    # 2.是否有UA 没有则使用随机UA 或 或者使用来源文件的UA（随机从文件中取出一个）
    def _handleHeaders(self, headers):
        if len(headers) == 0:
            # 使用随机UA
            headers['User-Agent'] = fake_useragent.UserAgent().random
            return headers
        else:
            # 如果headers不为空 且存在user-agent 直接返回
            if 'User-Agent' in list(headers.keys()):
                return headers
            # headers中缺少 ua
            else:
                if self._uaFrom == 1:
                    headers['User-Agent'] = fake_useragent.UserAgent().random
                elif self._uaFrom == 2:
                    with open(os.path.join(os.path.abspath('../res'), 'UA.txt'), 'r', encoding='utf-8-sig') as f:
                        res = f.read().split('\n')
                    if len(res) != 0 and res != ['']:
                        headers['User-Agent'] = res[random.randint(0, len(res)) - 1]
                    else:
                        self.Print('UA.txt文件为空，自动创建UA')
                        headers['User-Agent'] = fake_useragent.UserAgent().random
                return headers

    def _analysisPageEncoding(self, pageStr):
        # 1.Xpath提取
        lxmlPage = etree.HTML(pageStr)
        encodingList = lxmlPage.xpath('//meta/@charset')
        encodingList += [''.join(re.findall(r'charset=(.*)', tmp)[0]) for tmp in lxmlPage.xpath('//meta['
                                                                                                '@http-equiv="content'
                                                                                                '-type"]/@content')]
        # self.Print(encodingList)
        encoding = self._getListCoincidenceOnce(encodingList, self._encodingList)
        if encoding is not None:
            self.Print("[~]网页编码格式为{}".format(encoding))
            logging.debug("网页编码格式为{}".format(encoding))
            return encoding

        # 2.正则提取
        encodingList.clear()
        encodingList = re.findall(r'charset=\"?(.*?)\"\s*/?>', pageStr)
        # self.Print(encodingList)
        encoding = self._getListCoincidenceOnce(encodingList, self._encodingList)
        if encoding is not None:
            # self.Print(encoding)
            self.Print("[~]网页编码格式为{}".format(encoding))
            logging.debug("网页编码格式为{}".format(encoding))
            return encoding

        # 3.返回默认的 强制编码
        self.Print('[!]没有发现编码格式，使用默认编码{}'.format(self._encodingNoFound))
        logging.warning('没有发现编码格式，使用默认编码{}'.format(self._encodingNoFound))
        return self._encodingNoFound

    # 获取两个列表的第一个交集对象 并返回
    @staticmethod
    def _getListCoincidenceOnce(List1, List2):
        for L1 in List1:
            if L1 in List2:
                return L1
        return None

    @staticmethod
    def _iniStrToList(strS):
        if len(strS) != 0:
            return strS.replace('[', '').replace(']', '').replace(' ', '').split(',')
        else:
            return []

    # 缓存页面
    def _cachePage(self, url, pageStr, encoding):
        flag = False
        file_name = url.replace('\\', '_').replace('//', '_').replace('*', '_').replace('?', '_').replace(':', '') \
            .replace('"', '_').replace('<', '_').replace('>', '_').replace('/', '_').replace('|', '_').replace(' ', '') \
            .strip()
        for tmp in self._defPageSuffix:
            if re.search(re.compile(r'^.*?\.{}$'.format(tmp)), file_name) is not None:
                flag = True
                break
        if not flag:
            file_name += '.html'
        with open(os.path.join(os.path.abspath('../../result/cache_page'), file_name), 'w', encoding=encoding) as f:
            f.write(pageStr)
        self.Print('[~]{}缓存完成'.format(file_name))
        logging.debug('{}缓存完成'.format(file_name))

    def Print(self, info):
        if self._noSpiderTip:
            pass
        else:
            print(info)

#
# def main():
#     rs = RequestSite()
#     res = rs.request(url='https://www.cnblogs.com/hanmk/p/9843136.html',
#                      headers={
#                          'cookie': '_ga=GA1.2.1 719380925.1574583191; '
#                                    '__gads=ID=f3453840d3041fa3:T=1574583191:S=ALNI_Mb_upiEmwlfSdSkUNaQ82KsHxGVoA; '
#                                    '_gid=GA1.2.2106134220.1575203500 '
#                      })
#     # self.Print(res)
#
#
# if __name__ == '__main__':
#     main()
