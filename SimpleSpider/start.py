# coding:utf-8
from SimpleSpider.SimpleSpiderMain import SimpleSpider


def main():
    ss = SimpleSpider('./config.json')
    ss.SpiderWork()


if __name__ == '__main__':
    main()