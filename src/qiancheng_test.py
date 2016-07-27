#-*- coding: UTF-8 -*-
'''
Created on 2016年5月11日

@author: leftstone
'''

import requests
from lxml import etree
from urllib import quote
from urllib import unquote
import re
import cookielib
import urllib2
def urllib_test():
    loginUrl = "https://ehirelogin.51job.com/Member/UserLogin.aspx"
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    response = requests.get(loginUrl)
    print response.cookies
    print response

def test():
    s = requests.session()
    print "\n\ncookies0:"
    for k,v in s.cookies.items():
        print k,"====",v
    
    hd = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding":"gzip, deflate, sdch",
    "Accept-Language":"zh-CN,zh;q=0.8",
    "Cache-Control":"max-age=0",
    "Connection":"keep-alive",
    "Cookie":"guid=14357995489525990032; _ga=GA1.2.1189310845.1442582609; slife=mycenter_rsmtips%3D1%26%7C%26compfans%3D1%257C0%257C0%257C0%26%7C%26pmcsteup%3D1%26%7C%26lastvisit%3D070200; guide=1; collapse_expansion=1; EhireGuid=e0088ab378f94c8f89534ae32ffaa183; search=jobarea%7E%60070200%7C%21ord_field%7E%600%7C%21list_type%7E%600%7C%21recentSearch0%7E%602%A1%FB%A1%FA070200%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA%CB%E3%B7%A8%B9%A4%B3%CC%CA%A6%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1462678918%A1%FB%A1%FA0%A1%FB%A1%FA%7C%21recentSearch1%7E%602%A1%FB%A1%FA070200%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA%B0%AC%C1%AA%BF%C6%A1%FB%A1%FA1%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1461404386%A1%FB%A1%FA0%A1%FB%A1%FA%7C%21recentSearch2%7E%602%A1%FB%A1%FA070200%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA%BB%FA%C6%F7%D1%A7%CF%B0%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1462678906%A1%FB%A1%FA0%A1%FB%A1%FA%7C%21recentSearch3%7E%602%A1%FB%A1%FA070200%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA%CA%FD%BE%DD%CD%DA%BE%F2%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1461404821%A1%FB%A1%FA0%A1%FB%A1%FA%7C%21recentSearch4%7E%602%A1%FB%A1%FA070200%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA%CA%FD%BE%DD%CD%DA%BE%F2%B9%A4%B3%CC%CA%A6%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1462678646%A1%FB%A1%FA0%A1%FB%A1%FA%7C%21; AccessKey=b46232a75f284d4; LangType=Lang=&Flag=1",
    "Host":"ehire.51job.com",
    "Referer":"http://ehire.51job.com/Navigate.aspx?ShowTips=11&PwdComplexity=N",
    "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
    }
    loginUrl = "https://ehirelogin.51job.com/Member/UserLogin.aspx"
    
    res = s.get(loginUrl, headers =hd)
    print "\n\ncookies11:"
    for k,v in res.cookies.items():
        print k,"====",v
    
    print "\n\ncookies12:"
    for k,v in s.cookies.items():
        print k,"====",v
    with open("../tmp/result1.html","w") as f:
        f.write(res.content) 
    
    return 0
 
    selector = etree.HTML(res.content)
    hidLangType = selector.xpath('//input[@name="hidLangType"]/@value')[0]
    hidAccessKey = selector.xpath('//input[@name="hidAccessKey"]/@value')[0]
    hidEhireGuid = selector.xpath('//input[@name="hidEhireGuid"]/@value')[0]
    fksc = selector.xpath('//input[@name="fksc"]/@value')[0]
    txtPasswordCN = selector.xpath('//input[@name="txtPasswordCN"]')
    
    loginload = {
                "ctmName":quote("安能聚业"),
                "userName":quote("上海安能聚创供应链"),
                "password":"aneqc888",
                "checkCode":"",
                "oldAccessKey":hidAccessKey,
                "langtype":hidLangType,
                "isRememberMe":"false",
                "sc":fksc,
                "ec":hidEhireGuid,
                "returl":""}
    # for k,v in loginload.items():
    #     print k,"====",v
    
    hd = {"Origin":"http://ehire.51job.com",
          "Referer":"http://ehire.51job.com/MainLogin.aspx",
          "Upgrade-Insecure-Requests":"1",
          "Host":"ehirelogin.51job.com",
          "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0",
          "Accept-Language":"zh-CN,zh;q=0.8",
          "Accept-Encoding":"gzip, deflate",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection":"keep-alive",
            "CacheControl":"max-age=0",
            "Content-Type":"application/x-www-form-urlencoded"}
    
    res = s.post(loginUrl,data = loginload,headers = hd)
    print "\n\ncookies2:"
    for k,v in s.cookies.items():
        print k,"====",v
    with open("../tmp/result2.html","w") as f:
        f.write(res.content)
        
    selector = etree.HTML(res.content)
    __VIEWSTATE = selector.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
    postBackArg =  selector.xpath('//a')[0].get("href")
    p = re.compile(r'\'.*\'')
    args = p.findall(postBackArg)
    args = args[0].split(",")
    __EVENTTARGET = args[0][1:-1]
    __EVENTARGUMENT =args[1][1:-1]
    offlineData = {"__VIEWSTATE":__VIEWSTATE,"__EVENTTARGET":__EVENTTARGET,"__EVENTARGUMENT":__EVENTARGUMENT}
    qury_str = selector.xpath('//form[@method="post"]/@action')[0].split("?")[1]            
    url = "http://ehire.51job.com/Member/UserOffline.aspx?"+qury_str
    try:
        lastinfo = selector.xpath('//table/tr/td[@width="20%"]')
        lasttime = lastinfo[2].text
        other_ip = lastinfo[3].text
    except:
        lasttime = ""
        other_ip = ""
    print "post, url:",url
    res = s.post(url,data = offlineData,headers = hd)
    print("lasttime:%s,other_ip:%s"%(lasttime,other_ip))
    print "\n\ncookies3:"
    for k,v in s.cookies.items():
        print k,"====",v
    with open("../tmp/result3.html","w") as f:
        f.write(res.content)
        
    url = "http://ehire.51job.com/Candidate/SearchResumeIndex.aspx"
    res = s.get(url,headers=hd)
    print "\n\ncookies4:"
    for k,v in s.cookies.items():
        print k,"====",v
    with open("../tmp/result4.html","w") as f:
        f.write(res.content)
        
        
    from template_qiancheng import getSearchIDInfo
    cvID = "307661274"
    soID = getSearchIDInfo(res.content, cvID)        
    url = "http://ehire.51job.com/Candidate/SearchResume.aspx"
    res = s.post(url, headers=hd, data=soID)
    print "\n\ncookies5:"
    for k,v in s.cookies.items():
        print k,"====",v
    with open("../tmp/result5.html","w") as f:
        f.write(res.content)
        
    
    selector = etree.HTML(res.content)
    lines = selector.xpath('//tr/td/p/span/a[@target="_blank"]/@href')
    url = "http://ehire.51job.com"+lines[0]
    res = s.get(url,headers=hd)
    print "\n\ncookies6:"
    for k,v in s.cookies.items():
        print k,"====",v
    with open("../tmp/result6.html","w") as f:
        f.write(res.content)
    
    from template_qiancheng import getCVKey
    cvKey = getCVKey(res.content)
    res = s.post(url, headers=hd, data=cvKey)
    print "\n\ncookies7:"
    for k,v in s.cookies.items():
        print k,"====",v
    with open("../tmp/result7.html","w") as f:
        f.write(res.content)

#test()
urllib_test()

