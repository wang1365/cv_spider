# -*- coding: UTF-8 -*-
'''
Created on 2016年3月20日

@author: leftstone
'''
import requests

from lxml import etree
import random
import time
import json
import threading
from time import sleep

try:
    import cPickle as pickle
except:
    import pickle
import os
import re

from checkcode.main_zhilian import get_result
from template_zhilian import getZhilianRelease
from config import get_zhilian_configs
from template_zhilian import getSearchKeyInfo

from logger import FetchLogger

clients_zhilian = {}
sep = "\n\n"


def process_zhilian(query, payload):
    str_res = "0" + sep + "not supported"
    user = query["user"]
    passwd = query["passwd"]
    key = user + passwd
    print query
    #     for k,v in payload.items():
    #         print k,v.decode("utf-8")
    #     return str_res

    if clients_zhilian.has_key(key):
        client = clients_zhilian[key]
        op_type = query["op_type"]
        if "login" == op_type:
            str_res = "1" + sep + "user:%s has login successful" % (user)
        elif "logout" == op_type:
            client.logout()
            clients_zhilian.pop(key)
            str_res = "1" + sep + "user:%s logout successful" % (user)
        elif op_type == "release_job":
            if len(payload) == 0:
                str_res = "0" + sep + "user:%s release_job no payload" % (user)
            else:
                str_res = client.release(job_info=payload)
        elif op_type == "update_job":
            if len(payload) == 0 or (not payload.has_key("e_job_id")):
                str_res = "0" + sep + "user:%s update_job no payload" % (user)
            else:
                str_res = client.update(jobid=payload["e_job_id"], job_info=payload)
        elif op_type == "pause_job":
            if len(payload) == 0 or (not payload.has_key("e_jobs")):
                str_res = "0" + sep + "user:%s pause_job no payload" % (user)
            else:
                str_res = client.stop_job(payload["e_jobs"])
        elif op_type == "renew_job":
            if len(payload) == 0 or (not payload.has_key("e_jobs")):
                str_res = "0" + sep + "user:%s renew_job no payload" % (user)
            else:
                str_res = client.renew_job(payload["e_jobs"])
        elif op_type == "reflesh_job":
            if len(payload) == 0 or (not payload.has_key("e_job_id")):
                str_res = "0" + sep + "user:%s reflesh_job no payload" % (user)
            else:
                str_res = client.reflesh_jobs(payload["e_job_id"])
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
        elif op_type == "get_zhilian_coins":
            str_res = client.get_zhilian_coins()
        else:
            str_res = "0" + sep + "not supported op_type:%s" % (op_type)

    else:
        if query["op_type"] != "login":
            str_res = "0" + sep + "you have not login yet"
        else:
            client = CZhiLian()
            res = client.login(user, passwd)
            if res[0] == "1":
                clients_zhilian[key] = client
            str_res = res

    return str_res


class CCVInfo():
    def __init__(self, cv_id, cv_url, has_usr=False):
        self.cv_id = cv_id
        self.cv_url = cv_url
        self.has_usr = has_usr


