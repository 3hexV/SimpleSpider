# coding:utf-8
import os
import configparser
from simple_spider.worker.spiderWork import SpiderWorker


def initSys():
    cp = configparser.ConfigParser()
    cp.read('./simple_spider/sys_func/syspath.ini', encoding='utf-8')
    # print(cp.sections())
    if cp.has_section('Ini Path'):
        cp.set('Ini Path', 'WorkPath', os.path.abspath('./'))
        cp.write(fp=open('./simple_spider/sys_func/syspath.ini', 'w', encoding='utf-8'))
        return 0

    print('[~]第一次初始化完成')
    cp.add_section('Ini Path')
    cp.set('Ini Path', 'WorkPath', os.path.abspath('./'))
    cp.write(fp=open('./simple_spider/sys_func/syspath.ini', 'w', encoding='utf-8'))


def main():
    initSys()
    os.chdir(os.getcwd() + r'/simple_spider/worker/')
    SpiderWorker()


if __name__ == '__main__':
    main()
