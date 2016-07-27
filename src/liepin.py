# -*- coding: UTF-8 -*-
'''
Created on 2016年3月11日

@author: leftstone
'''
import os
import requests
import time
from lxml import etree
import json
import random
import template
from logger import FetchLogger

try:
    import cPickle as pickle
except:
    import pickle

import threading

from checkcode.main_liepin import get_result
from config import get_configs

clients_liepin = {}
sep = "\n\n"


def process_liepin(query, payload):
    user = query["user"]
    passwd = query["passwd"]
    key = user + passwd
    print query
    str_res = "0" + sep + "not supported"
    if clients_liepin.has_key(key):
        client = clients_liepin[key]
        op_type = query["op_type"]
        if "login" == op_type:
            str_res = "1" + sep + "user:%s has already login successful" % (user)
        elif "logout" == op_type:
            client.logout()
            clients_liepin.pop(key)
            str_res = "1" + sep + "user:%s logout successful" % (user)
        elif op_type == "release_job":
            if len(payload) == 0:
                str_res = "0" + sep + "user:%s release_job no payload" % (user)
            else:
                level = None
                update = None
                if payload.has_key("update_job_id"):
                    update = payload["update_job_id"]
                if payload.has_key("ejob_level") and payload["ejob_level"] == "1":
                    level = 1

                res = client.release(level=level, update=update, job_info=payload)
                try:
                    job_id = int(res)
                    str_res = "1" + sep + str(job_id)
                except:
                    str_res = "0" + sep + res
        elif op_type == "pause_job":
            if len(payload) == 0 or (not payload.has_key("e_jobs")):
                str_res = "0" + sep + "user:%s pause_job no payload" % (user)
            else:
                res = client.stop_job(payload["e_jobs"])
                str_res = res[0] + sep + res[1]
        elif op_type == "reflesh_job":
            if len(payload) == 0 or (not payload.has_key("e_jobs")):
                str_res = "0" + sep + "user:%s reflesh_job no payload" % (user)
            else:
                res = client.reflesh_jobs(payload["e_jobs"])
                str_res = res[0] + sep + res[1]
        elif op_type == "check_new_cv":
            if len(payload) == 0 or (not payload.has_key("e_job_id")):
                str_res = "0" + sep + "user:%s check_new_cv no payload" % (user)
            else:
                res = client.check_new_cv(payload["e_job_id"])
                str_res = "1" + sep + str(res)
        elif op_type == "set_search_cv":
            if len(payload) == 0:
                str_res = "0" + sep + "user:%s set_search_cv no payload" % (user)
            else:
                res = client.search_cv(payload)
                str_res = "1" + sep + str(res)
        else:
            str_res = "0" + sep + "not supported op_type:%s" % (op_type)

    else:
        if query["op_type"] != "login":
            str_res = "0" + sep + "you have not login yet"
        else:
            client = CLiePin()
            res = client.login(user, passwd)
            if res["flag"] == 1:
                clients_liepin[key] = client
                str_res = "1" + sep + "user:%s login successful" % (user)
            else:
                str_res = "0" + sep + "user:%s login failed" % (user)

    return str_res


