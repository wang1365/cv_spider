# -*- coding: UTF-8 -*-
'''
Created on 2016年3月31日

@author: leftstone
'''

from lxml import etree
from string import strip
import re

jobInfo = {
    'ScriptManager1': "ScriptManager1|btnPublish",
    'strMarkValue': "New",
    'tblFlag': "",
    'jobId': "",
    'MainMenuNew1$CurMenuID': "MainMenuNew1_imgJob|sub2",
    'drpPosition': "",
    'drpDiv': "",
    'hidMdJobName': "0",
    # 'CJOBNAME':"行政专员3",
    'hidJobCode': "",
    'POSCODE': "",
    'EJOBNAME': "",
    # 'JOBNUM':"5",
    'JobAreaAllValue': "'010000','020000','030000','030200','030300','030400','030500','030600','030700','030800','031400','031500','031700','031800','031900','032000','032100','032200','032300','032400','032600','032700','032800','032900','040000','050000','060000','070000','070200','070300','070400','070500','070600','070700','070800','070900','071000','071100','071200','071300','071400','071600','071800','071900','072000','072100','072300','072500','080000','080200','080300','080400','080500','080600','080700','080800','080900','081000','081100','081200','081400','081600','090000','090200','090300','090400','090500','090600','090700','090800','090900','091000','091100','091200','091300','091400','091500','091600','091700','091800','091900','092000','092100','092200','092300','100000','100200','100300','100400','100500','100600','100700','100800','100900','101000','101100','101200','101300','101400','101500','101600','101700','101800','101900','102000','102100','110000','110200','110300','110400','110500','110600','110700','110800','110900','111000','120000','120200','120300','120400','120500','120600','120700','120800','120900','121000','121100','121200','121300','121400','121500','121600','121700','121800','130000','130200','130300','130400','130500','130600','130700','130800','130900','131000','131100','131200','140000','140200','140300','140400','140500','140600','140700','140800','140900','141000','141100','141200','141300','141400','141500','150000','150200','150300','150400','150500','150600','150700','150800','150900','151000','151100','151200','151400','151500','151600','151700','151800','160000','160200','160300','160400','160500','160600','160700','160800','160900','161000','161100','161200','161300','170000','170200','170300','170400','170500','170600','170700','170800','170900','171000','171100','171200','171300','171400','171500','171600','171700','171800','171900','172000','180000','180200','180300','180400','180500','180600','180700','180800','180900','181000','181100','181200','181300','181400','181500','181600','181700','181800','190000','190200','190300','190400','190500','190600','190700','190800','190900','191000','191100','191200','191300','191400','191500','200000','200200','200300','200400','200500','200600','200700','200800','200900','201000','201100','201200','210000','210200','210300','210400','210500','210600','210700','210800','210900','211000','211100','211200','220000','220200','220300','220400','220500','220600','220700','220800','220900','221000','221100','221200','221300','221400','230000','230200','230300','230400','230500','230600','230700','230800','230900','231000','231100','231200','231300','231400','231500','240000','240200','240300','240400','240500','240600','240700','240800','240900','241000','241100','250000','250200','250300','250400','250500','250600','251000','251100','251200','251300','251400','251500','251600','251700','251800','251900','252000','260000','260200','260300','260400','260500','260600','260700','260800','260900','261000','270000','270200','270300','270400','270500','270600','270700','270800','270900','271000','271100','271200','271300','271400','271500','280000','280200','280300','280400','280700','280800','280900','281000','281100','281200','281300','281400','281500','290000','290200','290300','290400','290500','290600','300000','300200','300300','300400','300500','300600','300700','300800','310000','310200','310300','310400','310500','310600','310700','310800','310900','311000','311100','311200','311300','311400','311500','311600','311700','311800','311900','320000','320200','320300','320400','320500','320600','320700','320800','320900','330000','340000','350000','360000','00000'",
    'AllJobArea': "'010000','020000','030000','030200','030300','030400','030500','030600','030700','030800','031400','031500','031700','031800','031900','032000','032100','032200','032300','032400','032600','032700','032800','032900','040000','050000','060000','070000','070200','070300','070400','070500','070600','070700','070800','070900','071000','071100','071200','071300','071400','071600','071800','071900','072000','072100','072300','072500','080000','080200','080300','080400','080500','080600','080700','080800','080900','081000','081100','081200','081400','081600','090000','090200','090300','090400','090500','090600','090700','090800','090900','091000','091100','091200','091300','091400','091500','091600','091700','091800','091900','092000','092100','092200','092300','100000','100200','100300','100400','100500','100600','100700','100800','100900','101000','101100','101200','101300','101400','101500','101600','101700','101800','101900','102000','102100','110000','110200','110300','110400','110500','110600','110700','110800','110900','111000','120000','120200','120300','120400','120500','120600','120700','120800','120900','121000','121100','121200','121300','121400','121500','121600','121700','121800','130000','130200','130300','130400','130500','130600','130700','130800','130900','131000','131100','131200','140000','140200','140300','140400','140500','140600','140700','140800','140900','141000','141100','141200','141300','141400','141500','150000','150200','150300','150400','150500','150600','150700','150800','150900','151000','151100','151200','151400','151500','151600','151700','151800','160000','160200','160300','160400','160500','160600','160700','160800','160900','161000','161100','161200','161300','170000','170200','170300','170400','170500','170600','170700','170800','170900','171000','171100','171200','171300','171400','171500','171600','171700','171800','171900','172000','180000','180200','180300','180400','180500','180600','180700','180800','180900','181000','181100','181200','181300','181400','181500','181600','181700','181800','190000','190200','190300','190400','190500','190600','190700','190800','190900','191000','191100','191200','191300','191400','191500','200000','200200','200300','200400','200500','200600','200700','200800','200900','201000','201100','201200','210000','210200','210300','210400','210500','210600','210700','210800','210900','211000','211100','211200','220000','220200','220300','220400','220500','220600','220700','220800','220900','221000','221100','221200','221300','221400','230000','230200','230300','230400','230500','230600','230700','230800','230900','231000','231100','231200','231300','231400','231500','240000','240200','240300','240400','240500','240600','240700','240800','240900','241000','241100','250000','250200','250300','250400','250500','250600','251000','251100','251200','251300','251400','251500','251600','251700','251800','251900','252000','260000','260200','260300','260400','260500','260600','260700','260800','260900','261000','270000','270200','270300','270400','270500','270600','270700','270800','270900','271000','271100','271200','271300','271400','271500','280000','280200','280300','280400','280700','280800','280900','281000','281100','281200','281300','281400','281500','290000','290200','290300','290400','290500','290600','300000','300200','300300','300400','300500','300600','300700','300800','310000','310200','310300','310400','310500','310600','310700','310800','310900','311000','311100','311200','311300','311400','311500','311600','311700','311800','311900','320000','320200','320300','320400','320500','320600','320700','320800','320900','330000','340000','350000','360000'",
    'RestrictedJobArea': "'010000','020000','030000','030200','030300','030400','030500','030600','030700','030800','031400','031500','031700','031800','031900','032000','032100','032200','032300','032400','032600','032700','032800','032900','040000','050000','060000','070000','070200','070300','070400','070500','070600','070700','070800','070900','071000','071100','071200','071300','071400','071600','071800','071900','072000','072100','072300','072500','080000','080200','080300','080400','080500','080600','080700','080800','080900','081000','081100','081200','081400','081600','090000','090200','090300','090400','090500','090600','090700','090800','090900','091000','091100','091200','091300','091400','091500','091600','091700','091800','091900','092000','092100','092200','092300','100000','100200','100300','100400','100500','100600','100700','100800','100900','101000','101100','101200','101300','101400','101500','101600','101700','101800','101900','102000','102100','110000','110200','110300','110400','110500','110600','110700','110800','110900','111000','120000','120200','120300','120400','120500','120600','120700','120800','120900','121000','121100','121200','121300','121400','121500','121600','121700','121800','130000','130200','130300','130400','130500','130600','130700','130800','130900','131000','131100','131200','140000','140200','140300','140400','140500','140600','140700','140800','140900','141000','141100','141200','141300','141400','141500','150000','150200','150300','150400','150500','150600','150700','150800','150900','151000','151100','151200','151400','151500','151600','151700','151800','160000','160200','160300','160400','160500','160600','160700','160800','160900','161000','161100','161200','161300','170000','170200','170300','170400','170500','170600','170700','170800','170900','171000','171100','171200','171300','171400','171500','171600','171700','171800','171900','172000','180000','180200','180300','180400','180500','180600','180700','180800','180900','181000','181100','181200','181300','181400','181500','181600','181700','181800','190000','190200','190300','190400','190500','190600','190700','190800','190900','191000','191100','191200','191300','191400','191500','200000','200200','200300','200400','200500','200600','200700','200800','200900','201000','201100','201200','210000','210200','210300','210400','210500','210600','210700','210800','210900','211000','211100','211200','220000','220200','220300','220400','220500','220600','220700','220800','220900','221000','221100','221200','221300','221400','230000','230200','230300','230400','230500','230600','230700','230800','230900','231000','231100','231200','231300','231400','231500','240000','240200','240300','240400','240500','240600','240700','240800','240900','241000','241100','250000','250200','250300','250400','250500','250600','251000','251100','251200','251300','251400','251500','251600','251700','251800','251900','252000','260000','260200','260300','260400','260500','260600','260700','260800','260900','261000','270000','270200','270300','270400','270500','270600','270700','270800','270900','271000','271100','271200','271300','271400','271500','280000','280200','280300','280400','280700','280800','280900','281000','281100','281200','281300','281400','281500','290000','290200','290300','290400','290500','290600','300000','300200','300300','300400','300500','300600','300700','300800','310000','310200','310300','310400','310500','310600','310700','310800','310900','311000','311100','311200','311300','311400','311500','311600','311700','311800','311900','320000','320200','320300','320400','320500','320600','320700','320800','320900','330000','340000','350000','360000'",
    # 'JobAreaSelectValue':"040000",
    # 'DEGREEFROM':"",
    # 'txtSelectedJobAreas':"深圳",
    'hidJobAreasLimit': "",
    'hidWorkareaId': "",
    'hidAddress': "盐田区东海道435号安能物流(义乌华贸城公交站下车即到)",
    'hidWorkarea': "040000",
    'hidLon': "",
    'hidLat': "",
    'hidLandMarkId': "",
    # 'txtWorkAddress':"深圳市盐田区东海道435号安能物流(义乌华贸城公交站下车即到)",
    # 'AGEFROM':"",
    # 'AGETO':"",
    # 'FuncType1Text':"行政专员/助理",
    # 'FuncType1Value':"2303",
    # 'FL1':"",
    'TxtOtherLanguage1': "",
    # 'FLevel1':"",
    'FuncType2Text': "",
    'FuncType2Value': "",
    'FL2': "",
    'TxtOtherLanguage2': "",
    'FLevel2': "",
    'hidFunRecommend1': "",
    'hidFunRecommend2': "",
    'hidFunRecommend3': "",
    'hidFunRecommendSelected': "",
    # 'WORKYEAR':"",
    # 'Major1Text':"",
    # 'Major1Value':"",
    # 'Term':"0",
    'Major2Text': "",
    'Major2Value': "",
    'hidIsSalaryDefault': "",
    'hidIsCustomSalary': "0",
    'DdrSalaryType': "1",
    'YEARSALARY': "01",
    # 'ProvideSalary':"05",
    'TxtSalaryFrom': "",
    'TxtSalaryTo': "",
    'TxtCustomSalary': "",
    'hidAllSalaryCities': "北京,长春,成都,重庆,长沙,东莞,大连,福州,广东省,广州,哈尔滨,合肥,杭州,济南,江西省,昆明,宁波,南京,青岛,上海,苏州,沈阳,深圳,天津,武汉,无锡,西安,厦门,郑州",
    'hidAjaxIndustry': "交通/运输/物流",
    'hidAjaxJobType1': "行政|后勤",
    'hidAjaxJobType2': "",
    'hidAjaxJobName1': "行政专员|助理",
    'hidAjaxJobName2': "",
    'hidAjaxCompanyType': "民营/私营企业",
    'hidLinkButtonID': "1",
    'hidJobtype_erji': "行政专员|助理",
    'hidJobtype_erji2': "",
    # 'TxtJobKeywords':"",
    'hidIndex': "0",
    'viewTimes': "0",
    # 'CJOBINFO':'''''',
    'hidCCopyContent': "",
    'EJOBINFO': "",
    'hidMode': "1",
    'hidJobDescAss1': "",
    'hidJobDescAss2': "",
    'hidJobDescAss3': "",
    'hidJobDescAssContent': "",
    'radEmail1': "0",
    'JOBEMAIL': "sunlijun@ane56.com",
    'HidCompanyEmail': "sunlijun@ane56.com",
    'HidDivEmail': "",
    'hidEmails': "{mail4383568:fuwenliang@ane56.com,mail4383569:pengbo@ane56.com,mail4393544:zhaorongdi@ane6.com}",
    'hasFilter': "",
    'RefID1': "",
    'RefID2': "",
    'HidFLTID': "",
    'HidNewFLTID': "",
    # 'JOBORDER':"999",
    'jobOrderInputTip': "1",
    'hidDivOrder': "-1",
    'hidJobOrderCoid': "3250422",
    'viewTimes2': "0",
    'hidUrlParameters': "",
    'WCBigAreaCode1$2': "rdbGroup2_1",
    'WCBigAreaCode2$2': "rdbGroup2_1",
    'TextKeyWords': "",
    'HidSHowSaleDiv': "0",
    'HidSaleSelect': "",
    'TextKeyWords2': "",
    'HidSHowSaleDiv2': "",
    'HidSale2Select': "",
    'TpmName': "",
    'checkErr': "1^230:373|2^255:373|3^326:221|4^283:293|5^-22:0|6^0:0|7^347:727|8^347:856|9^372:982|10^397:982|11^1077:309|12^659:108|13^-22:0|14^230:857|15^200-22:200|16^-22:0|17^-22:0|",
    'hidCOID': "",
    'hidDIVID': "",
    'hidMark': "Job",
    'hidTop': "1053",
    'hidLeft': "523",
    'ViewCOID': "",
    'ViewDIVID': "",
    'ViewJobArea': "",
    'ViewCJobName': "",
    'ViewEJobName': "",
    'ViewIssuehDate': "",
    'ViewPOSCODE': "",
    'ViewNewJobName': "",
    'hidWelfare': "",
    'ddlCompanyType': "",
    'matchjobFun': "3",
    'matchjobInd': "3",
    'matchmajor': "3",
    'matchedu': "3",
    'matchworkyear': "3",
    'matchage': "3",
    'matchsalary': "3",
    'matchlang': "3",
    'matchlocal': "3",
    'workaddressId': "",
    'workaddressCityCode': "",
    '__EVENTTARGET': "",
    '__EVENTARGUMENT': "",
    '__LASTFOCUS': "",
    '__VIEWSTATE': "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",
    '__ASYNCPOST': "true",
}

