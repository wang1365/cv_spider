# -*- coding: UTF-8 -*-
'''
Created on 2016年3月31日

@author: leftstone
'''

import requests

from lxml import etree
import random
import time
import json
import threading
import chardet
from string import strip

try:
    import cPickle as pickle
except:
    import pickle
import os
from logger import FetchLogger
from checkcode.main_51job import get_result
from template_qiancheng import getQianChengRelease, getCityCode
from config import get_qiancheng_configs
from template_qiancheng import getSearchKeyInfo
from template_qiancheng import getSearchIDInfo
from template_qiancheng import getCVKey
from urllib import quote
from urllib import unquote
import re

clients_qiancheng = {}
sep = "\n\n"


def process_qiancheng(query, payload):
    str_res = "0" + sep + "not supported"
    ctmName = query["ctmName"]
    user = query["user"]
    passwd = query["passwd"]
    key = ctmName + user + passwd
    print query
    #     for k,v in payload.items():
    #         print k,v.decode("utf-8")
    #     return str_res


    if clients_qiancheng.has_key(key):
        client = clients_qiancheng[key]
        if not client._check_login():
            client.login(ctmName, user, passwd)
        user = user.decode("utf-8")
        op_type = query["op_type"]
        if "login" == op_type:
            str_res = "1" + sep + "user:%s has login successful" % (user)
        elif "logout" == op_type:
            str_res = client.loginout()
            clients_qiancheng.pop(key)
        elif op_type == "release_job":
            if len(payload) == 0:
                str_res = "0" + sep + "user:%s release_job no payload" % (user)
            else:
                str_res = client.release(job_info=payload)
        elif op_type == "update_job":
            if len(payload) == 0:
                str_res = "0" + sep + "user:%s update_job no payload" % (user)
            else:
                str_res = client.update(job_info=payload)

        elif op_type == "pause_job":
            if len(payload) == 0 or (not payload.has_key("e_jobs")):
                str_res = "0" + sep + "user:%s pause_job no payload" % (user)
            else:
                str_res = client.stop_jobs(payload["e_jobs"])
        elif op_type == "reflesh_job":
            if len(payload) == 0 or (not payload.has_key("e_jobs")):
                str_res = "0" + sep + "user:%s reflesh_job no payload" % (user)
            else:
                str_res = client.reflesh_jobs(payload["e_jobs"])
        elif op_type == "check_new_cv":
            if len(payload) == 0 or (not payload.has_key("e_job_id")):
                str_res = "0" + sep + "user:%s check_new_cv no payload" % (user)
            else:
                str_res = client.check_new_cv(payload["e_job_id"])
        elif op_type == "set_search_cv":
            if len(payload) == 0:
                str_res = "0" + sep + "user:%s set_search_cv no payload" % (user)
            else:
                str_res = client.search_cv(payload)
        elif op_type == "getCVContacts":
            str_res = client.getCVContacts(payload["e_cv_id"])
        else:
            str_res = "0" + sep + "not supported op_type:%s" % (op_type)

    else:
        if query["op_type"] != "login":
            str_res = "0" + sep + "you have not login yet"
        else:
            client = CQianCheng()
            res = client.login(ctmName, user, passwd)
            if res[0] == "1":
                clients_qiancheng[key] = client
            str_res = res

    return str_res