class CLiePin():
    def __init__(self):
        self.log = FetchLogger().getLogger()
        self.usr_agents = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0",
            "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C; .NET4.0E; InfoPath.3)",
            "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36 TheWorld 6"]

        self.hd = {
            "Host": "",
            "Referer": "https://passport.liepin.com/e/account/",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "CacheControl": "no-cache"
        }
        self.cf = get_configs()
        self.cv_path = self.cf["liepin_cv_path"]
        self.scraw_time_sp = 1.0
        try:
            self.scraw_time_sp = float(self.cf["scraw_time_sp"])
        except:
            pass

        self.cv_db = {}
        self.cv_list = []
        self.cv_db_file = self.cf["liepin_cv_db_file"]
        try:
            with open(self.cv_db_file, "r") as f:
                self.cv_db = pickle.load(f)
        except:
            self.cv_db = {}

        self.downClock = [int(c.split(":")[0]) for c in self.cf["scraw_time_range_clock"].split(",")]
        self.log.fatal("self.downClock:%s" % (str(self.downClock)))

        self.currDownNum = 0

        self.cv_db_mutex = threading.Lock()
        self.cv_list_mutex = threading.Lock()
        # url = "https://lpt.liepin.com/resume/downloadExp/?language=0&resume_fmt=html&save_type=download"
        self.url_downhead = self.cf["cv_down_url"] + "?language=0&resume_fmt=html&save_type=download"
        self.scraw_thread = threading.Thread(target=self._down_load_cv)
        self.scraw_thread.start()
        self.session = None
        self.pre_reflesh_time = 0
        maxNumRange = [int(i) for i in self.cf["scraw_max_num_per_day"].split(",")]
        self.maxCvNumPerDay = random.randint(maxNumRange[0], maxNumRange[1])
        self.log.fatal("self.maxCvNumPerDay:%s" % (str(self.maxCvNumPerDay)))

    def _down(self, url):
        return self.session.post(url)

    def logout(self):
        # url = "http://www.liepin.com/user/logout"
        url = self.cf["logout_url"]
        res = self.session.get(url)
        return res

    def release(self, update=None, level=None, job_info=None):
        u'''
        update:为None时，表示初次发布职位；如果要更新职位，需要传入jobid
        成功：返回值为jobid。
        
        #4868200
        '''
        query = "?ejob_id=" + str(update) if update else "?joblv=0"
        # doc = self.session.get("https://lpt.liepin.com/ejob/editEjob4Public/"+query)
        doc = self.session.get(self.cf["edit_job_url"] + query)
        release_data = template.getLiePinRelease(doc.content, job_info, level)
        release_data["actionType"] = "update" if update else "publish"

        url = "https://lpt.liepin.com/ejob/saveejob4public.json"
        # url=self.cf["save_job_url"]
        hd = self.hd
        hd["Host"] = "lpt.liepin.com"
        hd["Origin"] = "https://lpt.liepin.com"
        hd["User-Agent"] = self._getRandAgent()
        # hd["Referer"]="https://lpt.liepin.com/ejob/editEjob4Public"
        hd["X-Requested-With"] = "XMLHttpRequest"

        resp = self.session.post(url, data=release_data, headers=hd)
        res = ""
        print resp.text
        jo = json.loads(resp.text)
        if jo["flag"] == 1:
            url_back = jo["data"]["nextUrl"]
            res = url_back.split("?")[1].split("&")[0].split("=")[1]
            self.log.fatal("release successful, ejob_id:%s." % (res))
        else:
            res = jo["msg"]
            self.log.fatal("release failed, msg:%s." % (res))

        if update == None and job_info.has_key("ejob_title"):
            sokey = {"keys": job_info["ejob_title"],}
            if self.search_cv(sokey):
                self.log.fatal("searching ejob_title:%s has started" % (job_info["ejob_title"]))
        return res

    def _getCheckCode(self):
        # url="https://passport.liepin.com/captcha/randomcode/?0.36194390487117667"
        url = self.cf["check_code_url"]
        r1 = self.session.post(url)
        fn = "../tmp/1.bmp"
        f = open(fn, "wb")
        f.write(r1.content)
        f.close()
        res = get_result(fn)
        return res

    def _getRandAgent(self):
        return self.usr_agents[random.randint(0, len(self.usr_agents) - 1)]

    def login(self, usr='anehr', passwd='d3f3267d4762d52340c111f58e64b1dc'):
        self.session = requests.session()

        #         agent_ip  = "101.200.165.93:80"
        #         agent_ip = "111.56.32.72:80"
        #         #agent_ip = "202.100.167.137:80"
        #         #agent_ip  = "111.161.126.106:80"
        #         proxies = {
        #           "http": agent_ip,
        #           "https": agent_ip,
        #         }
        #         self.session.proxies = proxies

        url = "https://passport.liepin.com/e/login.json"
        post_data = {"user_kind": "1", "url": "", 'user_login': usr, 'user_pwd': passwd, "verifycode": ""}
        check_code_err_cnt = 0
        self.hd["Host"] = "passport.liepin.com"
        flag = 0
        msg = ""
        self.usr = usr
        while (1):
            ck = self._getCheckCode()
            post_data["verifycode"] = ck
            self.hd["User-Agent"] = self._getRandAgent()
            res = self.session.post(url, data=post_data, headers=self.hd);
            jo = json.loads(res.text)

            if jo["flag"] == 1:
                flag = 1
                msg = u"登录成功"
                res = self.session.get(jo["data"]["url"]);
                with open("../tmp/result.html", "w") as f:
                    f.write(res.content)
                self.log.fatal("usr:%s login liepin sucessfully." % (usr))
                break

            """{"code":"5000","msg":"用户名或密码错误，还有4次机会","flag":0}"""
            """{"code":"5000","msg":"验证码填写有误，请重新填写","flag":0}"""
            if jo["msg"] != u"验证码填写有误，请重新填写" and jo["msg"] != u"验证码不正确":
                msg = jo["msg"]
                break

            check_code_err_cnt += 1
            print check_code_err_cnt
            if check_code_err_cnt % 3 == 0:
                time.sleep(self.scraw_time_sp)
        return {"flag": flag, "msg": msg}

    def _get_all_jobs(self):
        url = "https://lpt.liepin.com/ejob/showPublishEjobList/"
        if not self.session:
            return []
        res = self.session.get(url)
        selector = etree.HTML(res.content)
        try:
            last_url = selector.xpath('//a[@class="last"]/@href')[0]
            kv_map = self._getUrlQuryMap(last_url)
            pageSize = kv_map["pageSize"]
            page_num = int(kv_map["curPage"]) + 1
        except:
            page_num = 1

        curr = 0
        ejobids = []
        while (curr < page_num):
            if curr > 0:
                res = self.session.get(url + "?pageSize=" + pageSize + "&curPage=" + str(curr))
                selector = etree.HTML(res.content)
            curr += 1
            lines = selector.xpath('//tr')
            for tr in lines:
                ejobid = tr.get("data-ejobid")
                if not ejobid:
                    continue
                ejobids.append(ejobid)
        print ejobids
        return ejobids

    def reflesh_jobs(self, jobs=None):
        u'''
        jobs的格式如下：
        jobs = "4821586|4762135|4868200|4868196|4868192|4868171|4863694|4853285|4824026|4762134|4671619|4670742|4590280"
        
        返回结果：
         成功：{"flag":"1","msg":"职位刷新成功"}
         识别：{"flag":"0","msg":"部分职位由于今天已经刷新过，没有刷新"}
        '''
        if jobs == None:
            jobs = "|".join(self._get_all_jobs())

        # jobs = "4880396"
        self.log.fatal("usr:%s update ids:%s" % (self.usr, jobs))
        self.log.fatal("usr:%s %s" % (self.usr, jobs))
        # url = "https://lpt.liepin.com/ejob/refreshEjobs"
        # url = self.cf["reflesh_url"]
        url = "https://lpt.liepin.com/ejob/refreshejobs.json"
        res = self.session.post(url, data={"ejob_ids": jobs}, headers={"X-Requested-With": "XMLHttpRequest"})
        jo = json.loads(res.content)
        return (str(jo["flag"]), "refresh ok.")

    def stop_job(self, jobs=None):
        u'''
        jobs的格式如下：
        jobs = "4868196|4868192"
        
        返回结果：
         成功：{"flag":"1","msg":"职位暂停成功"}
         识别：{"flag":"0","msg":"部分职位由于今天已经刷新过，没有刷新"}
        '''
        if jobs == None:
            return '{"flag":"0","msg":"部分职位由于今天已经刷新过，没有刷新"}'
        self.log.fatal("usr:%s %s" % (self.usr, jobs))
        url = "https://lpt.liepin.com/ejob/pauseejobs.json"
        # url = self.cf["stop_url"]
        res = self.session.post(url, data={"ejob_ids": jobs}, headers={"X-Requested-With": "XMLHttpRequest"})
        self.log.fatal(res.text)
        self.log.fatal("usr:%s %s" % (self.usr, res.text))
        jo = json.loads(res.text)
        if jo["flag"] == 1:
            return ("1", "stop successfully.")
        else:
            return ("0", "stop failed.")

    def check_new_cv(self, ejob_id="4762135"):
        """ejob_token = selector.xpath('//input[@name="ejob_token"]/@value')[0]"""

        self.log.fatal("usr:%s %s" % (self.usr, ejob_id))
        # url = "https://lpt.liepin.com/apply/ejob/showRecvResumeList/?kind=2&layout=2&ejob_id="+ejob_id
        url = self.cf["cv_list_url"] + "?kind=2&layout=2&ejob_id=" + ejob_id
        res = self.session.get(url)
        selector = etree.HTML(res.content)
        lines = selector.xpath('//tr[@data-readflag="UNREAD"]')
        cvs = []
        for tr in lines:
            cvs.append((tr.get("data-resumeid"), tr.get("data-resumeidencode"), tr.get("data-appejobid")))
        cv_info = [self._save_sv(cv) for cv in cvs]
        self.log.fatal("usr:%s check_new_cv %s" % (self.usr, cv_info))
        return cv_info

    def _save_sv(self, cv):
        if self.cv_db.has_key(cv[0]):
            return self.cv_db[cv[0]]
        strtime = time.strftime("%Y%m%d%H")
        cv_path = self.cv_path + os.sep + strtime
        if not os.path.exists(cv_path):
            os.mkdir(cv_path)
        url = self.url_downhead
        self.log.fatal("usr:%s cv_id:%s" % (self.usr, cv[0]))
        res_id_encode = cv[1]
        apply_id = cv[2]
        url += "&res_id_encode=" + res_id_encode + "&apply_id=" + apply_id
        print "down url:", url
        res = self._down(url)
        fn = cv_path + os.sep + cv[0] + ".html"
        with open(fn, "w") as f:
            f.write(res.content)

        fn_id = strtime + "/" + cv[0] + ".html"
        if self.cv_db_mutex.acquire(1):
            self.cv_db[cv[0]] = fn_id
            self.cv_db_mutex.release()
        self.log.fatal("usr:%s download cv_id:%s save to %s sucessful." % (self.usr, cv[0], fn))
        return fn_id

    def _pickle_cv_id(self):
        if self.cv_db_mutex.acquire(1):
            db_bak = {}
            try:
                with open(self.cv_db_file, "rb") as f:
                    db_bak = pickle.load(f)
            except:
                pass
            if len(db_bak) != len(self.cv_db):
                with open(self.cv_db_file, "wb") as f:
                    pickle.dump(self.cv_db, f, protocol=2)
            self.cv_db_mutex.release()

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
                self._down_named_cv()
                time.sleep(10)
                self.log.fatal("no cv to down:%d time:%s" % (self.no_cv_down, time.strftime("%Y-%m-%d %H:%M:%S")))
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

    def _getPageNum(self, selector):
        page_num = 0
        try:
            lastpage = selector.xpath('//a[@class="last"]/@href')[0]
            kv_map = self._getUrlQuryMap(lastpage)
            t_key = "curPage"
            if kv_map.has_key(t_key):
                try:
                    page_num = int(kv_map[t_key])
                except:
                    pass
        except:
            pass
        return page_num + 1

    def _getUrlQuryMap(self, url):
        kv_map = {}
        for kv in url.split("?")[1].split("&"):
            k_v = kv.split("=")
            kv_map[k_v[0]] = k_v[1]

        return kv_map

    def _collect_cv_info(self, sokey):
        url = "https://lpt.liepin.com/resume/soResumeNew/?forlog=1"
        payload, more_page = template.getSearchKeyInfo(sokey)

        print payload
        res = self.session.post(url, data=payload)
        selector = etree.HTML(res.content)
        page_num = self._getPageNum(selector)
        cur_page = 0
        print "page_num:", page_num
        while (cur_page < page_num):
            if cur_page > 0:
                more_page["curPage"] = str(cur_page)
                res = self.session.post(url, data=more_page)
                selector = etree.HTML(res.content)

            cur_page += 1
            lines = selector.xpath('//tr')
            cvs = []
            for tr in lines:
                res_id = tr.get("data-resumeid")
                if not res_id:
                    continue
                res_url = tr.get("data-resumeurl")
                kv_map = {}
                for kv in res_url.split("?")[1].split("&"):
                    k_v = kv.split("=")
                    kv_map[k_v[0]] = k_v[1]
                t_key = "res_id_encode"
                if not kv_map.has_key(t_key):
                    continue
                res_id_encode = kv_map[t_key]
                cvs.append((res_id, res_id_encode, ""))

            if self.cv_list_mutex.acquire(1):
                self.cv_list.extend(cvs)
                self.cv_list_mutex.release()
            time.sleep(self.scraw_time_sp)

    def _down_named_cv(self):
        def _getQuryInfo(selector, curr):
            try:
                qury_url = selector.xpath('//a[@class="last"]/@href')[0]
            except:
                return None, None
            q_map = self._getUrlQuryMap(qury_url)
            page_num = 0
            try:
                page_num = int(q_map["curPage"]) + 1
            except:
                pass
            pageSize = ""
            try:
                pageSize = q_map["pageSize"]
            except:
                pass

            k_ = ""
            try:
                k_ = int(q_map["_"]) + 1
            except:
                pass

            return page_num, "&pageSize=" + pageSize + "&curPage=" + str(curr) + "&_=" + k_,

        if self.session == None:
            return

        url = "https://lpt.liepin.com/apply/resume/showRecvResumeList/?kind=1&layout=2"
        res = self.session.get(url)
        selector = etree.HTML(res.content)
        cur_page = 0
        page_num, qury = _getQuryInfo(selector, cur_page + 1)
        if page_num == None:
            self.log.fatal("page_num == None")
            return
        while cur_page < page_num:
            if cur_page > 0:
                res = self.session.get(url + qury)
                selector = etree.HTML(res.content)
                if cur_page + 1 < page_num:
                    _, qury = _getQuryInfo(selector, cur_page + 1)
            cur_page += 1
            lines = selector.xpath('//tr')
            cvs = []
            for tr in lines:
                res_id = tr.get("data-resumeid")
                if not res_id:
                    continue
                resumeidencode = tr.get("data-resumeidencode")
                appejobid = tr.get("data-appejobid")
                cvs.append((res_id, resumeidencode, appejobid))

            if self.cv_list_mutex.acquire(1):
                self.cv_list.extend(cvs)
                self.cv_list_mutex.release()
            time.sleep(self.scraw_time_sp)

    def search_cv(self, sokey=None):
        if not sokey:
            return None

        t = threading.Thread(target=self._collect_cv_info, args=(sokey,))
        t.start()
        return "search started."

    def getCVContacts(self):
        url = "https://lpt.liepin.com/resume/socondition/"
        res = self.session.get(url)
        print res
        with open("../tmp/result1.html", "w") as f:
            f.write(res.content)

        url = "https://lpt.liepin.com/resume/soresume/?forlog=1"
        hd = {}
        hd["Referer"] = "https://lpt.liepin.com/resume/socondition/"
        hd["Upgrade-Insecure-Requests"] = "1"
        hd["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        hd["Accept-Encoding"] = "gzip, deflate"
        hd["Accept-Language"] = "zh-CN,zh;q=0.8"
        hd["Cache-Control"] = "max-age=0"
        hd["Connection"] = "keep-alive"
        hd["Content-Type"] = "application/x-www-form-urlencoded"
        hd["Host"] = "lpt.liepin.com"
        hd["Origin"] = "https://lpt.liepin.com"
        hd[
            "User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36"
        hd[
            "Cookie"] = "__uuid=1444473858080.98; _uuid=515909ADFFA8440C47F9A03932BEDFD7; pgv_pvi=6141179904; gr_user_id=0284b141-df0b-4adc-af07-accc4d9b0e18; user_login=anehr; msk=true; salary=true; autologin=true; is_lp_user=true; user_vip=0; fe_lpt_newindex=true; fe_lpt_publishjobnew=true; _fecdn_=0; fe_lpt_msk=true; _e_ld_auth_=g03EfP3RFKbVRTXONG%2Fdcg%3D%3D%0D%0A; verifycode=f617ca0a3b8245a69156f25297a1f6ef; user_name=%E5%BC%A0%E8%BF%9E%E6%88%90; user_id=25968799; lt_auth=6u8IOSEGmV%2F74neNjWVY5vtIjdisUD%2FI9XxbgBFVhdLuWqCx4PznSg2PqbgOxBIhkBwkd8ULNbb8%0D%0AMe3%2Fy3RC6EERwGmjlICzo%2Fq50WEBSeJcI%2F2h0f2rkciGE51zlHlXmHYwongfxkmm4UZ3YNW4nQs%3D%0D%0A; user_kind=1; login_temp=islogin; b-beta2-config=%7B%22v%22%3A%222%22%2C%22d%22%3A236%2C%22e%22%3A8628372%2C%22entry%22%3A%220%22%2C%22p%22%3A%222%22%2C%22n%22%3A%22%E5%BC%A0%E8%BF%9E%E6%88%90%22%2C%22audit%22%3A%221%22%2C%22user_id%22%3A25968799%2C%22ecomp_id%22%3A8628372%2C%22jz%22%3A%220%22%2C%22version%22%3A%222%22%7D; __tlog=1462448841967.17%7C00000000%7C00000000%7C00000000%7C00000000; __session_seq=39; __uv_seq=39; gr_session_id_2abfd0d7eaa44a729d761fb028300b6c=29a0fb7e-e657-40e9-ace6-8a7651657f46; Hm_lvt_a2647413544f5a04f00da7eee0d5e200=1460933464,1461498276,1461673445,1462448842; Hm_lpvt_a2647413544f5a04f00da7eee0d5e200=1462453057; JSESSIONID=0B4E4A1C556AAE9EFDD6CA3D1F031BC2; _mscid=00000000"

        res = self.session.get(
            "https://concat.lietou-static.com/dev/lpt/pc/revs/v1/tpls/resume/search_resid_new_d3773b2e.js")
        print res
        with open("../tmp/result2.html", "w") as f:
            f.write(res.content)

        res = self.session.get(
            "https://statistic.liepin.com/statisticPlatform/tLog?page_id=&url=https%3A%2F%2Flpt.liepin.com%2Fresume%2Fsoresume%2F%3Fforlog%3D1&refer=https%3A%2F%2Flpt.liepin.com%2Fresume%2Fsoresume%2F%3Fforlog%3D1&resolution=1920X1080&uuid=1444473858080.98&sessionId=1462448841967.17&if_mscid=00000000&il_mscid=00000000&ef_mscid=00000000&el_mscid=00000000&v_stay_time=142295&type=v&user_id=25968799&user_kind=1&session_seq=36&uv_seq=36&t=1462452652839")
        print res
        with open("../tmp/result3.html", "w") as f:
            f.write(res.content)

        res = self.session.get(
            "https://statistic.liepin.com/statVisit.do?site=1&userId=25968799&userKind=1&url=https%3A%2F%2Flpt.liepin.com%2Fresume%2Fsoresume%2F%3Fforlog%3D1&resolution=1920x1080&h=20&m=50&s=52&cookie=1&ref=https%3A%2F%2Flpt.liepin.com%2Fresume%2Fsoresume%2F%3Fforlog%3D1&puuid=14624525105496468945040&stay_time=142000&rand=0.985040241353391")
        print res
        with open("../tmp/result4.html", "w") as f:
            f.write(res.content)

        res = self.session.post(url, headers=hd,
                                data={"res_ids": "18447915", "res_ids": 26267261, "res_ids": "", "res_ids": "",
                                      "res_ids": ""})
        print res
        with open("../tmp/result5.html", "w") as f:
            f.write(res.content)

    def getAccountInfo(self):
        url = "https://lpt.liepin.com/lptresourcelog/showresourcelist/?is_first=0"


def test_login():
    liepin = CLiePin()
    res = liepin.login()
    print res
    res = liepin.getCVContacts()
    print res
    # liepin.scraw_thread.join()


def test_release_job():
    liepin = CLiePin()
    res = liepin.login()
    print res["msg"]
    # update = "4880396"
    res = liepin.release(update=None, level=1, job_info={"detail_language_english": 1,})
    print res


def test_stop_job():
    liepin = CLiePin()
    res = liepin.login()
    print res["msg"]
    res = liepin.stop_job(jobs="4868196")
    print res[0], res[1]


def test_check_job():
    liepin = CLiePin()
    res = liepin.login()
    print res["msg"]
    res = liepin.check_new_cv(ejob_id="4821586")
    print res


def test_reflesh_job():
    liepin = CLiePin()
    res = liepin.login()
    print res["msg"]
    # jobs="4821586|4762135"
    res = liepin.reflesh_jobs()
    print res


def test_all():
    liepin = CLiePin()
    res = liepin.login()
    print res["msg"]

    res = liepin.release(update="4880396", level=1, job_info={"detail_language_english": 1,})
    print res

    res = liepin.stop_job(jobs="4868196")
    print res

    res = liepin.check_new_cv(ejob_id="4762135")
    print res

    res = liepin.reflesh_jobs(jobs="4821586|4762135")
    print res

    res = liepin.logout()
    print res


def test_search_cv():
    liepin = CLiePin()
    res = liepin.login()
    print res["msg"]

    #     sokey={"search_level":"2",
    #             "search_scope":"",
    #             "keys":"",
    #             "keysRelation":"",
    #             "company_name":u"万得资讯",
    #             "company_name_scope":"",
    #             "industrys":"",
    #             "jobtitles":"",
    #             "dqs":"",
    #             "contains_wantdq":"0",
    #             "edulevellow":"",
    #             "edulevelhigh":"",
    #             "school_kind":"",
    #             "edulevel_tz":"",
    #             "agelow":"",
    #             "agehigh":"",
    #             "workyearslow":"",
    #             "workyearshigh":"",
    #             "sex":"",
    #             "updateDate":""}

    sokey = {"company_name": u"万得资讯"}
    res = liepin.search_cv(sokey)
    print res

    liepin.scraw_thread.join()


if __name__ == "__main__":
    #     liepin = CLiePin()
    #     res = liepin.login(u"唯捷配送","ecd2afe5d98baf7e39916c5366dd9efb")
    #     print res

    # test_login()
    test_release_job()
    # test_stop_job()
    # test_check_job()
    # test_reflesh_job()
    # test_all()
    # test_search_cv()

    print "done"