search_info = {
    "ScriptManager1": "ScriptManager1|btnSearch",
    "DpSearchList": "",
    "txtUserID": u"--多个ID号用空格隔开--",
    "WORKFUN1$Text": u"最多只允许选择3个项目",
    "WORKFUN1$Value": "",
    "KEYWORD": "机器学习",
    "chkKeyWord": "on",
    "AREA$Text": "",
    "AREA$Value": "",
    "WorkYearFrom": "0",
    "WorkYearTo": "99",
    "TopDegreeFrom": "",
    "TopDegreeTo": "",
    "LASTMODIFYSEL": "5",
    "WORKINDUSTRY1$Text": u"最多只允许选择3个项目",
    "WORKINDUSTRY1$Value": "",
    "SEX": "99",
    "JOBSTATUS": "99",
    "hidSearchID": "2,3,6,23,8,1,4,5,25,2,3,6,23",
    "hidWhere": "",
    "hidValue": "",
    "hidTable": "",
    "hidSearchNameID": "",
    "hidPostBackFunType": "",
    "hidChkedRelFunType": "",
    "hidChkedExpectJobArea": "",
    "hidChkedKeyWordType": "0",
    "hidNeedRecommendFunType": "",
    "hidIsFirstLoadJobDiv": "1",
    "txtSearchName": "",
    "ddlSendCycle": "1",
    "ddlEndDate": "7",
    "ddlSendNum": "10",
    "txtSendEmail": "",
    "COID": "",
    "DIVID": "",
    "txtJobName": "",
    "__ASYNCPOST": "true",
    "btnSearch": u"查询",
}


