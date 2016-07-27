# -*- coding: UTF-8 -*-
'''
Created on 2016年3月14日

@author: leftstone
'''
import os
from xml.etree import ElementTree

config = None
config_zhilian = None
config_qiancheng = None
cwd = os.getcwd()

project_dir = cwd if cwd[-3:] != "src" else cwd[:-4]


def _get_element(root, config, key, path, default=""):
    node_find = root.findall(path)
    p = default
    if len(node_find) != 0:
        p = node_find[0].text if node_find[0].text else p
    config[key] = p


def get_configs():
    global config
    if config:
        return config

    config = {}
    fn = project_dir + os.sep + "configs" + os.sep + "config.xml"
    text = open(fn, "r").read()
    root = ElementTree.fromstring(text)
    p = project_dir + os.sep + "resumes" + os.sep + "liepin"
    _get_element(root, config, "liepin_cv_path", 'paths/liepin_cv_path', p)
    p = project_dir + os.sep + "resumes" + os.sep + "liepin" + os.sep + "cv_db.pkl"
    _get_element(root, config, "liepin_cv_db_file", 'paths/liepin_cv_db_file', p)
    _get_element(root, config, "scraw_time_sp", 'down_load/scraw_time_sp', 0.1)
    _get_element(root, config, "scraw_time_range", 'down_load/scraw_time_range', "5,10")
    _get_element(root, config, "scraw_time_range_clock", 'down_load/scraw_time_range_clock', "9:00,21:00")
    _get_element(root, config, "scraw_max_num_per_day", 'down_load/scraw_max_num_per_day', "100,2000")

    _get_element(root, config, "reflesh_job_time", 'reflesh_job_time', "06:00")
    _get_element(root, config, "logout_url", 'logout_url', "http://www.liepin.com/user/logout")
    _get_element(root, config, "edit_job_url", 'edit_job_url', "https://lpt.liepin.com/ejob/editEjob4Public/")
    _get_element(root, config, "save_job_url", 'save_job_url', "https://lpt.liepin.com/ejob/saveEjob4Public")
    _get_element(root, config, "check_code_url", 'check_code_url',
                 "https://passport.liepin.com/captcha/randomcode/?0.36194390487117667")
    _get_element(root, config, "login_url", 'login_url', "https://passport.liepin.com/e/CLiliepinon")
    _get_element(root, config, "login_host", 'login_host', "passport.liepin.com")
    _get_element(root, config, "reflesh_url", 'reflesh_url', "https://lpt.liepin.com/ejob/refreshEjobs")
    _get_element(root, config, "stop_url", 'stop_url', "https://lpt.liepin.com/ejob/pauseEjobs")
    _get_element(root, config, "cv_list_url", 'cv_list_url',
                 "https://lpt.liepin.com/apply/ejob/showRecvResumeList/?kind=2&layout=2&ejob_id=")
    _get_element(root, config, "cv_down_url", 'cv_down_url',
                 "https://lpt.liepin.com/resume/downloadExp/?language=0&resume_fmt=html&save_type=download")

    return config


def get_zhilian_configs():
    global config_zhilian
    if config_zhilian:
        return config_zhilian
    fn = project_dir + os.sep + "configs" + os.sep + "config_zhilian.xml"
    config_zhilian = {}
    text = open(fn, "r").read()
    root = ElementTree.fromstring(text)
    p = project_dir + os.sep + "resumes" + os.sep + "zhilian"
    _get_element(root, config_zhilian, "zhilian_cv_path", 'paths/zhilian_cv_path', p)
    p = project_dir + os.sep + "resumes" + os.sep + "zhilian" + os.sep + "cv_db.pkl"
    _get_element(root, config_zhilian, "zhilian_cv_db_file", 'paths/zhilian_cv_db_file', p)
    _get_element(root, config_zhilian, "scraw_time_sp", 'down_load/scraw_time_sp', 1)
    _get_element(root, config_zhilian, "reflesh_job_time", 'reflesh_job_time', "06:00")
    _get_element(root, config_zhilian, "scraw_time_range", 'down_load/scraw_time_range', "5,10")
    _get_element(root, config_zhilian, "scraw_time_range_clock", 'down_load/scraw_time_range_clock', "9:00,21:00")
    _get_element(root, config_zhilian, "scraw_max_num_per_day", 'down_load/scraw_max_num_per_day', "100,2000")

    return config_zhilian


def get_qiancheng_configs():
    global config_qiancheng
    if config_qiancheng:
        return config_qiancheng
    fn = project_dir + os.sep + "configs" + os.sep + "config_qiancheng.xml"
    config_qiancheng = {}
    text = open(fn, "r").read()
    root = ElementTree.fromstring(text)
    p = project_dir + os.sep + "resumes" + os.sep + "qiancheng"
    _get_element(root, config_qiancheng, "qiancheng_cv_path", 'paths/qiancheng_cv_path', p)
    p = project_dir + os.sep + "resumes" + os.sep + "qiancheng" + os.sep + "cv_db.pkl"
    _get_element(root, config_qiancheng, "qiancheng_cv_db_file", 'paths/qiancheng_cv_db_file', p)
    _get_element(root, config_qiancheng, "scraw_time_sp", 'down_load/scraw_time_sp', 1)
    _get_element(root, config_qiancheng, "reflesh_job_time", 'reflesh_job_time', "06:00")
    _get_element(root, config_qiancheng, "scraw_time_range", 'down_load/scraw_time_range', "5,10")
    _get_element(root, config_qiancheng, "scraw_time_range_clock", 'down_load/scraw_time_range_clock', "9:00,21:00")
    _get_element(root, config_qiancheng, "scraw_max_num_per_day", 'down_load/scraw_max_num_per_day', "100,2000")

    return config_qiancheng


if __name__ == "__main__":
    cf = get_qiancheng_configs()
    print cf
