# -*- coding: UTF-8 -*-
'''
Created on 2016年5月10日

@author: leftstone
'''
import logging.handlers


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class FetchLogger(object):
    def __init__(self, x=0):
        LOG_FILE = '../logs/fetch.log'
        fmt = '%(asctime)s - %(filename)s:%(funcName)s:%(lineno)s - %(name)s - %(message)s'
        fh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024,
                                                  backupCount=5)  # 实例化handler
        formatter = logging.Formatter(fmt)  # 实例化formatter
        fh.setFormatter(formatter)  # 为handler添加formatter

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger = self.logger = logging.getLogger('')  # 获取名为tst的logger
        logger.addHandler(fh)  # 为logger添加handler
        logger.addHandler(ch)
        logger.setLevel(logging.DEBUG)

    def getLogger(self):
        return self.logger
