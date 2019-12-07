# coding:utf-8
import configparser
import os


class FilePathCalc:
    dirAbnormalFlag = False

    def __init__(self, sysPath=''):
        self.cp = configparser.ConfigParser()
        self.cp.read(sysPath, encoding='utf-8')

        self.workpath = self.cp.get('Ini Path', 'workpath')

        self.userconfig = self.workpath + self.cp.get('User Path', 'userconfig')
        self.usertestconfig = self.workpath + self.cp.get('User Path', 'usertestconfig')
        self.userres = self.workpath + self.cp.get('User Path', 'userres')
        self.usercachepage = self.workpath + self.cp.get('User Path', 'usercachepage')
        self.userresdata = self.workpath + self.cp.get('User Path', 'userresdata')

        self.root = self.workpath + self.cp.get("Sys Path", 'root')
        self.funcex = self.workpath + self.cp.get("Sys Path", 'funcex')
        self.sysres = self.workpath + self.cp.get('Sys Path', 'sysres')
        self.syslog = self.workpath + self.cp.get('Sys Path', 'syslog')
        self.systmp = self.workpath + self.cp.get('Sys Path', 'systmp')
        self.sysspiderlib = self.workpath + self.cp.get('Sys Path', 'sysspiderlib')

        # print(self.workpath)
        # print(self.userconfig)
        # print(self.usertestconfig)
        # print(self.userres)
        # print(self.usercachepage)
        # print(self.userresdata)
        #
        # print(self.root)
        # print(self.funcex)
        # print(self.sysres)
        # print(self.systmp)

    def checkDir(self):
        print("工作目录 -- {}".format(self._boolToTip(os.path.isdir(self.workpath))))

        print("用户配置文件所在目录 -- {}".format(self._boolToTip(os.path.isdir(self.userconfig))))
        print("用户测试配置文件所在目录 -- {}".format(self._boolToTip(os.path.isdir(self.usertestconfig))))
        print("用户资源文件所在目录 -- {}".format(self._boolToTip(os.path.isdir(self.userres))))

        print("缓存文件所在目录 -- {}".format(self._boolToTip(os.path.isdir(self.usercachepage))))
        print("爬取结果文件所在目录 -- {}".format(self._boolToTip(os.path.isdir(self.userresdata))))

        print("系统函数资源文件所在目录 -- {}".format(self._boolToTip(os.path.isdir(self.sysres))))
        print("系统缓存文件所在目录 -- {}".format(self._boolToTip(os.path.isdir(self.systmp))))
        print("系统日志文件所在目录 -- {}".format(self._boolToTip(os.path.isdir(self.syslog))))
        print("扩展函数文件所在目录 -- {}".format(self._boolToTip(os.path.isdir(self.funcex))))
        print("根目录 -- {}".format(self._boolToTip(os.path.isdir(self.root))))
        print("爬虫主要工作目录 -- {}".format(self._boolToTip(os.path.isdir(self.sysspiderlib))))

    def returnFilePath(self, desc, fileName):
        if desc == 'userconfig':
            return self.userconfig + fileName
        elif desc == 'usertestconfig':
            return self.usertestconfig + fileName
        elif desc == 'userres':
            return self.userres + fileName
        elif desc == 'userresdata':
            return self.userresdata + fileName
        elif desc == 'usercachepage':
            return self.usercachepage + fileName
        elif desc == 'root':
            return self.root + fileName
        elif desc == 'systmp':
            return self.systmp + fileName
        elif desc == 'sysres':
            return self.sysres + fileName
        elif desc == 'funcex':
            return self.funcex + fileName
        elif desc == 'sysspiderlib':
            return self.sysspiderlib + fileName
        elif desc == 'syslog':
            return self.syslog + fileName

    def _boolToTip(self, boolV):
        if not boolV:
            self.dirAbnormalFlag = True
        return '存在' if boolV else '缺失'


# def main():
#     fpc = FilePathCalc('./syspath.ini')
#     res = fpc.returnFilePath('userconfig', 'config_1.json')
#     res = fpc.returnFilePath('usertestconfig', 'config_1.json')
#     fpc.checkDir()
#     print(res)
#
#
# if __name__ == '__main__':
#     main()