class CZhiLian():
    def __init__(self):
        self.usr_agents = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0",
            "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C; .NET4.0E; InfoPath.3)",
            "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36 TheWorld 6"]
        self.hd = {
            "Host": "",
            "Referer": "https://passport.liepin.com/e/account/",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection": "keep-alive",
            "CacheControl": "max-age=0",
            "Origin": "http://rd2.zhaopin.com",
            "Referer": "http://rd2.zhaopin.com/portal/myrd/regnew.asp?za=2",
            "Upgrade-Insecure-Requests": "1"
        }
        self.log = FetchLogger().getLogger()
        self.cf = get_zhilian_configs()
        self.cv_path = self.cf["zhilian_cv_path"]
        if not os.path.exists(self.cv_path):
            os.mkdir(self.cv_path)
        self.scraw_time_sp = 1.0
        try:
            self.scraw_time_sp = float(self.cf["scraw_time_sp"])
        except:
            pass

        self.cv_db = {}
        self.cv_list = []
        self.cv_db_file = self.cf["zhilian_cv_db_file"]
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
        self.ejobs = None
        maxNumRange = [int(i) for i in self.cf["scraw_max_num_per_day"].split(",")]
        self.maxCvNumPerDay = random.randint(maxNumRange[0], maxNumRange[1])
        self.log.fatal("self.maxCvNumPerDay:%s" % (self.maxCvNumPerDay))

    def _down_load_cv(self):
        self.no_cv_down = 1;
        while 1:
            if self.cf["reflesh_job_time"] == time.strftime("%H:%M"):
                if self.pre_reflesh_time == 0 or int(time.time() - self.pre_reflesh_time) > 86400:
                    self._reflesh_jobs()
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
                self._down_named_cv()
                time.sleep(10)
                print "no cv to down:%d time:%s" % (self.no_cv_down, time.strftime("%Y-%m-%d %H:%M:%S"))
                self.no_cv_down += 1
                continue

            self.currDownNum += 1
            if self.currDownNum > self.maxCvNumPerDay:
                continue
            self._save_sv(cv)
            if (len(self.cv_db) + 1) % 100 == 0:
                self._pickle_cv_id()

            scrawRange = [int(i) for i in self.cf["scraw_time_range"].split(",")]
            randTime = random.randint(scrawRange[0], scrawRange[1])
            time.sleep(randTime)

    def _getCheckCode(self):
        # url="https://passport.liepin.com/captcha/randomcode/?0.36194390487117667"
        url = "https://passport.zhaopin.com/checkcode/imgrd?r=1458439182000"
        r1 = self.session.post(url)
        fn = "../tmp/1.bmp"
        f = open(fn, "wb")
        f.write(r1.content)
        f.close()
        res = get_result(fn)
        return res

    def _getRandAgent(self):
        return self.usr_agents[random.randint(0, len(self.usr_agents) - 1)]

    def login(self, usrname="38288551", passwd="anezl888"):

        self.session = requests.session()
        agent_ip = "101.200.165.93:80"
        # agent_ip ="111.56.32.72:80"
        # agent_ip = "202.100.167.137:80"
        agent_ip = "111.161.126.106:80"
        proxies = {
            "http": agent_ip,
            "https": agent_ip,
        }
        # self.session.proxies = proxies

        url = "https://passport.zhaopin.com/org/login"
        post_data = {"LoginName": usrname, "Password": passwd, "CheckCode": "", "Submit": ""}
        check_code_err_cnt = 0
        self.hd["Host"] = "passport.zhaopin.com"

        self.usr = usrname
        uid = ""
        while 1:
            ck = self._getCheckCode()
            if len(ck) != 4:
                continue
            post_data["CheckCode"] = ck
            self.hd["User-Agent"] = self._getRandAgent()
            res = self.session.post(url, data=post_data, headers=self.hd)
            # <div style="zoom:normal;" class="msg_error">验证码错误！</div>
            selector = etree.HTML(res.content)
            with open("../tmp/result1.html", "w") as f:
                f.write(res.content)
            ck_errs = selector.xpath('//div[@class="msg_error"]')
            if len(ck_errs) == 0:
                p = re.compile(r'window.location.href = (.*);')
                href = re.findall(p, res.content)
                if len(href) == 0:
                    return "0\n\n user:%s login failed, the user need test more." % (self.usr)
                else:
                    ##href=['"http://rd2.zhaopin.com/s/loginmgr/loginproc_new.asp"']
                    res = self.session.get(href[0][1:-1])
                    with open("../tmp/result2.html", "w") as f:
                        f.write(res.content)
                    break
                    # return
            else:
                if ck_errs[0].text == None:
                    print res.url
                    uid = res.url.split("=")[1]
                    # https://passport.zhaopin.com/org/sel
                    selUrl = "https://passport.zhaopin.com/org/sel"
                    selData = {"bkurl": "", "toSys": "0", "uid": uid, "xybackurl": ""}
                    print selData
                    res = self.session.post(selUrl, selData)
                    # url = "http://rd2.zhaopin.com/s/loginmgr/loginpoint.asp?id=38288551&BkUrl=&deplogincount=22"
                    url = "http://rd2.zhaopin.com/s/loginmgr/loginproc_new.asp"
                    res = self.session.get(url)
                    with open("../tmp/result3.html", "w") as f:
                        f.write(res.content)

                    url = "http://rd2.zhaopin.com/s/loginmgr/loginpoint.asp?id=38288551&BkUrl=&deplogincount=22"
                    res = self.session.get(url)
                    with open("../tmp/result4.html", "w") as f:
                        f.write(res.content)
                    break
                if u"用户名或密码错误！" == ck_errs[0].text:
                    return "0\n\n %s." % (ck_errs[0].text)
                if u"验证码错误！" != ck_errs[0].text:
                    return "0\n\n %s." % (ck_errs[0].text)

                check_code_err_cnt += 1
                if check_code_err_cnt % 3 == 0:
                    time.sleep(3)
                print "error checkcode try:%d" % (check_code_err_cnt)

        return "1\n\n user:%s login sucessfully." % (self.usr)

    def logout(self):
        url = "http://rd2.zhaopin.com/s/loginmgr/logout.asp"
        self.session.get(url)
        # res.url == "http://hr.zhaopin.com/hrclub/index.html":
        return "1\n\n logout sucessful."

    def down(self):
        url = "http://rd.zhaopin.com/resumepreview/resume/viewone/1/5339385518?resume=5339385518&star=&companyid=38288551"
        res = self.session.get(url)
        with open("../tmp/resume.html", "w") as f:
            f.write(res.content)

        url = "http://rd.zhaopin.com/resumepreview/resume/viewone/2/JR110190439R90000000000_1_1?searchresume=1"
        res = self.session.get(url)
        with open("../tmp/resume1.html", "w") as f:
            f.write(res.content)

    def _down_named_cv(self):
        pass

    def update(self, jobid="CC382885514J90257237000", job_info=None):
        url = "http://jobads.zhaopin.com/Position/PositionModify/" + jobid
        res = self.session.get(url)
        pload = getZhilianRelease(res.content, job_info, update=True)
        if not isinstance(pload, dict):
            return pload
        pload["PositionNumber"] = jobid

        res = self.session.post(url, data=pload)

        print res.url
        print res.content
        jo = json.loads(res.text)
        print jo["Code"]

        if jo["Code"] == 200:
            jobid = jo["Data"]["JobPositionNumber"]
            res_str = "1\n\n" + jobid
        else:
            res_str = "0\n\n" + jo["Messages"]
        return res_str

    def release(self, job_info):
        jobid = ""
        url = "http://jobads.zhaopin.com/Position/PositionAdd"
        res = self.session.get(url)
        pload = getZhilianRelease(res.content, job_info)
        if not isinstance(pload, dict):
            return pload

        res = self.session.post(url, data=pload)
        jo = json.loads(res.text)
        self.log.fatal(jo)
        # {"Code":200,"Messages":"职位发布成功","Data":{"JobTitle":"人事行政专员3","JobPositionNumber":"CC382885514J90257183000","EditId":192383602,"CityList":[{"ProvinceId":0,"CityId":636,"CityName":null,"CqId":0,"CqName":null,"Coordinates":null}],"DeductCount":1,"JsResult":{"StatusCode":200,"Message":"职位发布成功"}},"Message":"职位发布成功"}

        self._search_related_job(job_info)
        if jo["Code"] == 200:
            jobid = jo["Data"]["JobPositionNumber"]
            res_str = "1\n\n" + jobid
        else:
            res_str = "0\n\n" + jo["Messages"]

        return res_str

    def _search_related_job(self, job_info=None):
        url = "http://rdsearch.zhaopin.com/Home/ResultForPosition?source=rd"
        try:
            job_title = "&SF_1_1_1=" + job_info["JobTitle"]
            job_type = "&SF_1_1_17=" + job_info["JobTypeMain"] + "," + job_info["JobTypeMinor"]
            job_employ_type = "&SF_1_1_19=" + job_info["EmploymentType"]
            pos_place = "&SF_1_1_18=" + job_info["PositionPubPlace"]
            url = url + job_title + job_type + job_employ_type + pos_place
        except:
            return

        # url = "http://rdsearch.zhaopin.com/Home/ResultForPosition?SF_1_1_1=%E4%BA%BA%E4%BA%8B%E8%A1%8C%E6%94%BF%E4%B8%93%E5%91%985&SF_1_1_17=5002000,3010000&SF_1_1_19=2&source=rd&SF_1_1_18=636"
        res = self.session.get(url)
        self._add_search_result(res.content)

    def _add_search_result(self, content, src="release_job"):
        # url = "http://rdsearch.zhaopin.com/Home/ResultForPosition?SF_1_1_1=%E4%BA%BA%E4%BA%8B%E8%A1%8C%E6%94%BF%E4%B8%93%E5%91%985&SF_1_1_17=5002000,3010000&SF_1_1_19=2&source=rd&SF_1_1_18=636"

        selector = etree.HTML(content)
        lines = selector.xpath('//a[@target="_blank"]')
        for line in lines:
            try:
                tag = line.get("tag")
                cv_url = line.get("href")
                if tag == None or cv_url == None:
                    continue
                self.log.fatal("when %s, search related cv:%s,%s" % (src, tag, cv_url))
                if self.cv_list_mutex.acquire(1):
                    self.cv_list.append(CCVInfo(tag, cv_url, False))
                    self.cv_list_mutex.release()
            except:
                pass

    def stop_job(self, jobs=None):
        u'''
        jobs的格式如下：
        jobs = "CC382885514J90257183000,CC382885514J90257182000,CC382885514J90257181000"
        
        返回结果：
         成功：{"flag":"1","msg":"职位暂停成功"}
         识别：{"flag":"0","msg":"部分职位由于今天已经刷新过，没有刷新"}
        '''
        if jobs == None:
            return '{"flag":"0","msg":"部分职位由于今天已经刷新过，没有刷新"}'
        self.log.fatal("usr:%s %s" % (self.usr, jobs))
        url = "http://jobads.zhaopin.com/Position/PositionPause"
        # url = self.cf["stop_url"]
        res = self.session.post(url, data={"positionNumbers": jobs})
        self.log.fatal(res.text)
        self.log.fatal("usr:%s %s" % (self.usr, res.text))
        jo = json.loads(res.text)
        msg = ""
        if jo['Code'] == 200:
            msg = "1\n\n" + jo["Message"]
        else:
            msg = "0\n\n" + jo["Message"]
        return msg

    def renew_job(self, jobs=None):
        u'''
        http://jobads.zhaopin.com/Position/PositionRenew
        jobs = "CC382885514J90257183000,CC382885514J90257182000,CC382885514J90257181000"        
        '''
        if jobs == None:
            return "0\n\n provide jobs is None"
        self.log.fatal("usr:%s renew_job %s" % (self.usr, jobs))
        url = "http://jobads.zhaopin.com/Position/PositionRenew"
        res = self.session.post(url, data={"positionNumbers": jobs})
        self.log.fatal("usr:%s %s" % (self.usr, res.text))
        jo = json.loads(res.text)
        msg = ""
        if jo['Code'] == 200:
            msg = "1\n\n" + jo["Message"]
        else:
            msg = "0\n\n" + jo["Message"]
        return msg

    def _save_sv(self, cv_info):
        if self.cv_db.has_key(cv_info.cv_id):
            return self.cv_db[cv_info.cv_id]
        strtime = time.strftime("%Y%m%d%H")
        cv_path = self.cv_path + os.sep + strtime
        if not os.path.exists(cv_path):
            os.mkdir(cv_path)
        new_content = ""
        if cv_info.has_usr:
            sub_content = self.session.post(cv_info.cv_url).content
            sub_sel = etree.HTML(sub_content)
            ph_no = sub_sel.xpath('//div/div/div/div/div/div/span/em/b')[0].text
            email = sub_sel.xpath('//div/div/div/div/div/div/span/em/i')[0].text
            to_change = '''手机：''' + ph_no + '''<br />E-mail：<a href="mailto:''' + email + '''">''' + email + '''</a>'''
            insert_flag = False
            start = "<!--普通简历显示联系方式-->"
            end = "<!--end橄榄枝-->"
            for line in sub_content.split("\n"):
                line = line.lstrip()
                if line[:len(start)] == start:
                    insert_flag = True
                    continue
                if line[:len(end)] == end:
                    insert_flag = False
                    new_content += to_change
                    continue
                if insert_flag:
                    continue
                new_content += line
        else:
            new_content = self.session.get(cv_info.cv_url).content
        fn = cv_path + os.sep + cv_info.cv_id + ".html"
        with open(fn, "w") as f:
            f.write(new_content)

        fn_id = strtime + "/" + cv_info.cv_id + ".html"
        if self.cv_db_mutex.acquire(1):
            self.cv_db[cv_info.cv_id] = fn_id
            self.cv_db_mutex.release()
        info_str = "usr:%s download cv_id:%s save to %s sucessful." % (self.usr, cv_info.cv_id, fn)
        self.log.fatal(info_str)
        return fn_id

    def _getJobInfo(self, arg_jobId=None):
        if arg_jobId != None:
            if self.jobInfo.has_key(arg_jobId):
                return self.jobInfo[arg_jobId]
        url = "http://jobads.zhaopin.com/Position/PositionManage"
        res = self.session.get(url)
        selector = etree.HTML(res.content)
        rs_sel = selector.xpath('//span/em')
        page_num = 1
        for rs in rs_sel:
            if 0 == len(rs.keys()):
                try:
                    page_num = int(rs.text)
                except:
                    pass
                break
        self.log.fatal("user:%s, jobs' page_num:%d" % (self.usr, page_num))
        curr = 0
        find_flag = False
        while curr < page_num:
            curr += 1
            if curr > 0:
                url = "http://jobads.zhaopin.com/Position/PositionManageStatus"
                payload = {
                    "pageindex": str(curr),
                    "status": "3",
                    "jobpositionType": "0",
                    "orderByType": "1",
                    "orderBy": "2"}
                hd = self.hd
                hd["X-Requested-With"] = "XMLHttpRequest"
                hd["Referer"] = "http://jobads.zhaopin.com/Position/PositionManage"
                hd["Host"] = "jobads.zhaopin.com"
                hd["Origin"] = "http://jobads.zhaopin.com"
                res = self.session.post(url, data=payload, headers=hd)
                selector = etree.HTML(res.content)

            jobTitle = {}
            rs_sel = selector.xpath('//span/font')
            for rs in rs_sel:
                if "id" in rs.keys():
                    jobid = rs.get("id")[9:]
                    jobTitle[jobid] = rs.text
                    if arg_jobId == jobid:
                        find_flag = True
                        break
            for k, v in jobTitle.items():
                if self.jobInfo.has_key(k):
                    continue
                position = "position_" + k
                data_editid = selector.xpath('//input[@id="' + position + '"]/@data-editid')[0]
                self.jobInfo[k] = (v, data_editid)

            if find_flag == True:
                break
            self.log.fatal("user:%s, get jobs info current page:%d" % (self.usr, curr))
            time.sleep(self.scraw_time_sp)
        self._pickle_cv_id()
        if arg_jobId != None:
            return None if find_flag == False else self.jobInfo[arg_jobId]

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

    def check_new_cv(self, job_id="CC382885514J90257162000"):
        # job_id = "CC382885514J90257162000"
        # url = "http://rd2.zhaopin.com/rdapply/resumes/apply/position?SF_1_1_46=0&SF_1_1_44=192942892&JobTitle=%E4%BA%BA%E4%BA%8B%E8%A1%8C%E6%94%BF%E4%B8%93%E5%91%985&JobStatus=3&IsInvited=0&jobNum=CC382885514J90257237000"
        if job_id == None or len(job_id) == 0:
            return "0\n\njobid(%s) is error" % (str(job_id))

        job_info = self._getJobInfo(job_id)
        if job_info == None:
            return "0\n\njobid(%s) is not found" % (str(job_id))

        url = "http://rd2.zhaopin.com/rdapply/resumes/apply/position?SF_1_1_46=0&JobStatus=3&IsInvited=0"
        SF_1_1_44 = "&SF_1_1_44=" + job_info[1]
        JobTitle = "&JobTitle=" + job_info[0]
        jobNum = "&jobNum=" + job_id
        url = url + SF_1_1_44 + JobTitle + jobNum

        res = self.session.post(url)
        selector = etree.HTML(res.content)
        rs_sel = selector.xpath('//td/a[@class="link "]/@href')
        resumebhs = selector.xpath('//input[@data-isfeedback="true"]/@data-resumebh')

        cv_list = []
        for idx, cv_url in enumerate(rs_sel):
            cv_list.append(CCVInfo(cv_id=resumebhs[idx], cv_url=cv_url, has_usr=True))
        cv_info = [self._save_sv(cv) for cv in cv_list]
        self._pickle_cv_id()
        self.log.fatal("usr:%s check_new_cv %s" % (self.usr, cv_info))
        return "1\n\n" + str(cv_info)

    def _collect_cv_info(self, sokey=None):
        # http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_1=%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0&orderBy=DATE_MODIFIED,1&SF_1_1_27=0&exclude=1
        url = "http://rdsearch.zhaopin.com/Home/ResultForCustom"
        #         query = {"SF_1_1_1":u"机器学习",
        #                  "orderBy":"DATE_MODIFIED,1",
        #                  "exclude":"1",
        #                  "SF_1_1_27":"0"}

        query = getSearchKeyInfo(sokey)
        for k, v in query.items():
            self.log.fatal("usr:%s search parameter:%s:%s" % (self.usr, k, v))
        hd = self.hd
        hd["Host"] = "rdsearch.zhaopin.com"
        hd["Upgrade-Insecure-Requests"] = "1"
        hd["Referer"] = "http://rdsearch.zhaopin.com/home/SearchByCustom"

        res = self.session.get(url, params=query, headers=hd)
        # <input id="rd-resumelist-pageCount" type="hidden" value="134" />
        try:
            selector = etree.HTML(res.content)
            pageCount = int(selector.xpath('//input[@id="rd-resumelist-pageCount"]/@value')[0])
            self.log.fatal("usr:%s search cv page count %d" % (self.usr, pageCount))
        except:
            pageCount = 1
        currPage = 0
        while currPage < pageCount:
            if currPage > 0:
                query["pageIndex"] = str(currPage + 1)
                res = self.session.get(url, params=query, headers=hd)
            currPage += 1
            self._add_search_result(res.content, src="search non name cv")
            time.sleep(self.scraw_time_sp)

    def search_cv(self, sokey=None):
        # self._collect_cv_info()
        if not sokey:
            return "0\n\nsearch key is None."

        t = threading.Thread(target=self._collect_cv_info, args=(sokey,))
        t.start()
        return "1\n\nsearch started."

    def get_zhilian_coins(self):
        url = "http://rd2.zhaopin.com/Consume/NestedStandard"
        res = self.session.get(url)
        with open("../tmp/result.html", "w") as f:
            f.write(res.content)

        u'''<i>账户余额：</i><span>131</span>'''

        p = re.compile(r'<i>账户余额：</i><span>(\d+)</span>')
        coins = re.findall(p, res.content)
        if len(coins) == 0:
            return "0\n\ncan not find coin description."
        try:
            nr = int(coins[0])
        except:
            nr = 0
        return "1\n\n" + str(nr)

    def _get_all_jobs(self):
        ejobids = []
        url = "http://jobads.zhaopin.com/Position/PositionManage"
        if not self.session:
            return []
        res = self.session.get(url)
        selector = etree.HTML(res.content)

        try:
            page_num = int(selector.xpath('//input[@name="pageCount"]/@value')[0])
            status = selector.xpath('//input[@name="position_status"]/@value')[0]
        except:
            page_num = 0

        self.log.fatal("page_num:%d" % (page_num))

        more_data = {
            "pageindex": "1",
            "status": status,
            "jobpositionType": "0",
            "orderByType": "1",
            "orderBy": "2",}
        curr = 0
        url = "http://jobads.zhaopin.com/Position/PositionManageStatus"
        hd = {"Host": "jobads.zhaopin.com",
              "Origin": "http://jobads.zhaopin.com",
              "X-Requested-With": "XMLHttpRequest",
              "Referer": "http://jobads.zhaopin.com/Position/PositionManage",}
        while (curr < page_num):
            if curr > 0:
                more_data["pageindex"] = str(curr + 1)
                res = self.session.post(url, data=more_data, headers=hd)
                with open("../tmp/ddd" + str(curr) + ".html", "w") as f:
                    f.write(res.content)
                selector = etree.HTML(res.content)
            curr += 1
            ids = selector.xpath('//span[@class="checkbox"]/@data-value')
            self.log.fatal("get jobids:%s." % (str(ids)))
            ejobids.extend(ids)
            time.sleep(self.scraw_time_sp)
        return ejobids

    def reflesh_jobs(self, ejob_id):
        # ejob_id = "CC382885514J902574350000"
        url = "http://jobads.zhaopin.com/Position/PositionRefDate"
        res = self.session.post(url, data={"positionNumbers": ejob_id})
        u'''{res.content:"Code":200,"Message":"职位刷新成功！","Data":0}
        {"Code":500,"Message":"职位刷新失败！","Data":0}'''
        jo = json.loads(res.content)
        msg = jo["Message"]
        print type(jo["Code"]), jo["Code"]
        res_str = "1\n\n" + msg if jo["Code"] == 200 else "0\n\n" + msg
        self.log.fatal("reflesh_jobs ejob_id:%s msg:%s" % (ejob_id, msg))
        return res_str

    def _reflesh_jobs(self):
        if None == self.ejobs:
            self.ejobs = self._get_all_jobs()
        for job_id in self.ejobs:
            '''
            {
              "Code": 200,
              "Messages": "您选择了1个职位刷新，将使用20个智联币",
              "Data": {
                "PositionCount": 1,
                "FreeRefreshCount": 0,
                "NeedPay": 20.0
              },
              "Message": "您选择了1个职位刷新，将使用20个智联币"
            }
            '''
            url = "http://jobads.zhaopin.com/Position/PositionRefreshCheck"
            res = self.session.post(url, data={"positionNumbers": job_id})
            jo = json.loads(res.content)
            if jo["Code"] == 200:
                if jo["Data"]["FreeRefreshCount"] != 1:
                    continue
                res_str = self.reflesh_jobs(job_id)
                if res_str[0] != "1":
                    continue
                self.log.fatal("auto reflesh jobid:%s successfully" % (job_id))
                time.sleep(1)

    def getCVContacts(self):
        url = "http://rdsearch.zhaopin.com/Home/SearchByCustom?source=rd"
        res = self.session.get(url)
        print res
        with open("../tmp/result0.html", "w") as f:
            f.write(res.content)

        url = "http://rdsearch.zhaopin.com/Home/SearchByResumeId"
        res = self.session.get(url)
        print res
        with open("../tmp/result1.html", "w") as f:
            f.write(res.content)

        for k, v in self.session.cookies.items():
            print k, "==========", v
        hd = {}
        hd[
            "Cookie"] = "pageReferrInSession=http%3A//rd2.zhaopin.com/s/homepage.asp; Home_ResultForCustom_orderBy=DATE_MODIFIED%2C1; LastSearchHistory=%7b%22Id%22%3a%2245685016-c591-49be-b070-683d74092e58%22%2c%22Name%22%3a%22%e6%95%b0%e6%8d%ae%e6%8c%96%e6%8e%98+%2b+%e5%8d%97%e4%ba%ac%22%2c%22SearchUrl%22%3a%22http%3a%2f%2fsou.zhaopin.com%2fjobs%2fsearchresult.ashx%3fjl%3d%25e5%258d%2597%25e4%25ba%25ac%26kw%3d%25e6%2595%25b0%25e6%258d%25ae%25e6%258c%2596%25e6%258e%2598%26p%3d1%26kt%3d3%26isadv%3d0%22%2c%22SaveTime%22%3a%22%5c%2fDate(1461251437572%2b0800)%5c%2f%22%7d; Hm_lvt_38ba284938d5eddca645bb5e02a02006=1459568576,1461251251; __xsptplus30=30.2.1462282409.1462282409.1%231%7Cother%7Ccnt%7C121122523%7C%7C%23%23F8GwS7_dY9e9NSKVsOPEklWgDXqT8oXi%23; Home_ResultForPosition_orderBy=DATE_MODIFIED%2C1; _jzqx=1.1458439742.1462455645.3.jzqsr=hr%2Ezhaopin%2Ecom|jzqct=/hrclub/index%2Ehtml.jzqsr=hr%2Ezhaopin%2Ecom|jzqct=/hrclub/index%2Ehtml; utype=135942673; urlfrom=121113803; urlfrom2=121113803; adfcid=pzzhubiaoti; adfcid2=pzzhubiaoti; adfbid=0; adfbid2=0; dywez=95841923.1462887846.56.34.dywecsr=other|dyweccn=121113803|dywecmd=cnt|dywectr=%E6%99%BA%E8%81%94%E6%8B%9B%E8%81%98; _jzqy=1.1456326206.1462887846.10.jzqsr=sogou|jzqct=%E6%99%BA%E8%81%94%E6%8B%9B%E8%81%98.jzqsr=baidu|jzqct=%E6%99%BA%E8%81%94%E6%8B%9B%E8%81%98; _jzqckmp=1; Home_ResultForResumeId_orderBy=DATE_MODIFIED%2C1; __zpWAM=1458438643798.361986.1462455635.1462888445.8; __zpWAMs1=1; __zpWAMs2=1; __utmt=1; _jzqa=1.2521548100427010600.1456326206.1462455645.1462887846.15; _jzqc=1; _jzqb=1.2.10.1462887846.1; pcc=r=640787608&t=0; JsOrglogin=407828021; xychkcontr=38288551%2c1; lastchannelurl=https%3A//passport.zhaopin.com/org/Sel%3Fuid%3D135942673; JsNewlogin=135942673; cgmark=2; isNewUser=1; RDpUserInfo=; RDsUserInfo=316629614E724564557351664A73536A45655E64516D5273497428663D645B734067527757685C6655614672416457735F662673296A4A65622A1100E8288FF43EE66836FD3CE73994E35E68266629614E7247645E7356664B735F6A42655D64576D5A7330742A664E646C3D040AE32C98E83EE67633E83DE03A98E7C51D75076E0D27F304359E3E5A73267429664E645D7336672777586813661861017201641F7311661673276A16650664036D547344744A66106409731E67517736683066506142724F64277330664E73526A5A655964566D417340745566496453734767517721682066506140724C6454735C664B73526A426559645D6D25733C745966792A111EFA3C97F73FE87F34F62EE72C8AF0C70862127A1437FC1B3490375D6D2D733F7459664364567343675B775E68276629614E72416455735C664873326A23655564576D517343745F66306427734E67297726685766556141724C645E7351664673566A43655364226D20734F742766306455734B6758775D685C6658614672456452735F663773246A4A655A64546D5A7321742D664E64557348672377356859665F6147724664487355664273556A4C6529642A6D5C7342745F666; getMessageCookie=1; SearchHead_Erd=rd; dywea=95841923.2045503370193130200.1439814962.1462455009.1462887846.56; dywec=95841923; dyweb=95841923.48.5.1462888468439; __utma=269921210.502374082.1439814962.1462455009.1462887846.51; __utmb=269921210.35.8.1462888468441; __utmc=269921210; __utmz=269921210.1462887846.51.34.utmcsr=other|utmccn=121113803|utmcmd=cnt; __utmv=269921210.|2=Member=135942673=1"
        url = "http://rdsearch.zhaopin.com/Home/ResultForResumeId?SF_1_1_24=JR368017726R90250000000&SF_1_1_27=0&orderBy=DATE_MODIFIED%2c1&exclude=1"
        url = "http://rdsearch.zhaopin.com/Home/ResultForResumeId?SF_1_1_24=JR170317301R90000000000&orderBy=DATE_MODIFIED,1&SF_1_1_27=0&exclude=1"
        res = self.session.get(url, headers=hd)
        print res
        with open("../tmp/result2.html", "w") as f:
            f.write(res.content)


