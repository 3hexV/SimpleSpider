# coding:utf-8
from simple_spider.sys_func.filePathCalc import FilePathCalc


def main():
    fpc = FilePathCalc()
    fpc.checkDir()
    if fpc.dirAbnormalFlag:
        print('工作目录不全，工作环境异常')
        return 0
    print('工作目录完整')


if __name__ == '__main__':
    main()