class CQianCheng():
    def __init__(self):
        self.usr_agents = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0",
            "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C; .NET4.0E; InfoPath.3)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36 TheWorld 6"]
        self.log = FetchLogger().getLogger()
        self.hd = {
            "Host": "ehirelogin.51job.com",
            "User-Agent": self._getRandAgent(),
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection": "keep-alive",
            "CacheControl": "max-age=0",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        self.cf = get_qiancheng_configs()
        self.cv_path = self.cf["qiancheng_cv_path"]
        if not os.path.exists(self.cv_path):
            os.mkdir(self.cv_path)
        self.scraw_time_sp = 1.0
        try:
            self.scraw_time_sp = float(self.cf["scraw_time_sp"])
        except:
            pass

        self.cv_db = {}
        self.cv_list = []
        self.cv_db_file = self.cf["qiancheng_cv_db_file"]
        try:
            with open(self.cv_db_file, "rb") as f:
                (self.cv_db, self.jobInfo) = pickle.load(f)
                for cv, val in self.cv_db.items():
                    if not os.path.exists(self.cv_path + "/" + val):
                        self.cv_db.pop(cv)
        except:
            self.cv_db = {}
            self.jobInfo = {}

        self.cv_db_mutex = threading.Lock()
        self.cv_list_mutex = threading.Lock()

        self.currDownNum = 0
        self.downClock = [int(c.split(":")[0]) for c in self.cf["scraw_time_range_clock"].split(",")]
        print "self.downClock", self.downClock
        self.scraw_thread = threading.Thread(target=self._down_load_cv)
        self.scraw_thread.start()
        self.session = None
        self.pre_reflesh_time = 0
        maxNumRange = [int(i) for i in self.cf["scraw_max_num_per_day"].split(",")]
        self.maxCvNumPerDay = random.randint(maxNumRange[0], maxNumRange[1])
        self.log.fatal("self.maxCvNumPerDay:%s" % (self.maxCvNumPerDay))

    def _getRandAgent(self):
        return self.usr_agents[random.randint(0, len(self.usr_agents) - 1)]

    def _getCheckCode(self):
        # url="https://passport.liepin.com/captcha/randomcode/?0.36194390487117667"
        url = "http://ehire.51job.com/CommonPage/RandomNumber.aspx?type=login&r=%274583fce7-ae0f-40c5-a107-3e3b5e4f1574%27"
        r1 = self.session.post(url)
        fn = "../tmp/1.jpg"
        f = open(fn, "wb")
        f.write(r1.content)
        f.close()
        res = get_result(fn)
        return res

    def login(self, ctmName="安能聚业", userName="上海安能聚创供应链", password="aneqc888"):
        url = "https://ehirelogin.51job.com/Member/UserLogin.aspx"
        self.session = requests.session()
        agent_ip = "101.200.165.93:80"
        # agent_ip ="111.56.32.72:80"
        agent_ip = "202.100.167.137:80"
        # agent_ip = "111.161.126.106:80"
        proxies = {
            "http": agent_ip,
            "https": agent_ip,
        }
        self.session.proxies = proxies
        res = self.session.get(url)

        self.usr = ctmName + "'s" + userName
        print self.usr
        selector = etree.HTML(res.content)
        check_code_err_cnt = 0
        while 1:
            hidLangType = selector.xpath('//input[@name="hidLangType"]/@value')[0]
            hidAccessKey = selector.xpath('//input[@name="hidAccessKey"]/@value')[0]
            hidEhireGuid = selector.xpath('//input[@name="hidEhireGuid"]/@value')[0]
            fksc = selector.xpath('//input[@name="fksc"]/@value')[0]
            txtPasswordCN = selector.xpath('//input[@name="txtPasswordCN"]')
            checkCode = ""
            if len(txtPasswordCN) != 0:
                '''需要输入验证码'''
                checkCode = self._getCheckCode()
            loginload = {
                "ctmName": quote(ctmName),
                "userName": quote(userName),
                "password": password,
                "checkCode": checkCode,
                "oldAccessKey": hidAccessKey,
                "langtype": hidLangType,
                "isRememberMe": "false",
                "sc": fksc,
                "ec": hidEhireGuid,
                "returl": ""}

            self.hd["Origin"] = "http://ehire.51job.com"
            self.hd["Referer"] = "http://ehire.51job.com/MainLogin.aspx"
            self.hd["Upgrade-Insecure-Requests"] = "1"
            res = self.session.post(url, data=loginload, headers=self.hd)
            with open("../tmp/result1.html", "w") as f:
                f.write(res.content)
            selector = etree.HTML(res.content)
            try:
                '''"<span id="lblErrorCN" style="color:Red;">验证码输入错误</span>"'''
                '''"<span id="lblErrorCN" style="color:Red;">会员名、用户名或密码不准确</span>"'''
                lbl = selector.xpath('//span[@id="lblErrorCN"]')
                if len(lbl) == 0:
                    break
                print lbl
                if u'会员名、用户名或密码不准确' == lbl[0].text:
                    res_str = "0\n\n user name and passwd do not match!!."
                    self.log.fatal(res_str)
                    return res_str
                check_code_err_cnt += 1
                self.log.fatal("check code error:%s error_cnt:%d" % (checkCode, check_code_err_cnt))
                if check_code_err_cnt % 3 == 0:
                    time.sleep(3)
            except:
                break
        try:
            __VIEWSTATE = selector.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
            postBackArg = selector.xpath('//a')[0].get("href")
            p = re.compile(r'\'.*\'')
            args = p.findall(postBackArg)
            args = args[0].split(",")
            __EVENTTARGET = args[0][1:-1]
            __EVENTARGUMENT = args[1][1:-1]
            offlineData = {"__VIEWSTATE": __VIEWSTATE, "__EVENTTARGET": __EVENTTARGET,
                           "__EVENTARGUMENT": __EVENTARGUMENT}
            qury_str = selector.xpath('//form[@method="post"]/@action')[0].split("?")[1]
            url = "http://ehire.51job.com/Member/UserOffline.aspx?" + qury_str

            try:
                lastinfo = selector.xpath('//table/tr/td[@width="20%"]')
                lasttime = lastinfo[2].text
                other_ip = lastinfo[3].text
            except:
                lasttime = ""
                other_ip = ""
            print "post, url:", url
            res = self.session.post(url, data=offlineData, headers=self.hd)
            self.log.fatal("lasttime:%s,other_ip:%s" % (lasttime, other_ip))

        except Exception, e:
            self.log.fatal(str(e))
            self.log.fatal("no need offline other users")

        res_str = "1\n\n user:%s login sucessfully." % (self.usr.decode("utf-8"))
        self.log.fatal(res_str)

        try:
            res = self.session.get("http://js.51jobcdn.com/ehire2007/js/20160504/DictTable.js", headers=self.hd)
            conts = re.findall(re.compile('''var ctJobareaAss(.*?);'''), res.content)[0]
            with open("../tmp/DictTable.js", "w") as f:
                f.write(conts)
        except:
            self.log.fatal("down and kvsparse DictTable.js")

        # If cookies includes multiple domains, merge them to single domain
        cook = self.session.cookies
        domains = cook.list_domains()
        if len(domains) > 1:
            print '==> Multiple domains, merge to one domain: {}'.format(domains)
            kvs = requests.utils.dict_from_cookiejar(cook)
            for k, v in kvs.items():
                cook.set(k, v, domain=domains[0])
        return res_str

    def loginout(self):
        url = "http://ehire.51job.com/LoginOut.aspx"
        res = self.session.get(url)
        with open("../tmp/result11.html", "w") as f:
            f.write(res.content)
        res_str = "1\n\n user:%s loginout sucessfully." % (self.usr.decode("utf-8"))
        self.log.fatal(res_str)
        return res_str

    def release(self, job_info=None):
        if not job_info:
            return "0\n\n job info is null."

        url = "http://ehire.51job.com/Jobs/JobEdit.aspx?Mark=New"
        hd = self.hd
        res = self.session.get(url, headers=hd)
        with open("../tmp/result6.html", "w") as f:
            f.write(res.content)

        url = "http://ehire.51job.com/ajax/Systems/GlobalCompanyAjax.aspx"
        payload = {
            'dotype': 'saveworkaddress',
            'id': '',
            'areacode': getCityCode(job_info['hidWorkarea']),
            'city': job_info['hidWorkarea'],
            'address': job_info['hidAddress'].decode("utf-8"),
            'landmark': '',
            'saverecord': '0',
        }
        hd = self.hd
        hd["X-Requested-With"] = "XMLHttpRequest"
        hidWorkareaId = self.session.post(url, data=payload, headers=hd).content
        print "hidWorkareaId", hidWorkareaId
        hidWorkareaId = re.findall("CDATA\[(.*?)\]", hidWorkareaId)[1]
        print "hidWorkareaId", hidWorkareaId

        url = "http://ehire.51job.com/Jobs/JobEdit.aspx?Mark=New&AjaxPost=True"
        jobInfo = getQianChengRelease(res.content, job_info=job_info)
        if isinstance(jobInfo, str):
            self.log.fatal(jobInfo)
            return "0\n\n" + jobInfo

        jobInfo["hidWorkareaId"] = hidWorkareaId
        res = self.session.post(url, data=jobInfo, headers=self.hd)
        with open("../tmp/result7.html", "w") as f:
            f.write(res.content)
        cons = res.content.split("|")
        cons_len = len(cons)
        self.log.fatal("len(cons):%d" % (cons_len))
        res_str = ""
        if cons_len != 9:
            selector = etree.HTML('<?xml version="1.0"?>\n' + res.content)
            try:
                msg = selector.xpath('//table/tr/td/span[@id="WCMsg1_lblMsg"]')[0].text
                self.log.fatal("WCMsg1_lblMsg:%s" % msg)
            except:
                msg = "release failed."
            res_str = "0\n\n" + msg
        else:
            redirectUrl = "http://ehire.51job.com" + unquote(cons[-2])
            self.log.fatal("redirectUrl:%s" % redirectUrl)
            res = self.session.get(redirectUrl, headers=self.hd)
            with open("../tmp/result8.html", "w") as f:
                f.write(res.content)
            selector = etree.HTML(res.content)
            jobid = selector.xpath('//table/tr/td/table/tr/td/div[@value2="0"]/@value1')[0]

            res_str = "1\n\n" + jobid
            self.log.fatal("usr:%s,release successful,jobid:%s" % (self.usr.decode("utf-8"), jobid))

        skey = {"txtJobName": job_info["CJOBNAME"],
                "KEYWORD": job_info["TxtJobKeywords"],
                }
        self.search_cv(skey)
        return res_str

    def update(self, job_info):
        u"""job_info = {
        'jobid':"76507923",        
        'JOBNUM':"4",
        'JobAreaSelectValue':"040000",
        'DEGREEFROM':"",
        'txtSelectedJobAreas':"深圳",
        'txtWorkAddress':"深圳市盐田区东海道435号安能物流(义乌华贸城公交站下车即到)",
        'AGEFROM':"",
        'AGETO':"",
        'FuncType1Text':"行政专员/助理",
        'FuncType1Value':"2303",
        'FL1':"",
        'FLevel1':"",
        'WORKYEAR':"",
        'Major1Text':"",
        'Major1Value':"",
        'Term':"0",
        'ProvideSalary':"05",
        'TxtJobKeywords':"",
        'CJOBINFO':'''职位描述123
1、负责宿舍、食堂的管理，包括人员住宿、就餐和退宿手续的办理，分拨行政费用的统计与提交，水电故障的报修；
2、对各职能部门办公用品申购单审核并统一采购发放；
3、管理公司固定资产和备用钥匙（电脑、桌子、板凳、投影仪、复印机、传真机等办公设备），并在出现故障时及时报修；
4、日常费用的报销；
5、管理办公区清洁卫生，环境绿化；
6、对公司成本进行监控且进行成本分析；
7、公司证照及资质证件的申报办理与年审；
8、领导交待的其他工作。
职位要求
1、专科学历及以上，人力资源、行政管理等相关专业优先考虑；
2、熟练使用办公软件；
3、具备强烈的责任感，事业心，优秀的沟通能力，抗压能力强；
面试、上班地点：深圳市盐田区义乌华贸城对面安能物流
路线：任一地点乘坐公交车至盐田区“义乌华贸城”公交站，下车即可看到我公司仓库；盐田区东海道435号安能物流
招聘负责人：吴先生 17090205206 (亦可加微信咨询)
简历接收邮箱：wuzhizheng@ane56.com''',
        'JOBORDER':"999",
        }
        """
        if not isinstance(job_info, dict):
            self.log.fatal(
                "usr:%s,update failed ,job_info(%s) is not dict." % (self.usr.decode("utf-8"), type(job_info)))
            return "0\n\n update:job_info is not dict ."

        if not job_info.has_key("jobid"):
            self.log.fatal("usr:%s,update failed ,no jobid ." % (self.usr.decode("utf-8")))
            return "0\n\n update:no jobid ."

        jobid = job_info["jobid"]
        url_prefix = "http://ehire.51job.com/Jobs/JobEdit.aspx?Mark=Edit&Relation=N&Flag=1&isProvidesalary=undefined&JobId="

        get_url = url_prefix + jobid
        res = self.session.get(get_url, headers=self.hd)
        selector = etree.HTML(res.content)
        lblError = selector.xpath('//table/tr/td/span[@id="Error_lblErrorMsg"]')
        if len(lblError) != 0:
            self.log.fatal("usr:%s,update failed,jobid:%s is not found." % (self.usr.decode("utf-8"), jobid))
            return "0\n\njobid:%d is not found." % (jobid)

        jobInfo = getQianChengRelease(res.content, job_info=job_info, update=True)
        post_url = get_url + "&AjaxPost=True"
        res = self.session.post(post_url, headers=self.hd, data=jobInfo)
        if res.status_code != 200:
            self.log.fatal("usr:%s,update failed no reponse,jobid:%s" % (self.usr.decode("utf-8"), jobid))
            return "0\n\n update no responce."

        self.log.fatal("usr:%s,update successful,jobid:%s" % (self.usr.decode("utf-8"), jobid))
        return "1\n\n%s" % (jobid)

    def stop_job(self, jobid):
        # jobid = "70326540"
        url_prefix = "http://ehire.51job.com/Jobs/JobEdit.aspx?Mark=Edit&Relation=N&Flag=1&isProvidesalary=undefined&JobId="
        get_url = url_prefix + jobid
        res = self.session.get(get_url, headers=self.hd)
        selector = etree.HTML(res.content)
        lblError = selector.xpath('//table/tr/td/span[@id="Error_lblErrorMsg"]')
        if len(lblError) != 0:
            self.log.fatal("usr:%s,stop_job failed,jobid:%s is not found." % (self.usr.decode("utf-8"), jobid))
            return "0\n\njobid:%d is not found." % (jobid)

        post_url = get_url + "&AjaxPost=True"
        payload = {}
        payload["__ASYNCPOST"] = "true"
        payload["btnPause"] = "暂停"
        payload["jobId"] = jobid
        payload["strMarkValue"] = "Edit"
        payload["ScriptManager1"] = "ScriptManager1|btnPause"

        payload["__VIEWSTATE"] = selector.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
        res = self.session.post(post_url, headers=self.hd, data=payload)
        if res.status_code != 200:
            self.log.fatal("usr:%s,stop_job failed no reponse,jobid:%s" % (self.usr.decode("utf-8"), jobid))
            return "0\n\n stop_job no responce."

        self.log.fatal("usr:%s,stop_job successful,jobid:%s" % (self.usr.decode("utf-8"), jobid))
        return "1\n\nstop_job successful jobid:%s" % (jobid)

    def reflesh(self, jobid):
        # jobid = "70326540"
        url_prefix = "http://ehire.51job.com/Jobs/JobEdit.aspx?Mark=Edit&Relation=N&Flag=1&isProvidesalary=undefined&JobId="
        get_url = url_prefix + jobid
        res = self.session.get(get_url, headers=self.hd)
        selector = etree.HTML(res.content)
        lblError = selector.xpath('//table/tr/td/span[@id="Error_lblErrorMsg"]')
        if len(lblError) != 0:
            self.log.fatal("usr:%s,reflesh failed,jobid:%s is not found." % (self.usr.decode("utf-8"), jobid))
            return "0\n\njobid:%d is not found." % (jobid)

        post_url = get_url + "&AjaxPost=True"
        payload = {}
        payload["__ASYNCPOST"] = "true"
        payload["btnRefresh"] = "刷新"
        payload["jobId"] = jobid
        payload["strMarkValue"] = "Edit"
        payload["ScriptManager1"] = "ScriptManager1|btnRefresh"

        payload["__VIEWSTATE"] = selector.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
        res = self.session.post(post_url, headers=self.hd, data=payload)
        if res.status_code != 200:
            self.log.fatal("usr:%s,reflesh failed no reponse,jobid:%s" % (self.usr.decode("utf-8"), jobid))
            return "0\n\n reflesh no responce."

        self.log.fatal("usr:%s,reflesh successful,jobid:%s" % (self.usr.decode("utf-8"), jobid))
        return "1\n\nreflesh successful jobid:%s" % (jobid)

    def reflesh_jobs(self, e_jobs):
        jobs = e_jobs.split(",")
        for job in jobs:
            self.reflesh(job)
        self.log.fatal("usr:%s,reflesh successful,jobid:%s" % (self.usr.decode("utf-8"), jobs))
        return "1\n\nreflesh_jobs successful jobid:%s" % (str(jobs))

    def stop_jobs(self, e_jobs):
        jobs = e_jobs.split(",")
        for job in jobs:
            self.stop_job(job)
        self.log.fatal("usr:%s,stop_jobs successful,jobid:%s" % (self.usr.decode("utf-8"), jobs))
        return "1\n\nstop_jobs successful jobid:%s" % (str(jobs))

    def _save_cv(self, cv_info):
        cv_id = cv_info.split("&")[0].split("=")[1] if cv_info.startswith("/") else cv_info

        strtime = time.strftime("%Y%m%d%H")
        cv_path = self.cv_path + os.sep + strtime
        if not os.path.exists(cv_path):
            os.mkdir(cv_path)

        url = "http://ehire.51job.com/Candidate/ResumeViewFolder.aspx?hidFolder=EMP&hidFilter=0&hidSeqID="
        url = "http://ehire.51job.com" + cv_info if cv_info.startswith("/") else url + cv_id
        print url
        rs = self.session.get(url, headers=self.hd)
        content = rs.content

        lines = content.split("\r\n")
        dst_line = []
        if cv_info.startswith("/"):
            selector = etree.HTML(content)
            td_texts = [tr.text for tr in selector.xpath('//tr/td[@width="277"]')]
            if u"此人简历保密" in td_texts:
                return
            pass_flag = False
            start_str = "--></script>"
            end_str = '''<table id="resumeRecommend'''
            for _, l in enumerate(lines):
                lr = l.lstrip()
                if pass_flag == False:
                    if l.startswith('<style type="text/css">'):
                        pass_flag = True
                        continue
                    elif lr[:len(end_str)] == end_str:
                        break
                    else:
                        dst_line.append(l)

                if pass_flag == True:
                    if lr.startswith(start_str):
                        dst_line.append(l[len(start_str):])
                        pass_flag = False
                    else:
                        continue

        else:
            pass_flag = False
            start_str = "\t\t  --></script>"
            end_str = '''\t\t\t    <table border="0" cellpadding="0" align="center" cellspacing="0" width="650" id="divButtons">'''
            for _, l in enumerate(lines):
                if pass_flag == False:
                    if l.startswith("</title>"):
                        dst_line.append(
                            """</title><meta http-equiv="Content-Type" content="text/html; charset=utf-8" />""")
                        pass_flag = True
                    elif l == end_str:
                        break
                    else:
                        dst_line.append(l)

                if pass_flag == True:
                    if l.startswith(start_str):
                        dst_line.append(l[len(start_str):])
                        pass_flag = False
                    else:
                        continue
        new_content = "\r\n".join(dst_line)

        fn = cv_path + os.sep + cv_id + ".html"
        with open(fn, "w") as f:
            f.write(new_content)

        fn_id = strtime + "/" + cv_id + ".html"
        if self.cv_db_mutex.acquire(1):
            self.cv_db[cv_id] = fn_id
            self.cv_db_mutex.release()
        info_str = "usr:%s download cv_id:%s save to %s sucessful." % (self.usr, cv_id, fn)
        self.log.fatal(info_str)
        return fn_id

    def check_new_cv(self, jobid):
        url = "http://ehire.51job.com/Inbox/InboxViewEngine.aspx?bigCode=tp&code=0202&linkType=readResume&strIsHis=Y&JobID="
        get_url = url + jobid
        res = self.session.get(get_url, headers=self.hd)
        selector = etree.HTML(res.content)
        cvid_cons = selector.xpath('//input[@name="hidEngineCvlogIds"]/@value')
        if len(cvid_cons) == 0:
            return "1\n\nthere is no new cvs."

        u'''"7770733681|0|1,7770403832|0|2,7770252727|0|3"'''
        cv_ids = [s.split("|")[0] for s in cvid_cons[0].split(",")]
        res = [self._save_cv(cv_id) for cv_id in cv_ids]
        return "1\n\n" + str(res)

    def _down_load_cv(self):
        self.no_cv_down = 1;
        while 1:
            if self.cf["reflesh_job_time"] == time.strftime("%H:%M"):
                if self.pre_reflesh_time == 0 or int(time.time() - self.pre_reflesh_time) > 86400:
                    self.reflesh_jobs()
                    self.pre_reflesh_time = int(time.time())
                    maxNumRange = [int(i) for i in self.cf["scraw_max_num_per_day"].split(",")]
                    self.maxCvNumPerDay = random.randint(maxNumRange[0], maxNumRange[1])
                    self.currDownNum = 0
                    self.log.fatal("self.maxCvNumPerDay:%s" % (self.maxCvNumPerDay))

            currClock = int(time.strftime("%H"))
            if (currClock < self.downClock[0] and currClock > self.downClock[1]):
                time.sleep(100)
                continue

            cv = None
            if self.cv_list_mutex.acquire(1):
                if len(self.cv_list) != 0:
                    try:
                        cv = self.cv_list.pop(0)
                    except:
                        pass
                self.cv_list_mutex.release()
            if cv == None:
                self._pickle_cv_id()
                # self._down_named_cv()
                time.sleep(10)
                print "no cv to down:%d time:%s" % (self.no_cv_down, time.strftime("%Y-%m-%d %H:%M:%S"))
                self.no_cv_down += 1
                continue

            self.currDownNum += 1
            if self.currDownNum > self.maxCvNumPerDay:
                continue

            self._save_cv(cv)
            if (len(self.cv_db) + 1) % 100 == 0:
                self._pickle_cv_id()

            scrawRange = [int(i) for i in self.cf["scraw_time_range"].split(",")]
            randTime = random.randint(scrawRange[0], scrawRange[1])
            time.sleep(randTime)

    def _pickle_cv_id(self):
        if self.cv_db_mutex.acquire(1):
            db_bak = [{}, {}]
            try:
                with open(self.cv_db_file, "rb") as f:
                    db_bak = pickle.load(f)
            except:
                pass
            if len(db_bak[0]) != len(self.cv_db_file) or len(db_bak[1]) != len(self.jobInfo):
                with open(self.cv_db_file, "wb") as f:
                    pickle.dump((self.cv_db, self.jobInfo), f, protocol=2)
            self.cv_db_mutex.release()

    def search_cv(self, sokey=None):
        t = threading.Thread(target=self._collect_cv_info, args=(sokey,))
        t.start()
        return "1\n\nsearch started."

    def _collect_cv_info(self, sokey=None):
        get_url = "http://ehire.51job.com/Candidate/SearchResumeIndex.aspx"
        post_url = get_url + "?AjaxPost=True"
        res = self.session.get(get_url, headers=self.hd)
        with open("../tmp/result8.html", "w") as f:
            f.write(res.content)
        default_so_key = getSearchKeyInfo(res.content, sokey)

        res = self.session.post(post_url, headers=self.hd, data=default_so_key)
        with open("../tmp/result9.html", "w") as f:
            f.write(res.content)

        content = '''<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />''' + res.content
        selector = etree.HTML(content)
        url = "http://ehire.51job.com/Candidate/SearchResume.aspx"
        default_so_key["hidWhere"] = selector.xpath('//input[@name="hidWhere"]/@value')[0]
        default_so_key["hidValue"] = selector.xpath('//input[@name="hidValue"]/@value')[0]
        default_so_key["hidSearchID"] = selector.xpath('//input[@name="hidSearchID"]/@value')[0]
        default_so_key["__VIEWSTATE"] = re.findall(re.compile("__VIEWSTATE\|(.*?)\|"), res.content.split("\n")[-1])[0]

        default_so_key.pop("ScriptManager1")
        default_so_key.pop("AREA$Text")
        default_so_key.pop("__ASYNCPOST")

        #         for k,v in default_so_key.iteritems():
        #             print k,v
        res = self.session.post(url, headers=self.hd, data=default_so_key)
        with open("../tmp/result10.html", "w") as f:
            f.write(res.content)

        selector = etree.HTML(res.content)
        lines = selector.xpath('//tr/td/p/span/a[@target="_blank"]/@href')
        for line in lines:
            if self.cv_list_mutex.acquire(1):
                self.cv_list.append(line)
                self.cv_list_mutex.release()

    def _check_login(self):
        url = "http://ehire.51job.com/Jobs/JobEdit.aspx?Mark=New"
        hd = self.hd
        res = self.session.get(url, headers=hd)
        with open("../tmp/result10.html", "w") as f:
            f.write(res.content)
        u'<img src="http://img01.51jobcdn.com/imehire/ehire2007/default/image/navi/registe.gif" class="register" alt="" />'
        selector = etree.HTML(res.content)
        register_img_src = selector.xpath('//img[@class="register"]/@src')
        return True if len(register_img_src) == 0 else False

    def getCVContacts(self, cvID):
        cvID = "85798642"  # 不公开
        cvID = "307661274"
        #         cvID = "6098724"
        #         cvID = "318657201"
        from splinter import Browser
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
        selector = etree.HTML(browser.html)
        cvDownableNum = selector.xpath('//span[@id ="Navigate_AvalidResumes"]/a/b')[0].text
        if cvDownableNum == "0":
            self.log.fatal("id:%s can not be down, as to cvDownableNum == 0." % (cvID))
            browser.quit()
            return "0\n\ncvDownableNum is 0."

        browser.find_by_id('hlResumeSearch').click()
        browser.find_by_id('txtUserID').fill(cvID)
        time.sleep(1)
        browser.find_by_id('btnSearchID_leftbtnSearchID').click()

        cvTarget = browser.find_by_xpath('//tr/td/p/span/a[@target="_blank"]')
        if len(cvTarget) == 0:
            self.log.fatal("can not find the cv from this id:%s." % (cvID))
            browser.quit()
            return "0\n\ncan not find the cv from this id."
        cvTarget.click()
        allwindows = browser.windows
        browser.driver.switch_to_window(allwindows[-1].name)
        UndownloadLink = browser.find_by_id('UndownloadLink')
        if len(UndownloadLink) != 0:
            UndownloadLink.click()
            time.sleep(1)
            browser.find_by_id('btnCommonOK').click()
        selector = etree.HTML(browser.html)
        contents = browser.html.encode("utf-8")
        winNum = len(allwindows)
        for i in range(winNum):
            allwindows[winNum - 1 - i].close()
        browser.quit()
        lines = selector.xpath('//title')
        name = ""
        if len(lines) != 0:
            name = strip(lines[0].text)
        try:
            phone = \
            re.findall(re.compile('''<td height="20">电　话：</td><td height="20" colspan="3">(.*?)<span'''), contents)[0]
        except:
            phone = "not supplied"

        try:
            eMail = \
            re.findall(re.compile('''E-mail：</td><td height="20" colspan="3"><a href="mailto:(.*?)" class="blue">'''),
                       contents)[0]
        except:
            eMail = "not supplied"

        if not isinstance(name, unicode):
            name = name.decode("utf-8")
        if not isinstance(phone, unicode):
            phone = phone.decode("utf-8")

        result = "1\n\nname:%s\tphone:%s\teMail:%s" % (name, phone, eMail)
        self.log.fatal(result)
        return result

    def get_contacts_by_cv_id(self, cv_id):
        if not id:
            return {
                'ok': False,
                'reason': 'Invalid cv ID:{}'.format(cv_id)
            }

        # cvID = "85798642"#不公开
        # cvID = "307661274"
        def _prepare_search_info(_headers):
            url = "http://ehire.51job.com/Candidate/SearchResumeIndex.aspx"
            res = self.session.get(url, headers=_headers)
            with open("../tmp/result18.html", "w") as f:
                f.write(res.content)
            return res

        def _search_cv(headers, payload):
            url = "http://ehire.51job.com/Candidate/SearchResume.aspx"
            res = self.session.post(url, headers=headers, data=payload)
            with open("../tmp/result19.html", "w") as f:
                f.write(res.content)
            return res

        def _get_cv_href(res):
            lines = etree.HTML(res.content).xpath('//tr/td/p/span/a[@target="_blank"]/@href')
            return lines[0] if lines else None

        def _open_cv_page(_url, headers):
            res = self.session.get(_url, headers=headers)
            with open("../tmp/cv_page.html", "w") as f:
                f.write(res.content)
            return res

        def _find_contacts(_cv_res):
            root = etree.HTML(_cv_res.content)
            lines = root.xpath(u"//*[text()='电　话：']/following::node()[1]/text()")
            phone = lines[0] if lines else None

            lines = root.xpath(u"//*[text()='E-mail：']/following::node()[2]/text()")
            mail = lines[0] if lines else None

            if phone or mail:
                print u'Find contact: phone-{}, mail-{}'.format(phone, mail)
                return (phone, mail)
            return (phone, mail)

        def _is_cv_downloaded(_cv_res):
            return u'点击查看联系方式' not in _cv_res.text

        def _download_cv(_res, _cv_id):
            download_url = r'http://ehire.51job.com/Ajax/Resume/GlobalDownload.aspx'
            data = {
                "doType": "SearchToCompanyHr",
                "userId": _cv_id,
                "strWhere": ""
            }
            headers = {
                "Accept": "application/xml, text/xml, */*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "Connection": "keep-alive",
                # "Content-Length":51,
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "ehire.51job.com",
                "Origin": "http://ehire.51job.com",
                "Referer": _res.url,
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest"
            }

            res = self.session.post(download_url, headers=headers, data=data)
            with open("../tmp/download_result.html", "w") as f:
                f.write(res.content)
            return res

        # 1. Search cv
        res_prepare = _prepare_search_info(self.hd)
        payload = getSearchIDInfo(res_prepare.content, cv_id)
        print "1.Cookies1 ====>", self.session.cookies

        # 2. Post search request
        res_search = _search_cv(self.hd, payload)
        print "2.Cookies1 ====>", self.session.cookies

        # 3. Find cv's href from search response
        cv_href = _get_cv_href(res_search)
        if not cv_href:
            return {
                'ok': False,
                'reason': 'Not find cv'
            }

        # 4. Open cv page
        cv_url = "http://ehire.51job.com" + cv_href
        res_cv_page = _open_cv_page(cv_url, self.hd)
        print "3.Cookies1 ====>", self.session.cookies

        # 5. If cv not download, download it first
        if not _is_cv_downloaded(res_cv_page):
            res_download = _download_cv(res_cv_page, cv_id)
            print "3.1. Cookies1 ====>", self.session.cookies
            res_cv_page = _open_cv_page(cv_url, self.hd)
            print "3.2. Cookies1 ====>", self.session.cookies

        # 5. Get
        phone, mail = _find_contacts(res_cv_page)
        print "4. Cookies1 ====>", self.session.cookies

        return {
            'ok': any((phone, mail)),
            'contacts': {
                'phone': phone,
                'mail': mail
            }
        }


def test_release():
    jobload = {
        'CJOBNAME': "行政专员5",
        'JOBNUM': "5",
        'DEGREEFROM': "",
        'txtSelectedJobAreas': "北京",
        'hidAddress': '建邺区新地中心11',
        'hidWorkarea': '南京',
        'AGEFROM': "",
        'AGETO': "",
        'FuncType1Text': "行政专员/助理",
        'FuncType1Value': "2303",
        'FL1': "",
        'FLevel1': "",
        'WORKYEAR': "",
        'Major1Text': "",
        'Major1Value': "",
        'Term': "0",
        'ProvideSalary': "05",
        'TxtJobKeywords': "",
        'CJOBINFO': '''职位描述22
1、负责宿舍、食堂的管理，包括人员住宿、就餐和退宿手续的办理，分拨行政费用的统计与提交，水电故障的报修；
2、对各职能部门办公用品申购单审核并统一采购发放；
3、管理公司固定资产和备用钥匙（电脑、桌子、板凳、投影仪、复印机、传真机等办公设备），并在出现故障时及时报修；
4、日常费用的报销；
5、管理办公区清洁卫生，环境绿化；
6、对公司成本进行监控且进行成本分析；
7、公司证照及资质证件的申报办理与年审；
8、领导交待的其他工作。
职位要求
1、专科学历及以上，人力资源、行政管理等相关专业优先考虑；
2、熟练使用办公软件；
3、具备强烈的责任感，事业心，优秀的沟通能力，抗压能力强；
面试、上班地点：深圳市盐田区义乌华贸城对面安能物流
路线：任一地点乘坐公交车至盐田区“义乌华贸城”公交站，下车即可看到我公司仓库；盐田区东海道435号安能物流
招聘负责人：吴先生 17090205206 (亦可加微信咨询)
简历接收邮箱：wuzhizheng@ane56.com''',
        'JOBORDER': "999",
    }
    job_info = jobload
    client = CQianCheng()
    res = client.login()
    print res
    res = client.release(job_info)
    print res


if __name__ == "__main__":
    # test_release()
    client = CQianCheng()
    res = client.login()
    #     #res = client.login(ctmName="zhuocheng763",userName="zhuo427",password="abc123")
    #     print res

    client.get_contacts_by_cv_id('326000302')
    res = client.getCVContacts("6098724")
    print res
#     
#     client._check_login()

#     res = client.stop_jobs("66480047,65471652")
#     print res
#     res = client.reflesh_jobs("66480047,65471652")
#     print res

#     res = client.check_new_cv("77147846")
#     print res
#     print res.content

# client.search_cv()
# client._save_cv("/Candidate/ResumeView.aspx?hidUserID=311086226&hidEvents=23&hidKey=d9053d2cd7948c33c7badb1d38301953")
#     client.scraw_thread.join()
#     print res
# client.stop_job(111)
#    client.release(None)
# client.loginout()
# print res
