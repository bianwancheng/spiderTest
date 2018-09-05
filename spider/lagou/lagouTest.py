#!/usr/bin/env python
# encoding: utf-8
'''
@author: bwcheng
@time: 2018/8/7 10:27
@desc:
'''
import time
import requests
import xlsxwriter
from lxml import etree

keyWord = input("Please input the keywords that you want to :")
# keyWord = "python"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36",
    "Host": "www.lagou.com",
    "Referer": "https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=",
    "X-Anit-Forge-Token": None
}
workbook = xlsxwriter.Workbook('lagou.xlsx')
worksheet = workbook.add_worksheet('lagou')
list_row = ['industryField', 'companyShortName', 'positionName', 'createTime', 'positionAdvantage', 'salary',
                'city', 'jobNature', '职位诱惑']
worksheet.write_row('A1', list_row, workbook.add_format({'bold': True}))

# 创建excel并写入
def createExcel(dictData):
    workbook = xlsxwriter.Workbook('lagou.xlsx')
    worksheet = workbook.add_worksheet('lagou')
    list_row = ['industryField', 'companyShortName', 'positionName', 'createTime', 'positionAdvantage', 'salary',
                'city', 'jobNature', '职位诱惑']
    worksheet.write_row('A1', list_row, workbook.add_format({'bold': True}))
    for index in range(0, len(dictData)):
        list = [dictData[index]['industryField'], dictData[index]['companyShortName'], dictData[index]['positionName'],
                dictData[index]['createTime'],
                dictData[index]['positionAdvantage'], dictData[index]['salary'], dictData[index]['city'],
                dictData[index]['jobNature'],
                dictData[index]['职位诱惑']]
        print(dictData[index]['职位诱惑'])
        a = 'A'
        a = a + str(index + 2)
        worksheet.write_row(a, list)
    workbook.close()
    print('所有条目', len(dictData), '写入完成..')


# 获取总共页数
def getPageNum():
    url_page = ("https://www.lagou.com/jobs/list_{}?labelWords=&fromSearch=true&suginput=").format(keyWord)
    page_html = requests.get(url_page, headers=HEADERS)
    selector = etree.HTML(page_html.text)
    # xpath得到的是数组，得到页数并转换成int
    pageinfo = int(selector.xpath('//span[@class="span totalNum"]/text()')[0])
    return pageinfo


# 获取搜索到的页面的json数据
def getData():
    url = ('https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false')
    print(url)
    dataList = []
    index = 0
    pagenum = getPageNum()
    for page in range(1, pagenum + 1):
        form_data = {
            "first": "true",
            "pn": page,
            "kd": keyWord
        }
        # form_data = {
        #     "first": "true",
        #     "pn": 1,
        #     "kd": keyWord
        # }
        # print(page)
        html = requests.post(url=url, data=form_data, headers=HEADERS)
        # response对象转换成json
        html_json = html.json()
        # 此页搜索到的条数
        contentSize = int(html_json["content"]["positionResult"]["resultSize"])
        # print(contentSize)
        for index in range(0, contentSize):
            result = html_json["content"]["positionResult"]["result"][index]
            # positionId
            positionId = int(html_json["content"]["positionResult"]["result"][index]["positionId"])
            # 获取详情页面的数据,在此值简单写一下职位诱惑
            # url:https://www.lagou.com/jobs/97805.html   可以看出来是positionId
            url_detail = "https://www.lagou.com/jobs/{}.html".format(positionId)
            html = requests.get(url_detail, headers=HEADERS)
            # if html == '':
            #     time.sleep(120)
            #     html = requests.get(url_detail, headers=HEADERS)
            selector = etree.HTML(html.text)
            spanList = selector.xpath('//dd[@class="job-advantage"]/p/text()')
            span = "".join(spanList)
            # print(span)
            # print(result)
            # print('-' * 30)
            dictData = [{
                'industryField': result["industryField"],
                'companyShortName': result["companyShortName"],
                'positionName': result['positionName'],
                'createTime': result['createTime'],
                'positionAdvantage': result['positionAdvantage'],
                'salary': result['salary'],
                'city': result['city'],
                'jobNature': result['jobNature'],
                '职位诱惑': span
            }]
            dataList.extend(dictData)
            index = index + 1
            print('正在输出第', page, '页第', index, '条数据:', dictData)
            print('-' * 30)
            # 防止反爬机制设置下等待时间
            if page % 8 == 0:
                time.sleep(240)
            time.sleep(60)
        print(dataList)
    return dataList


if __name__ == '__main__':
    dataList = getData()
    createExcel(dataList)
