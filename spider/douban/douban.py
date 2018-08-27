#!/usr/bin/env python
# encoding: utf-8
'''
@author: bwcheng
@time: 2018/8/23 16:48
@desc:
'''

# 首次登陆需要输入账号、密码、验证码，登陆成功保存cookie到本地文件。
# 有cookie登陆直接读取本地cookie
import requests
from PIL import Image
import pickle
from lxml import etree

url = 'https://www.douban.com/'
login_url = 'https://www.douban.com/login'
data = {'source': 'index_nav',
        'captcha-solution': '',
        'form_email': 'bwcheng001@163.com',
        'form_password': 'wawxf1314cheng',
        'captcha-id': ''
        }

headers = {'Host': 'www.douban.com',
           'Referer': 'https://www.douban.com/',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
           'Accept-Encoding': 'gzip, deflate, br'}

Session = requests.session()
# Session是否保存有cookies，有机保存到Session.cookies
try:
    with open('cookie.txt', 'rb') as f:
        Session.cookies = pickle.load(f)
        # 这里我将读到的cookies输出
        print(Session.cookies, headers)
        flag = True
# 如果没有cookie，就读入用户输入
except:
    # 直接在data写死了省的测试的时候一直输入账号、密码
    # data['form_email'] = input('Please input your account:')
    # data['form_password'] = input('Please input your password:')
    flag = False


# 获取登录页面的验证码
def get_captcha():
    # 这里不要用requests.get(),因为会重新打开一个会话
    res = Session.get(login_url)
    selector = etree.HTML(res.text)
    # 得到图片路径
    imgSrc = selector.xpath('//img[@id="captcha_image"]/@src')[0]
    # 字符串类型   find()方法得到索引的位置
    index_start = imgSrc.find('=')
    index_end = imgSrc.find('&')
    captcha_id = imgSrc[index_start + 1: index_end]
    # 抓取图片并保存
    imgRes = requests.get(imgSrc, headers=headers)
    if imgRes.status_code == 200:
        print(imgRes.status_code)
        with open('captcha.jpg', 'wb')as f:
            f.write(imgRes.content)

    image = Image.open('captcha.jpg')
    image.show()
    captcha_solution = input('请输入验证码:')
    return captcha_solution, captcha_id
# 登陆
def login():
    if flag:
        res = Session.get(url, headers=headers)
        print(res.status_code)
    else:
        captcha_solution, captcha_id = get_captcha()
        data['captcha-solution'] = captcha_solution
        data['captcha-id'] = captcha_id
        res = Session.post(login_url, data=data, headers=headers)
        print(data)
        print(res.status_code)
        with open('dump.txt', 'wb')as f:
            pickle.dump(Session.cookies, f)
    selector = etree.HTML(res.text)
    loginName = selector.xpath('//li[@class="nav-user-account"]/a/span/text()')
    print(loginName)
if __name__ == '__main__':
    login()
