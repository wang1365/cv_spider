# -*- coding: UTF-8 -*-
'''
Created on 2016年5月6日

@author: leftstone
'''
from splinter import Browser
import time
from lxml import etree
from string import strip
import re


def splinter():
    browser = Browser()
    url = "http://ehire.51job.com/MainLogin.aspx"
    browser.visit(url)
    time.sleep(1)
    browser.find_by_id('txtMemberNameCN').fill(u'安能聚业')
    browser.find_by_id('txtUserNameCN').fill(u'上海安能聚创供应链')
    browser.find_by_id('txtPasswordCN').fill('aneqc888')
    browser.find_by_id('Login_btnLoginCN').click()
    time.sleep(1)
    browser.find_by_tag('a').click()
    browser.find_by_id('hlResumeSearch').click()
    # id 85798642 未公开
    # 309554553 未下载
    #
    browser.find_by_id('txtUserID').fill('6098724')
    time.sleep(1)
    browser.find_by_id('btnSearchID_leftbtnSearchID').click()

    cvTarget = browser.find_by_xpath('//tr/td/p/span/a[@target="_blank"]')
    if len(cvTarget) == 0:
        print "can not find the cv from this id."
        return
    cvTarget.click()
    allwindows = browser.windows
    driver = browser.driver
    driver.switch_to_window(allwindows[-1].name)
    UndownloadLink = browser.find_by_id('UndownloadLink')
    if len(UndownloadLink) == 0:
        print "can not find the cv from this id."
    else:
        UndownloadLink.click()
        time.sleep(1)
        browser.find_by_id('btnCommonOK').click()
    selector = etree.HTML(browser.html)
    lines = selector.xpath('//title')
    if len(lines) != 0:
        print "name:", strip(lines[0].text)

    contents = browser.html.encode("utf-8")
    print re.findall(re.compile('''<td height="20">电　话：</td><td height="20" colspan="3">(.*?)<span'''), contents)[0]
    printre.findall(re.compile('''E-mail：</td><td height="20" colspan="3"><a href="mailto:(.*?)" class="blue">'''),
                    contents)[0]
    winNum = len(allwindows)
    for i in range(winNum):
        allwindows[winNum - 1 - i].close()


splinter()
print "done"
