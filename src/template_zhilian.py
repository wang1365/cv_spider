# -*- coding: UTF-8 -*-
'''
Created on 2016年3月12日

@author: leftstone
'''
from lxml import etree

"""

 payload = {                   
                    "PriorityRule":"1",                  
                    "TemplateId":"CC382885514T90250025000",
                    "EmploymentType":"2",
                    "JobTitle":u"人事行政专员3",
                    "JobTypeMain":"5002000",
                    "SubJobTypeMain":"122",
                    "JobTypeMinor":"3010000",
                    "SubJobTypeMinor":"115",
                    "Quantity":"3",
                    "EducationLevel":"5",
                    "WorkYears":"-1",
                    "MonthlyPay":"0200104000",
                    "DontDisplayMonthlyPay":"False",
                    "JobDescription":'''<div style="font-size:12px;min-height:16px;"><div style="padding: 0px; margin: 0px; font-family: simsun; line-height: 25px; background-color: rgb(255, 255, 255); min-height: 16px;"><strong>职位职责：</strong></div><div style="padding: 0px; margin: 0px; font-family: simsun; line-height: 25px; background-color: rgb(255, 255, 255); min-height: 16px;">1、执行并完善公司的人事制度与计划，员工的入职、离职、异动、调岗等事项的办理<br/>2、人员的招聘与配置、人事信息管理与员工档案的维护，核算员工的薪酬福利等事宜；<br/>3、其它人事日常工作和部分行政后勤工作</div><div style="padding: 0px; margin: 0px; font-family: simsun; line-height: 25px; background-color: rgb(255, 255, 255); min-height: 16px;"><br/></div><div style="padding: 0px; margin: 0px; font-family: simsun; line-height: 25px; background-color: rgb(255, 255, 255); min-height: 16px;"><div style="padding: 0px; margin: 0px; min-height: 16px;"><strong>我们希望您：&nbsp;</strong></div><div style="padding: 0px; margin: 0px; min-height: 16px;">1、有大专以上学历，熟悉国家相关劳动法律、法规，熟悉人力资源管理工作流程和运作方式；<br/>2、具有较强的沟通能力及口头表达能力；<br/>3、熟悉使用office办公软件；</div><div style="padding: 0px; margin: 0px; min-height: 16px;">4、有物流行业经验者优先考虑、有驾照者优先考虑；</div><div style="padding: 0px; margin: 0px; min-height: 16px;"><br/></div><div style="padding: 0px; margin: 0px; min-height: 16px;"><strong>我们能给您：</strong></div><div style="padding: 0px; margin: 0px; min-height: 16px;">1、广阔的发展平台，因为我们是中国最大的零担快运加盟网络；</div><div style="padding: 0px; margin: 0px; min-height: 16px;">2、双维的晋升通道，我们已建立专业通道和管理通道任您选择；</div><div style="padding: 0px; margin: 0px; min-height: 16px;">3、合理的薪资报酬，我们实行KPI绩效考核制度，公平公正公开；</div><div style="padding: 0px; margin: 0px; min-height: 16px;">4、完善的培训体系，我们提供新员工、业务技能、管理晋升等培训；</div></div></div>''',
                    "welfaretab":"",
                    "PositionPubPlace":"636",
                    "ContractCityList":"489",
                    "PositionPubPlaceInitCityId":"",
                    "WorkAddress":u"无锡市锡山区八士镇芙蓉一路93号",
                    "WorkAddressCoordinate":"0,0",
                    "CompanyAddress":u"上海市青浦区徐泾镇华徐公路999号E通世界北区B座8F",
                    "DateEnd":"2016-04-14",
                    "ApplicationMethod":"2",
                    "EmailList":"1296131134@qq.com",
                    "ApplicationMethodOptionsList":"1,2",
                    "ESUrl":"",
                    "IsCorpUser":"False",
                    "IsShowRootCompanyIntro":"True",
                    "IsShowSubCompanyIntro":"False",
                    "DepartmentId":"38288551",
                    "PositionApplyReply":"-1"
                    }
                    
"""

