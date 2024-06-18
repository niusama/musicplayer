# # imself=Noneests
# # import execjs
# # import json
# # f = open('music163.js', encoding='utf-8').read()
# # js_code = execjs.compile(f)
# # def geturl(id):
# #     i4m = {"ids":"[2051548110]","br":128000,"csrf_token":""}
# #     res = js_code.call('get_post_data', i4m)
# #     print(res)
# #     headers = {
# #         "authority": "music.163.com",
# #         "accept": "*/*",
# #         "accept-language": "zh-CN,zh;q=0.9",
# #         "cache-control": "no-cache",
# #         "content-type": "application/x-www-form-urlencoded",
# #         "origin": "https://music.163.com",
# #         "pragma": "no-cache",
# #         "referer": "https://music.163.com/outchain/player?type=2&id="+id+"&auto=1&height=66&bg=e8e8e8",
# #         "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
# #         "sec-ch-ua-mobile": "?0",
# #         "sec-ch-ua-platform": "\"Windows\"",
# #         "sec-fetch-dest": "empty",
# #         "sec-fetch-mode": "cors",
# #         "sec-fetch-site": "same-origin",
# #         "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
# #     }
# #     cookies = {}
# #     url = "https://music.163.com/weapi/song/enhance/player/url"
# #     data = {
# #         "params": res['encText'],
# #         "encSecKey": res['encSecKey']
# #     }
# #     response = requests.post(url, headers=headers, data=data)
# #     dic=json.loads(response.text)
# #     print(response.text)
# #     print(dic["data"][0]['url'])
# #     return dic["data"][0]['url']
# # #geturl("2051548110")
# # # 文章不理解，我还专门录制了视频进行详细讲解，都放在这个扣裙了 708525271
# import os
# import re
# from os.path import exists
# import jieba
# import matplotlib.pyplot as plt
# import requests
# import xlsxwriter
# from PyQt5 import QtCore, QtWidgets
# import qtawesome
# from PyQt5.QtCore import QUrl
# from PyQt5.QtGui import QPalette, QBrush, QPixmap, QFont
# from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
# from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QFrame, QVBoxLayout, QLineEdit, QPushButton
# from bs4 import BeautifulSoup
# from wordcloud import WordCloud
# import SQL
# import json
# from selenium import webdriver
#
# from py_exp.seluminum import getsource
# # Headers={ "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
# #                           "Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0 "}
# # link="https://www.uump3.com/mp3/7295977"
# #
# # html = requests.get(link, headers=Headers)
# # soup = BeautifulSoup(html.text, 'html.parser')
# # result = soup.select("div.content-lrc.mt-1")
# # print(result)

from PyQt5 import QtCore, QtWidgets

from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QFrame, QVBoxLayout, QLineEdit, QPushButton

import threading

import time
import UI

# Process_barTRD_Sign = 0
# def waitsituation(self):
#         num=0
#         while 1 == 1:
#             num+=1
#             global Process_barTRD_Sign
#             print("threadnum=",num,Process_barTRD_Sign)
#             if Process_barTRD_Sign == 1:
#                 print("oh,yres")
#                 self.process_bar.setRange(0, 101)
#                 for i in range(0, 100):
#                     self.process_bar.setValue(i)
#                     time.sleep(5)
#             time.sleep(0.01)
# updatethread=threading.Thread(target=waitsituation, args=(UI.MainUi(QtWidgets.QMainWindow, QDialog) ,int ,))


