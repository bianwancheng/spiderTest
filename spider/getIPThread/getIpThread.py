#!/usr/bin/env python
# encoding: utf-8
'''
@author: bwcheng
@time: 2018/8/28 13:45
@desc:
'''
import requests
import threading
from lxml import etree


# 解析网页，并得到网页中的IP代理
def get_proxy(html):
    selector = etree.HTML(html)
    # print(selector.xpath("//title/text()"))
    proxies = []

    for each in selector.xpath("//tr")[1:]:
        # ip.append(each[0])
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


def thread_write_proxy(proxy):
    with open("./ip_proxy.txt", 'a+') as f:
        print("正在写入：", proxy)
        # 字典不能录入,转换成字符串
        f.write(str(proxy) + '\n')
        print("录入完成！！！")


# 添加线程模式
def thread_test_proxy(proxy):
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
            # normal_proxies.append(proxy)
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
    url = "http://www.xicidaili.com/nn/"
    header = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    }
    response = requests.get(
        url,
        headers=header,
    )
    # print(response.text)
    get_proxy(response.text)


if __name__ == "__main__":
    get_html()
