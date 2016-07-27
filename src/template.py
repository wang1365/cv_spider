# -*- coding: UTF-8 -*-
'''
Created on 2016年3月12日

@author: leftstone
'''
from lxml import etree


def loadJobTemplate():
    jobVaryInfo = {}
    with open("../configs/template_job.xml", "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line == "" or line[0] == "#":
                continue
            kv = line.split(":")
            if len(kv) != 2:
                continue
            jobVaryInfo[kv[0]] = kv[1]
    return jobVaryInfo


def loadSearchTemplate():
    info = {}
    with open("../configs/template_search.xml", "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line == "" or line[0] == "#":
                continue
            kv = line.split(":")
            if len(kv) != 2:
                continue
            info[kv[0]] = kv[1]
    return info


def getSearchKeyInfo(key_data):
    search_template = loadSearchTemplate()
    key_info = {}
    if not (key_data and isinstance(key_data, dict)):
        return None

    conCnt = 0
    for k, v in search_template.items():
        if k in key_data:
            key_info[k] = key_data[k]
        else:
            key_info[k] = v
        if key_info[k] != "":
            conCnt += 1

    cstContent = '''{'''
    info_len = len(key_info)
    for ix, (k, v) in enumerate(key_info.items()):
        if ix < (info_len - 1):
            cstContent += '''"''' + k + '''":"''' + v + '''",'''
        else:
            cstContent += '''"''' + k + '''":"''' + v + '''"'''

    cstContent += '''}'''

    key_info["cstContent"] = cstContent
    key_info["contains_wantdq"] = "0"
    key_info["so_translate_flag"] = "1"
    key_info["conditionCount"] = str(conCnt)
    key_info["cs_id"] = ""
    key_info["cs_createtime"] = ""

    more = {"cs_id": "", "sortflag": "", "expendflag": "1", "pageSize": "20", "curPage": "1",
            "cs_createtime": "", "cstContent": key_info["cstContent"], "conditionCount": "1",
            "hasphoto": "", "search_type": "0", "search_level": key_info["search_level"],
            "cs_createtime_flag": "", "is_display_switch_button": "false",
            "so_translate_flag": key_info["so_translate_flag"], "completionSearchFlag": ""}
    return (key_info, more)


def getLiePinRelease(content, job_info=None, level=None):
    selector = etree.HTML(content)
    ejob_token = selector.xpath('//input[@name="ejob_token"]/@value')[0]
    deptlist = selector.xpath('//input[@name="deptlist"]/@value')[0]
    ejob_id = selector.xpath('//input[@name="ejob_id"]/@value')[0]
    lea_createtime = selector.xpath('//input[@name="lea_createtime"]/@value')[0]
    ejob_status_req = selector.xpath('//input[@name="ejob_status_req"]/@value')[0]

    lie_pin_tem = {}
    lie_pin_tem["ejob_token"] = ejob_token
    lie_pin_tem["deptlist"] = deptlist
    lie_pin_tem["ejob_id"] = ejob_id
    lie_pin_tem["lea_createtime"] = lea_createtime
    lie_pin_tem["ejob_status_req"] = ejob_status_req
    lie_pin_tem["ejob_lv"] = "0"

    if level != None:
        lie_pin_tem["isRtsFreeEjob"] = "false"
        lie_pin_tem["cvCostCount"] = "0"
        lie_pin_tem["ejobCostCount"] = "1"
        lie_pin_tem["ejob_lv"] = "1"

    if job_info and isinstance(job_info, dict):
        jobVaryInfo = loadJobTemplate()
        job_info_keys = job_info.keys()
        for k, v in jobVaryInfo.items():
            if k in job_info_keys:
                lie_pin_tem[k] = job_info[k]
            else:
                lie_pin_tem[k] = v

    return lie_pin_tem


if __name__ == "__main__":
    jobVaryInfo = loadJobTemplate()
    print isinstance({}, dict)
    for k, v in jobVaryInfo.items():
        print k, v