def loadSearchTemplate():
    info = {}
    with open("../configs/template_search_qiancheng.xml", "r") as f:
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


def getSearchKeyInfo(content, key_data):
    search_template = loadSearchTemplate()
    key_info = search_info
    if not (key_data and isinstance(key_data, dict)):
        return None

    for k in key_data.keys():
        if k in search_template.keys():
            key_info[k] = key_data[k]

    selector = etree.HTML(content)

    key_info["__EVENTTARGET"] = selector.xpath('//input[@name="__EVENTTARGET"]/@value')[0]
    key_info["__EVENTARGUMENT"] = selector.xpath('//input[@name="__EVENTARGUMENT"]/@value')[0]
    key_info["__LASTFOCUS"] = selector.xpath('//input[@name="__LASTFOCUS"]/@value')[0]
    key_info["__VIEWSTATE"] = selector.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
    key_info["MainMenuNew1$CurMenuID"] = selector.xpath('//input[@name="MainMenuNew1$CurMenuID"]/@value')[0]
    key_info["hidSearchID"] = selector.xpath('//input[@name="hidSearchID"]/@value')[0]

    return key_info


def getSearchIDInfo(content, cvID):
    key_info = {
        "MainMenuNew1$CurMenuID": "MainMenuNew1_imgResume|sub4",
        "txtUserID": "16815311",
        "DpSearchList": "",
        "WORKFUN1$Text": "最多只允许选择3个项目",
        "WORKFUN1$Value": "",
        "KEYWORD": "---多关键字用空格隔开，请勿输入姓名、联系方式---",
        "AREA$Value": "",
        "WorkYearFrom": "0",
        "WorkYearTo": "99",
        "TopDegreeFrom": "",
        "TopDegreeTo": "",
        "LASTMODIFYSEL": "5",
        "WORKINDUSTRY1$Text": "最多只允许选择3个项目",
        "WORKINDUSTRY1$Value": "",
        "SEX": "99",
        "JOBSTATUS": "99",
        "hidSearchID": "2,3,6,23,8,1,4,5,25,2,3,6,23,2,3,6,23,2,3,6,23",
        "hidWhere": "",
        "hidValue": "ResumeID#16815311",
        "hidTable": "",
        "hidSearchNameID": "",
        "hidPostBackFunType": "",
        "hidChkedRelFunType": "",
        "hidChkedExpectJobArea": "",
        "hidChkedKeyWordType": "0",
        "hidNeedRecommendFunType": "",
        "hidIsFirstLoadJobDiv": "1",
        "txtSearchName": "",
        "ddlSendCycle": "1",
        "ddlEndDate": "7",
        "ddlSendNum": "10",
        "txtSendEmail": "",
        "COID": "",
        "DIVID": "",
        "txtJobName": "",
        "showGuide": "1",
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE": ""}

    selector = etree.HTML(content)

    key_info["__EVENTTARGET"] = selector.xpath('//input[@name="__EVENTTARGET"]/@value')[0]
    key_info["__EVENTARGUMENT"] = selector.xpath('//input[@name="__EVENTARGUMENT"]/@value')[0]
    key_info["__LASTFOCUS"] = selector.xpath('//input[@name="__LASTFOCUS"]/@value')[0]
    key_info["__VIEWSTATE"] = selector.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
    key_info["hidSearchID"] = selector.xpath('//input[@name="hidSearchID"]/@value')[0]
    key_info["txtUserID"] = cvID
    key_info["hidValue"] = "ResumeID#" + cvID
    return key_info


def getCVKey(content):
    key_info = {
        "EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "resumeViewFolderType": "TEMP",
        "hidMenuStatus": "0",
        "hidUserID": "16815311",
        "hidFolder": "TEMP",
        "hidSeqID": "16815311",
        "hidKeyWord": "",
        "hidJobID": "0",
        "hidAllSeqIds": "16815311",
        "hidAllUserIds": "16815311",
        "hidAllUserNames": "",
        "hidCheckedUserIds": "",
        "hidVisitedUserIds": "",
        "hidCheckedSeqIds": "",
        "hidCheckUserIds": "16815311",
        "hidCheckKey": "b722ba5337c06b7b6f60170632ec6b81",
        "hidIsRecommended": "",
        "lang": "",
        "hidWhere": "",
        "hidUserSex": "",
        "__VIEWSTATE": ""}
    selector = etree.HTML(content)

    key_info["hidUserID"] = selector.xpath('//input[@name="hidUserID"]/@value')[0]
    key_info["hidSeqID"] = selector.xpath('//input[@name="hidSeqID"]/@value')[0]
    key_info["hidAllSeqIds"] = selector.xpath('//input[@name="hidAllSeqIds"]/@value')[0]
    key_info["hidAllUserIds"] = selector.xpath('//input[@name="hidAllUserIds"]/@value')[0]
    key_info["hidCheckUserIds"] = selector.xpath('//input[@name="hidCheckUserIds"]/@value')[0]
    key_info["hidCheckKey"] = selector.xpath('//input[@name="hidCheckKey"]/@value')[0]
    key_info["__VIEWSTATE"] = selector.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
    return key_info


def loadJobTemplate():
    jobVaryInfo = {}
    with open("../configs/template_job_qiancheng.xml", "r") as f:
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


def getQianChengRelease(content, job_info=None, update=False):
    content = '<?xml version="1.0"?>\n' + content
    selector = etree.HTML(content)

    qc_job = jobInfo
    try:
        hidWorkareaId = selector.xpath('//input[@name="hidWorkareaId"]/@value')[0]
    except:
        hidWorkareaId = ""

    try:
        __LASTFOCUS = selector.xpath('//input[@name="__LASTFOCUS"]/@value')[0]
        __EVENTARGUMENT = selector.xpath('//input[@name="__EVENTARGUMENT"]/@value')[0]
        __EVENTTARGET = selector.xpath('//input[@name="__EVENTTARGET"]/@value')[0]
    except:
        __LASTFOCUS = ""
        __EVENTARGUMENT = ""
        __EVENTTARGET = ""

    qc_tem = {"strMarkValue": selector.xpath('//input[@name="strMarkValue"]/@value')[0],
              "MainMenuNew1_CurMenuID": selector.xpath('//input[@name="MainMenuNew1$CurMenuID"]/@value')[0],
              "drpCompany": selector.xpath('//table/tr/td/span/div/select/option[@selected="selected"]/@value')[0],
              "hidMdJobName": selector.xpath('//input[@name="hidMdJobName"]/@value')[0],
              "JobAreaAllValue": selector.xpath('//input[@name="JobAreaAllValue"]/@value')[0],
              "AllJobArea": selector.xpath('//input[@name="AllJobArea"]/@value')[0],
              "RestrictedJobArea": selector.xpath('//input[@name="RestrictedJobArea"]/@value')[0],
              "hidWorkareaId": hidWorkareaId,
              "hidAddress": selector.xpath('//input[@name="hidAddress"]/@value')[0],
              "hidWorkarea": selector.xpath('//input[@name="hidWorkarea"]/@value')[0],
              "txtWorkAddress": selector.xpath('//input[@name="txtWorkAddress"]/@value')[0],
              "__VIEWSTATE": selector.xpath('//input[@name="__VIEWSTATE"]/@value')[0],
              "__LASTFOCUS": __LASTFOCUS,
              "__EVENTARGUMENT": __EVENTARGUMENT,
              "__EVENTTARGET": __EVENTTARGET,
              "matchjobFun": selector.xpath('//input[@name="matchjobFun"]/@value')[0],
              "matchjobInd": selector.xpath('//input[@name="matchjobInd"]/@value')[0],
              "matchmajor": selector.xpath('//input[@name="matchmajor"]/@value')[0],
              "matchedu": selector.xpath('//input[@name="matchedu"]/@value')[0],
              "matchworkyear": selector.xpath('//input[@name="matchworkyear"]/@value')[0],
              "matchage": selector.xpath('//input[@name="matchage"]/@value')[0],
              "matchsalary": selector.xpath('//input[@name="matchsalary"]/@value')[0],
              "matchlang": selector.xpath('//input[@name="matchlang"]/@value')[0],
              "matchlocal": selector.xpath('//input[@name="matchlocal"]/@value')[0],
              "jobOrderInputTip": selector.xpath('//input[@name="jobOrderInputTip"]/@value')[0],
              "hidDivOrder": selector.xpath('//input[@name="hidDivOrder"]/@value')[0],
              "hidJobOrderCoid": selector.xpath('//input[@name="hidJobOrderCoid"]/@value')[0],
              'viewTimes': selector.xpath('//input[@name="viewTimes"]/@value')[0],
              'hidIndex': selector.xpath('//input[@name="hidIndex"]/@value')[0],}

    # print chardet.detect(qc_tem["hidAddress"])
    for k, v in qc_tem.iteritems():
        qc_job[k] = v

    #     for k,v in jobInfo.iteritems():
    #         qc_tem[k] = v

    if job_info and isinstance(job_info, dict):
        jobVaryInfo = loadJobTemplate()
        job_info_keys = job_info.keys()
        for k, v in jobVaryInfo.items():
            if k in job_info_keys:
                qc_job[k] = job_info[k]
            else:
                qc_job[k] = v
        if job_info.has_key("txtSelectedJobAreas"):
            places = re.split('，|,', job_info["txtSelectedJobAreas"])
            codes = [getCityCode(strip(p)) for p in places]
            if "xxx" in codes:
                return "invalid city"
            cityCode = "|".join(codes)
            qc_job["JobAreaSelectValue"] = cityCode
            qc_job["hidAddress"] = job_info['hidAddress']
            qc_job["hidWorkarea"] = getCityCode(strip(job_info['hidWorkarea']))
            qc_job["txtWorkAddress"] = job_info['hidWorkarea'] + job_info['hidAddress']

    if update == True:
        qc_job["strMarkValue"] = "Edit"
        qc_job["CJOBNAME"] = selector.xpath('//input[@name="CJOBNAME"]/@value')[0]
        qc_job["btnSave"] = "保存"
    else:
        qc_job["btnPublish"] = "发布"

    return qc_job


def getCityCode(city="孝感"):
    city2code = {}
    with open("../tmp/DictTable.js", "r") as f:
        conts = f.read()[1:-1]
    for place in conts.split("}, {"):
        parts = place.split(",")
        c = strip(parts[0].split(":")[1])
        p = strip(parts[1].split(":")[1])
        city2code[p[1:-1]] = c[1:-1]

    if not city2code.has_key(city):
        return "xxx"
    return city2code[city]


if __name__ == "__main__":
    #     jobVaryInfo = loadSearchTemplate()
    #     print isinstance({}, dict)
    #     for k,v in jobVaryInfo.items():
    #         print k,":",v
    print getCityCode()
    places = re.split('，|,', "杭州，北京")

    print places
    cityCode = "|".join([getCityCode(strip(p)) for p in places])
    print "ddd", cityCode
