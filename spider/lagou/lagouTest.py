#!/usr/bin/env python
# encoding: utf-8
'''
@author: bwcheng
@time: 2018/8/7 10:27
@desc:
'''
import os
import random
import threading
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


# 读取ip
def readProxie():
    with open('ip_proxy.txt', 'r')as f:
        # proxieList = pickle.load(f)
        proxieList = f.readlines()
        len(proxieList)
        print(proxieList)
        return proxieList


# 删除ip_proxy.txt无效的iP
def deleteIp(dicIp):
    with open('ip_proxy.txt', 'r')as f:
        # proxieList = pickle.load(f)
        proxieList = f.readlines()
    with open('ip_proxy.txt', 'w')as fw:
        for ip in proxieList:
            if dicIp in ip:
                continue
            fw.write(ip)


# 随机一个ip地址
def randomIp():
    proxiesList = readProxie()
    # eval()函数转传成字典
    proxies = eval(proxiesList[random.randint(0, len(proxiesList))])
    return proxies, proxiesList


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


# 获取总共页数,返回总页数、此时的ip、ip列表
def getPageNum():
    url_page = ("https://www.lagou.com/jobs/list_{}?labelWords=&fromSearch=true&suginput=").format(keyWord)
    # # 随机一个ip地址
    proxies, proxiesList = randomIp()
    try:
        time.sleep(3)
        page_html = requests.get(url_page, proxies=proxies, headers=HEADERS, timeout=60)
        print("可以用的ip:", proxies)
    except:
        if len(proxiesList) != 0:
            print("删除无效的ip:", proxies)
            deleteIp(str(proxies))
            time.sleep(random.randint(8, 10))
            getPageNum()
    selector = etree.HTML(page_html.text)
    # xpath得到的是数组，得到页数并转换成int
    pageinfo = int(selector.xpath('//span[@class="span totalNum"]/text()')[0])
    return pageinfo, proxies, proxiesList


# 获取搜索到的页面的json数据
def getData():
    url = ('https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false')
    print(url)
    dataList = []
    pageinfo, proxies, proxiesList = getPageNum()
    print(pageinfo)
    for page in range(1, pageinfo + 1):
        print("进入到第", page, "页")
        form_data = {
            "first": "true",
            "pn": page,
            "kd": keyWord
        }
        try:
            print("此时的ip为：", proxies)
            print("每爬一页就换一个ip")
            while True:
                proxie, proxiesList = randomIp()
                if proxies != proxie:
                    print("换后的ip为:", proxie)
                    proxies = proxie
                    break
            time.sleep(random.randint(5, 10))
            html = requests.post(url=url, data=form_data, headers=HEADERS, proxies=proxies, timeout=60)
        except:
            deleteIp(proxies)
            # # 随机一个ip地址
            while len(proxiesList) > 0:
                proxies = randomIp()
                time.sleep(random.randint(8, 10))
                html = requests.post(url=url, data=form_data, headers=HEADERS, proxies=proxies, timeout=60)
                if html.status_code == 200:
                    break
                else:
                    deleteIp(proxies)
            if len(proxiesList) == 0:
                print("没有合适的ip终止爬取")
                return 'NULL'
        # response对象转换成json
        html_json = html.json()
        # 此页的json内容
        print(html_json)
        # 此页搜索到的条数
        contentSize = int(html_json["content"]["positionResult"]["resultSize"])
        print(contentSize)
        for index in range(0, contentSize):
            result = html_json["content"]["positionResult"]["result"][index]
            # positionId
            positionId = int(html_json["content"]["positionResult"]["result"][index]["positionId"])
            # 获取详情页面的数据,在此值简单写一下职位诱惑
            # url:https://www.lagou.com/jobs/97805.html   可以看出来是positionId
            url_detail = "https://www.lagou.com/jobs/{}.html".format(positionId)
            time.sleep(random.randint(8, 10))
            html = requests.get(url_detail, headers=HEADERS)
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
        # print(dataList)
    createExcel(dataList)


# 抓取有效ip
# 解析网页，并得到网页中的IP代理
def get_proxy(html):
    selector = etree.HTML(html)
    proxies = []

    for each in selector.xpath("//tr")[1:]:
        ip = each.xpath("./td[2]/text()")[0]
        port = each.xpath("./td[3]/text()")[0]
        type = each.xpath("./td[6]/text()")[0].lower()
        # 拼接IP地址，端口号
        str = ip + ":" + port
        # proxy定义成字典
        proxy = {type: str}
        proxies.append(proxy)
    print(len(proxies))
    test_proxies(proxies)

# 写入txt文件
def thread_write_proxy(proxy):
    with open("./ip_proxy.txt", 'a+') as f:
        print("正在写入：", proxy)
        # 字典不能录入,转换成字符串
        f.write(str(proxy) + '\n')
        print("录入完成！！！")


# 添加线程模式
def thread_test_proxy(proxy):
    # 验证ip是否可用就用需要爬取的网页url验证即可
    url = "https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false"
    header = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    }
    try:
        response = requests.get(
            url, headers=header, proxies=proxy, timeout=1)
        if response.status_code == 200:
            print("该代理IP可用：", proxy)
            thread_write_proxy(proxy)
        else:
            print("该代理IP不可用：", proxy)
    except Exception:
        print("该代理IP无效：", proxy)
        pass


# 验证已得到IP的可用性
def test_proxies(proxies):
    proxies = proxies
    # print("test_proxies函数开始运行。。。\n", proxies)
    for proxy in proxies:
        test = threading.Thread(target=thread_test_proxy, args=(proxy,))
        test.start()


def get_html():
    url = "http://www.xicidaili.com/nn/2"
    header = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    }
    response = requests.get(
        url,
        headers=header,
    )
    get_proxy(response.text)


if __name__ == '__main__':
    if not os.path.exists("ip_proxy.txt"):
        get_html()
        time.sleep(random.randint(5, 10))
    getData()
