import requests
import time

Data = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Connection": "keep-alive",
    "Cookie": "JSESSIONID=kH11WBXQJ1V34ZHmCqJlwJbPjlhGQgFzZqrs3s8CDXrT4h1DhH6p!332034534; BIGipServerpool_xy3_web=1075161280.17183.0000; CNZZDATA1257386840=1579075426-1455542385-%7C1455542385",
    "Host": "passport.liepin.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0"
}

Target = "https://passport.liepin.com/captcha/randomcode/?0.36194390487117667"
s = requests.session()
for i in range(1, 1001):
    r1 = s.post(Target, headers=Data)
    f = open("img_189.cn/%04d.jpg" % (i), "wb")
    f.write(r1.content)
    f.close()
    if i % 100 == 0:
        print "get images:", i
    time.sleep(0.01)
