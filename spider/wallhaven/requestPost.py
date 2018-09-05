# 爬取wallhaven上的的图片，支持自定义搜索关键词，自动爬取并该关键词下所有图片并存入本地电脑。
import os
import re

import requests
import time
import random
from lxml import etree

keyWord = input("Please input the keywords that you want to download :")


class Spider():
    # 初始化参数
    def __init__(self):
        # headers是请求头，"User-Agent"、"Accept"等字段都是通过谷歌Chrome浏览器查找的！
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36",
        }
        # filePath是自定义的，本次程序运行后创建的文件夹路径，存放各种需要下载的对象。
        self.filePath = ('/小Python程序集合/桌面壁纸/' + keyWord + '/')

    def creat_File(self):
        # 新建本地的文件夹路径，用于存储网页、图片等数据！
        filePath = self.filePath
        if not os.path.exists(filePath):
            os.makedirs(filePath)

    def get_pageNum(self):
        # 用来获取搜索关键词得到的结果总数,用total记录。由于数字是夹在形如：1,985 Wallpapers
        # found for “dog”的string中，
        # 所以需要用个小函数，提取字符串中的数字提取出来并转换成int类型就OK了
        url = ("https://alpha.wallhaven.cc/search?q={}&categories=111&purity=100&sorting="
               "relevance&order=desc").format(keyWord)  # 该页面的搜索地址就是这样的结构可以打开网址看一下
        print('url:', url)
        html = requests.get(url)
        html.encoding = 'utf-8'
        print(html.text)
        selector = etree.HTML(html.text)  # 得到Element对象
        print(selector)
        # 定位到下面的位置得到text()的值,得到的是一个列表
        pageInfo = selector.xpath('//header[@class="listing-header"]/h1[1]/text()')
        print(pageInfo, keyWord)
        # 取出列表的值赋给一个字符串，然后进行拆分，得到搜索出来的结果总数
        # 两种方法：1、拆分 2、利用正则表达式调用sub()函数
        # total = int(str(pageInfo).split()[0][2:])
        total = str(pageInfo)
        total = int(re.sub('\D', '', total))  # 把total不是数字的字符变成''
        print(total)
        return total

    def main_fuction(self):
        # count是总图片数，times是总页面数
        self.creat_File()
        count = self.get_pageNum()
        print("We have found:{} images!".format(count))
        if count % 24 == 0:
            times = int(count / 24)
        else:
            times = int(count / 24 + 1)
        j = 1
        for i in range(times):
            pic_Urls = self.getLinks(i + 1)
            for item in pic_Urls:
                self.download(item, j)
                j += 1

    def getLinks(self, number):
        # 此函数可以获取给定number的页面中所有图片的链接，用List形式返回
        url = (
            "https://alpha.wallhaven.cc/search?q={}&categories=111&purity=100&sorting="
            "relevance&order=desc&page={}").format(keyWord, number)
        try:
            html = requests.get(url)
            selector = etree.HTML(html.text)
            # @class  /元素
            pic_Linklist = selector.xpath('//section[@class="thumb-listing-page"]/ul/li/figure/img/@data-src')
            # 图片的路径列表
            print(pic_Linklist)
        except Exception as e:
            print(repr(e))
        return pic_Linklist

    def download(self, url, count):
        # 此函数用于图片下载。其中参数url形如：https://alpha.wallhaven.cc/wallpapers/thumb/small/th-582943.jpg
        # xpath定位到图片的src
        pic_path = (self.filePath + keyWord + str(count) + '.jpg')  # 把照片存为jpg格式
        try:
            pic = requests.get(url, headers=self.headers)
            with open(pic_path, 'wb') as img:
                # 二进制的形式存入图片（文件）;提取文本就用text
                img.write(pic.content)
            print("Image:{} has been downloaded!".format(count))
            time.sleep(random.uniform(0, 2))
        except Exception as e:
            print(repr(e))


spider = Spider()
spider.main_fuction()
