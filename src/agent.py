# -*- coding: UTF-8 -*-
'''
Created on 2016年4月15日

@author: leftstone
'''

import requests
import time

ips = None


def getAgent():
    agent_param = {
        "orderid": "956145339966866",
        "num": "50",
        "protocol": "2",
        "sep": "2"}

    r = requests.get("http://dev.kuaidaili.com/api/getproxy", params=agent_param)
    return r.content.split('\n')


print requests.get("http://www.51job.com")


def test_ip(ip):
    #     ip = "111.56.32.72:80"
    #     ip = "101.200.165.93:80"
    # agent_ip = "202.100.167.137:80"
    # ip:125.40.26.102:9999 agent time:0.27s
    # ip:27.46.36.210:8118 agent time:0.06s
    proxies = {
        "http": ip,
        "https": ip,
    }

    t0 = time.time()
    r = requests.get("http://www.51job.com/", proxies=proxies)
    print "ip:%s agent time:%.2fs" % (ip, (time.time() - t0))


# ip = "101.200.165.93:80"
# ip = "118.26.118.15:9999"
# 111.161.126.106:80
# 210.101.131.229:8088

if 1:
    agent_ip = "111.161.126.106:80"
    test_ip(agent_ip)
else:
    ips = getAgent()
    print ips
    for idx, ip in enumerate(ips):
        print idx
        try:
            test_ip(ip)
        except:
            pass