# url = "http://rdsearch.zhaopin.com/Home/ResultForCustom"
#         query = {"SF_1_1_1":u"机器学习",
#                  "orderBy":"DATE_MODIFIED,1",
#                  "exclude":"1",
#                  "SF_1_1_27":"0"}
# 
#         query = getSearchKeyInfo(query)
#         for k,v in query.items():
#             self.log.fatal("usr:%s search parameter:%s:%s"%(self.usr,k,v))
#         hd = self.hd
#         hd["Host"] = "rdsearch.zhaopin.com"
#         hd["Upgrade-Insecure-Requests"] = "1"
#         hd["Referer"] = "http://rdsearch.zhaopin.com/home/SearchByCustom"
# 
#         res = self.session.get(url, params = query,headers = hd)
#         with open("../tmp/result.html","w") as f:
#             f.write(res.content)

if __name__ == "__main__":
    client = CZhiLian()
    # ret = client.login("anhui-200","2016jianli")
    ret = client.login()
    ret = client.getCVContacts()
    print ret


# res = client._reflesh_jobs()
#     print res
#     
#     client.scraw_thread.join()

#     res = client.renew_job(jobs = "CC382885514J90257183000,CC382885514J90257182000,CC382885514J90257181000")
#     print res
#     res = client.stop_job(jobs = "CC382885514J90257183000,CC382885514J90257182000,CC382885514J90257181000")
#     print res
#     
#     res = client.stop_job(jobs = "CC382885514J90257183001")
#     print res

#     ret = zhilian.update()
#     print ret

#    ret = client.down()
#     ret = zhilian.logout()
#     print ret