"""
待沟通的payload
url = "http://rd2.zhaopin.com/rdapply/resumes/apply/search?SF_1_1_44=192942892&orderBy=CreateTime"
pay_load = {        
                    "PageList2":"",
                    "DColumn_hidden":"",
                    "searchKeyword":"",
                    "curSubmitRecord":"20",
                    "curMaxPageNum":"1",
                    "PageList2":"",
                    "buttonAsse":u"导入测评系统",
                    "buttonInfo":u"发通知信",
                    "SF_1_1_50":"2",
                    "SF_1_1_51":"-1",
                    "SF_1_1_45":"",
                    "SF_1_1_44":"192942892",
                    "SF_1_1_52":"0",
                    "SF_1_1_49":"0",
                    "IsInvited":"0",
                    "position_city":"[%%POSITION_CITY%%]",
                    "deptName":"",
                    "select_unique_id":"",
                    "selectedResumeList":"",
                    "PageNo":"",
                    "PosState":"",
                    "MinRowID":"",
                    "MaxRowID":"2722819791",
                    "RowsCount":"123",
                    "PagesCount":"5",
                    "PageType":"0",
                    "CurrentPageNum":"1",
                    "Position_IDs":"[%%POSITION_IDS%%]",
                    "Position_ID":"[%%POSITION_ID%%]",
                    "SortType":"0",
                    "isCmpSum":"0",
                    "SelectIndex_Opt":"0",
                    "Resume_count":"0",
                    "CID":"38288551",
                    "forwardingEmailList":"",
                    "click_search_op_type":"2",
                    "X-Requested-With":"XMLHttpRequest"
                    }
"""


def loadJobTemplate():
    jobVaryInfo = {}
    with open("../configs/template_job_zhilian.xml", "r") as f:
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
    with open("../configs/template_search_zhilian.xml", "r") as f:
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

    for k in key_data.keys():
        if k in search_template.keys():
            key_info[k] = key_data[k]

    key_info["orderBy"] = "DATE_MODIFIED,1"
    key_info["exclude"] = "1"
    key_info["SF_1_1_27"] = "0"
    return key_info


def getZhilianRelease(content, job_info=None, update=False):
    selector = etree.HTML(content)
    zhilian_tem = {}
    LoginPointId = selector.xpath('//input[@name="LoginPointId"]/@value')[0]
    PublicPoints = selector.xpath('//input[@name="PublicPoints"]/@value')[0]
    HavePermissionToPubPosition = selector.xpath('//input[@name="HavePermissionToPubPosition"]/@value')[0]
    CanPubPositionQty = selector.xpath('//input[@name="CanPubPositionQty"]/@value')[0]
    JobNo = selector.xpath('//input[@name="JobNo"]/@value')[0]
    SeqNumber = selector.xpath('//input[@name="SeqNumber"]/@value')[0]
    FilterId = selector.xpath('//input[@name="FilterId"]/@value')[0]

    zhilian_tem["LoginPointId"] = LoginPointId
    zhilian_tem["PublicPoints"] = PublicPoints
    zhilian_tem["HavePermissionToPubPosition"] = HavePermissionToPubPosition
    zhilian_tem["CanPubPositionQty"] = CanPubPositionQty
    zhilian_tem["JobNo"] = JobNo
    zhilian_tem["SeqNumber"] = SeqNumber
    zhilian_tem["FilterId"] = FilterId

    if update:
        Status = selector.xpath('//input[@name="Status"]/@value')[0]  #
        hide_JobTitle = selector.xpath('//input[@name="hide_JobTitle"]/@value')[0]
        PositionPubPlaceInitCityId = selector.xpath('//input[@name="PositionPubPlaceInitCityId"]/@value')[0]
        zhilian_tem["Status"] = Status
        zhilian_tem["hide_JobTitle"] = hide_JobTitle
        zhilian_tem["PositionPubPlaceInitCityId"] = PositionPubPlaceInitCityId
        zhilian_tem["btnAddClick"] = "saveasnotpub"
    else:
        zhilian_tem["btnAddClick"] = "saveandpub"
        try:
            if int(CanPubPositionQty) == 0:
                return "0\n\n可发布职位数为0，无法发布！"
        except:
            return "0\n\n可发布职位数获取失败：%s，无法发布！" % (CanPubPositionQty)

    if job_info and isinstance(job_info, dict):
        jobVaryInfo = loadJobTemplate()
        job_info_keys = job_info.keys()
        for k, v in jobVaryInfo.items():
            if k in job_info_keys:
                zhilian_tem[k] = job_info[k]
            else:
                zhilian_tem[k] = v
    if zhilian_tem.has_key("JobDescription"):
        zhilian_tem["editorValue"] = zhilian_tem["JobDescription"]
    return zhilian_tem


if __name__ == "__main__":
    jobVaryInfo = getSearchKeyInfo({"SF_1_1_25": u"万得资讯",})
    print isinstance({}, dict)
    for k, v in jobVaryInfo.items():
        print k, ":", v
