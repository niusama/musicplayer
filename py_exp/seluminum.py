# #
# # # 导入时间模块
# # import time
# # # 导入webdriver模块
# # from selenium import webdriver
# # # 导入By模块
# # from selenium.webdriver.common.by import By
# # # 实例化浏览器对象
# # driver=webdriver.Edge()
# # # 进行浏览器的自动化
# # driver.get('https://music.163.com/')
# # # 隐式等待10秒钟(如果网页渲染不需要十秒钟就会提前结束)
# # driver.implicitly_wait(10)
# # # 最大化浏览器
# # driver.maximize_window()
# # # 点击登录
# # driver.find_element(By.CSS_SELECTOR,'.link.s-fc3').click()
# # # 强制睡眠2秒钟,有跳转的都需要等待浏览器的渲染,不然浏览器的响应速度跟不上代码的响应的时间(下面的都是一样的道理)
# # time.sleep(2)
# # # 点击其他方式登录
# # driver.find_element(By.CSS_SELECTOR,'div._1a7hecWJ > div > div > div > a').click()
# # time.sleep(2)
# # # 点击同意框
# # driver.find_element(By.CSS_SELECTOR,'#j-official-terms').click()
# # # 点击QQ登录
# # driver.find_element(By.CSS_SELECTOR,'div._3x8w3YCi > ul > li:nth-child(2) > a').click()
# # time.sleep(2)
# # # 获取当前浏览器所有的页面句柄
# # windows = driver.window_handles
# # # print(windows)  查看当前的网页有多少(可能我说的也不正确啊,可以不用管)
# # # 跳转到第二个页面,里面嵌套了网页了,不跳转的话,selenium访问不到
# # driver.switch_to.window(windows[1])
# # # 目标是嵌套元素,使用对应的函数,跳转到嵌套的网页
# # driver.switch_to.frame('ptlogin_iframe')
# # # 点击密码登录
# # driver.find_element(By.CSS_SELECTOR, '#switcher_plogin').click()
# # time.sleep(3)
# # # 获取当前浏览器所有的页面句柄
# # windows = driver.window_handles
# # # 跳转到第二个页面,里面嵌套了网页了,不跳转的话,selenium访问不到
# # driver.switch_to.window(windows[1])
# # # 跳转到第二个页面,里面嵌套了网页了,不跳转的话,selenium访问不到
# # driver.switch_to.frame(0)
# # # 输入你的QQ号
# # driver.find_element(By.CSS_SELECTOR, '#u').send_keys('QQ号')
# # time.sleep(2)
# # # 输入你的密码
# # driver.find_element(By.CSS_SELECTOR, '#p').send_keys('密码')
# # time.sleep(2)
# # # 点击登录
# # driver.find_element(By.CSS_SELECTOR, '#login_button').click()
# # time.sleep(3)
# # # 阻塞一下
# # input()
# # # 退出浏览器
# # driver.quit()
#
#
#
#
#
#
#
# import time
# from selenium import webdriver
# from bs4 import BeautifulSoup
#
# def get_html_src(url):
# # 可以任意选择浏览器,前提是要配置好相关环境，这里选择的是Chrome
#     driver = webdriver.Edge()
#     driver.get(url)
# # 切换成frame
#     #driver.switch_to_frame("g_iframe")
#     driver.switch_to.frame("g_iframe")
# # 休眠3秒,等待加载完成!
#     time.sleep(3)
#     page_src = driver.page_source
#     driver.close()
#     return page_src
#
# def parse_html_page(html):
#     soup = BeautifulSoup(html, 'lxml')
#     items = soup.find_all(attrs={'class':'text'})
#     print(items)
#     return items
#
# def song_id(items):
#     songid = []
#     for item in items:
# #        print('歌曲id:', item.a['href'].replace('/song?id=', ''))
# #        song_name = item.b['title']
# #        print('歌曲名字:', song_name)
#         songid.append(str(item.a['href'].replace('/song?id=', '')))
#     for i in songid :
#         print(i)
#     return songid
#
# def all_song():
#     url = "https://music.163.com/artist?id=" + str(7763)
#     html = get_html_src(url)
#     items = parse_html_page(html)
#     muidtol = song_id(items)
#     return(muidtol)
# all_song()
# time.sleep(300)
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait




#
# import os
# import re
# from os.path import exists
# import jieba
# import matplotlib.pyplot as plt
# import requests
# import xlsxwriter
# from bs4 import BeautifulSoup
# Headers={ "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#                           "Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0 "}
# look='https://www.uump3.com/mp3/77189923'
# response = requests.get(look, headers=Headers)
# html = response.text
# soup = BeautifulSoup(html, "html.parser")
# result=soup.select(".btn btn-primary")
# print(result)

driver = webdriver.Edge()
driver.set_window_position(-2000, -2000)
def seleget(url):

    look = url

    global driver
    #driver.minimize_window()
    driver.set_window_position(-2000, -2000)
    driver.get(look)
    driver.implicitly_wait(1)
    time.sleep(1)
    pre_music = driver.find_elements(By.CLASS_NAME, 'fa fa-download')
    content = driver.page_source
    # pre_music = content.select(".btn btn-primary")
    # print(pre_music)
    # print(type(pre_music))
    # print(pre_music.split(' '))
    # pre_music = str(pre_music)
    # print(type(pre_music))
    # pre_music = pre_music.replace("[<source src=\"", "", 1)
    # pre_music = pre_music.replace("\" type=\"audio/mpeg\"/>]", "", 1)
    content=BeautifulSoup(content, "html.parser")
    html=content.select("a.btn.btn-primary")
    print(html[0].get('href'))
    link=html[0].get('href')
    return link
    driver.quit()

def TT(url):
    look=url.replace("/music","/lkdata/download/?act=music&id=")
    look=look.replace("id=/","id=")
    #look="https://www.uump3.com/lkdata/download/?act=music&id=174774"
    # driver = webdriver.Edge()
    global driver
    driver.set_window_position(-2000, -2000)
    driver.get(look)
    #driver.implicitly_wait(1)
    #time.sleep(1)
    pre_music = driver.find_elements(By.CSS_SELECTOR, 'body > video > source')
    #print(pre_music)
    content = driver.page_source
    content = BeautifulSoup(content, "html.parser")
    html =  content.select("source")
    link=html[0].get('src')
    #print(link)
    driver.quit()
    print("downloadlink=",link)
    return link

def getsource(url):
    link=seleget(url)
    return TT(link)
#getsource("https://www.uump3.com/mp3/77189923")