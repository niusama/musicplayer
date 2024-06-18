import os
import re
from os.path import exists
import jieba
import matplotlib.pyplot as plt
import requests
import xlsxwriter
from PyQt5 import QtCore, QtWidgets
import qtawesome
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPalette, QBrush, QPixmap, QFont
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QFrame, QVBoxLayout, QLineEdit, QPushButton
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import SQL
import json
from selenium import webdriver

#from py_exp.seluminum import get_html_src, parse_html_page


#弹窗提示
def pop_prompt(title, str):
    msg_box = QMessageBox(QMessageBox.Warning, title, str)
    msg_box.exec_()

class MainUi(QtWidgets.QMainWindow, QDialog):

    def __init__(self, username):
        #登录界面
        super().__init__()

        self.username = username
        self.player = QMediaPlayer(self)
        self.playing = False
        self.play_index_now = -1
        self.Headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0 "
        }

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.start()
        self.timer.timeout.connect(self.check_music_status)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(960, 700)
        self.setWindowTitle('Music')

        # 创建窗口主部件
        self.main_widget, self.main_layout = self.build_widget()
        # 创建左侧部件
        self.left_widget, self.left_layout = self.build_widget('left_widget')
        # 创建右侧部件
        self.right_widget, self.right_layout = self.build_widget('right_widget')

        self.setCentralWidget(self.main_widget)  # 设置窗口主部件
        self.main_layout.addWidget(self.left_widget, 0, 0, 12, 2)  # 左侧部件在第0行第0列
        self.main_layout.addWidget(self.right_widget, 0, 2, 12, 10)  # 右侧部件在第0行第3列

        self.build_button(self.left_layout, 1, 0, 1, 3, text="每日推荐", name='left_label')
        self.build_button(self.left_layout, 4, 0, 1, 3, text="我的音乐", name='left_label')

        self.build_button(self.left_layout, 2, 0, 1, 3, self.pop_songs, "热门歌曲", 'left_button')
        self.build_button(self.left_layout, 3, 0, 1, 3, self.pop_singers, "热门歌手", 'left_button')
        self.build_button(self.left_layout, 5, 0, 1, 3, self.get_downloads, "我的下载", 'left_button')
        self.build_button(self.left_layout, 6, 0, 1, 3, self.get_collections, "我的收藏", 'left_button')
        self.build_button(self.left_layout, 7, 0, 1, 3, self.change_account, "切换账号", 'left_button')

        # 右侧顶部搜索框部件
        self.right_bar_widget, self.right_bar_layout = self.build_widget()
        #图标
        self.search_icon = QtWidgets.QLabel(chr(0xf002) + ' ' + '搜索  ')
        self.search_icon.setFont(qtawesome.font('fa', 20))
        #输入框
        self.search_label = QtWidgets.QLineEdit()
        self.search_label.setPlaceholderText("输入歌手、歌曲或用户，回车进行搜索")
        self.search_label.returnPressed.connect(
            lambda: self.search(self.search_label.text()))

        self.right_bar_layout.addWidget(self.search_icon, 0, 0, 1, 1)
        self.right_bar_layout.addWidget(self.search_label, 0, 1, 1, 8)
        self.right_layout.addWidget(self.right_bar_widget, 0, 0, 1, 9)

        self.search_result = QtWidgets.QLabel("搜索结果")
        self.search_result.setObjectName('right_label')
        self.right_layout.addWidget(self.search_result, 2, 0, 1, 5)

        self.operator_label = QtWidgets.QLabel("执行操作")
        self.operator_label.setObjectName('right_label')
        self.right_layout.addWidget(self.operator_label, 2, 5, 1, 3)

        # 搜索歌曲部件
        self.result_widget, self.result_layout = self.build_widget()

        self.result_button = [
            self.build_button(self.result_layout, 0, 1, event=lambda: self.play_music(0)),
            self.build_button(self.result_layout, 1, 1, event=lambda: self.play_music(1)),
            self.build_button(self.result_layout, 2, 1, event=lambda: self.play_music(2)),
            self.build_button(self.result_layout, 3, 1, event=lambda: self.play_music(3)),
            self.build_button(self.result_layout, 4, 1, event=lambda: self.play_music(4)),
            self.build_button(self.result_layout, 5, 1, event=lambda: self.play_music(5)),
            self.build_button(self.result_layout, 6, 1, event=lambda: self.play_music(6)),
            self.build_button(self.result_layout, 7, 1, event=lambda: self.play_music(7)),
            self.build_button(self.result_layout, 8, 1, event=lambda: self.play_music(8)),
            self.build_button(self.result_layout, 9, 1, event=lambda: self.play_music(9)),
        ]
        # self.search("陈奕迅")

        # 播放歌单部件
        self.operator_widget, self.operator_layout = self.build_widget('')

        self.build_tool_button("导出所有歌曲信息", self.operator_layout, 0, 0, self.export_songs_details,
                                               'fa.list', 'red', QtCore.QSize(50, 50), 3),
        self.build_tool_button("导出所有歌曲歌词", self.operator_layout, 0, 1, self.export_songs_lyric,
                                               'fa.file-text-o', 'red', QtCore.QSize(50, 50), 3),
        self.build_tool_button("下载当前播放歌曲", self.operator_layout, 1, 0, self.download,
                                                   'fa.download', 'red', QtCore.QSize(50, 50), 3),
        self.build_tool_button("收藏当前播放歌曲", self.operator_layout, 1, 1, self.collect,
                                                   'fa.heart', 'red', QtCore.QSize(50, 50), 3),
        self.build_tool_button("生成所有歌词词云", self.operator_layout, 2, 0, self.lyric_cloud,
                                                   'fa.cloud', 'red', QtCore.QSize(50, 50), 3),
        self.build_tool_button("热门歌手歌曲占比", self.operator_layout, 2, 1, self.hot_singer_song,
                                                    'fa.pie-chart', 'red', QtCore.QSize(50, 50), 3)

        self.right_layout.addWidget(self.result_widget, 3, 0, 1, 5)
        self.right_layout.addWidget(self.operator_widget, 3, 5, 1, 3)

        self.process_bar = QtWidgets.QProgressBar()  # 播放进度部件
        self.process_value = 0
        self.process_bar.setValue(self.process_value)
        self.process_bar.setFixedHeight(3)  # 设置进度条高度
        self.process_bar.setTextVisible(False)  # 不显示进度条文字

        # 播放控制部件
        self.console_widget, self.console_layout = self.build_widget()
        self.console_button_1 = self.build_button(self.console_layout, 0, 0, event=self.pre_music,
                                                  icon=qtawesome.icon('fa.backward', color='red'))
        self.console_button_2 = self.build_button(self.console_layout, 0, 2, event=self.next_music,
                                                  icon=qtawesome.icon('fa.forward', color='red'))
        self.console_button_3 = self.build_button(self.console_layout, 0, 1, event=self.play_music_by_button,
                                                   icon=qtawesome.icon('fa.play', color='red', font=18), icon_size=QtCore.QSize(30, 30))

        self.console_layout.setAlignment(QtCore.Qt.AlignCenter)  # 设置布局内部件居中显示
        self.right_layout.addWidget(self.process_bar, 9, 0, 1, 9)
        self.right_layout.addWidget(self.console_widget, 10, 0, 1, 9)

        self.main_layout.setSpacing(0)  # 设置内部控件间距

        self.left_widget.setStyleSheet('''
            QPushButton{border:none;color:white;}
            QPushButton#left_label{
                border:none;
                border-bottom:1px solid white;
                font-size:18px;
                font-weight:700;
            }
            QPushButton#left_button:hover{border-left:4px solid red;font-weight:700;}
            QWidget#left_widget{
                background:gray;
                border-top:1px solid white;
                border-bottom:1px solid white;
                border-left:1px solid white;
                border-top-left-radius:10px;
                border-bottom-left-radius:10px;
            }''')

        self.search_label.setStyleSheet(
            '''QLineEdit{
                border:1px solid gray;
                width:300px;
                border-radius:10px;
                padding:8px 4px;
        }''')

        self.right_widget.setStyleSheet('''
            QWidget#right_widget{
                color:#232C51;
                background:white;
                border-top:1px solid darkGray;
                border-bottom:1px solid darkGray;
                border-right:1px solid darkGray;
                border-top-right-radius:10px;
                border-bottom-right-radius:10px;
            }
            QLabel#right_label{
                border:none;
                font-size:20px;
                font-weight:700;

                text-align:center
            }
        ''')

        self.operator_widget.setStyleSheet(
            '''
                QToolButton{border:none; margin-left:15px}
                QToolButton:hover{border-bottom:2px solid #F76677;}
            ''')

        self.result_widget.setStyleSheet('''
            QPushButton{
                border:none;
                color:gray;
                font-size:18px;
                height:36px;
                padding-left:5px;
                padding-right:10px;
                text-align:left;
            }
            QPushButton:hover{
                color:black;
                border:1px solid #F3F3F5;
                border-radius:10px;
                background:LightGray;
            }
        ''')

        self.process_bar.setStyleSheet('''
            QProgressBar::chunk {
                background-color: red;
            }
        ''')

        self.console_widget.setStyleSheet('''
            QPushButton{
                border:none;
            }
        ''')

    #爬虫✔
    def search(self, keyword):
        self.keyword = keyword
        self.resultlist = []
        self.play_index_now = -1  # 每次重新搜索都将当前播放序号设置为-1
        self.num = 0
        baseurl = "https://www.uump3.com/index.php/so?key=" # 搜索基础地址
        Url = baseurl + keyword                             # 拼接成目标地址
        response = requests.get(Url, headers=self.Headers) #使用request访问网页
        html = response.text
        soup = BeautifulSoup(html, "html.parser")         # 是同beautifulsoup解析
        self.tags = soup.select(".text-primary")          #使用select 筛选目标标签

        for i in self.tags:
                look=i['href']
                look.replace("mp3","lkdata/download/?act=music&id=")
                pre_music=look
                if pre_music:
                    self.resultlist.append([i.text, pre_music])# 保存
                    self.num+=1
                    print(i.text, pre_music)
        self.song_show() #搜索结果栏展示

    #列表展示✔
    def song_show(self):  # 呈现"歌手-歌名"的形式
        for i in range(self.num):
            self.result_button[i].setText(self.resultlist[i][0])
            if i>8:
                return
    
    #进度条进程百分比更新✔
    def process_timer_status(self):  # 进度条进程百分比更新
        try:
            if self.playing is True:
                self.process_value += (100 / (self.duration / 1000))
                # print("当前进度：", self.process_value)
                self.process_bar.setValue(self.process_value)
        except Exception as e:
            print(repr(e))

    #自动播放✔
    def check_music_status(self):  # 播放结束则自动播放下一首
        player_status = self.player.mediaStatus()
        player_duration = self.player.duration()

        if player_status == 7:
            if not self.play_index_now >= self.num-1:
                self.next_music()

        if player_duration > 0:
            self.duration = player_duration

    #选择歌曲✔
    def play_music(self, num):  # 播放歌曲
        if num >= self.num:
            pop_prompt('温馨提示', '暂无该曲目')
            return
        self.process_value = 0
        self.play_index_now = num
        self.playing = True
        self.console_button_3.setIcon(qtawesome.icon('fa.stop', color='red', font=18))
        self.player.setMedia(QMediaContent(QUrl(self.resultlist[num][1])))
        self.player.setVolume(50)
        self.player.play()
        self.duration = self.player.duration()  # 音乐的时长

        self.process_timer = QtCore.QTimer()
        self.process_timer.setInterval(1000)
        self.process_timer.start()
        self.process_timer.timeout.connect(self.process_timer_status)

    #暂停-开始按钮✔
    def play_music_by_button(self):  # 播放按钮设置
        #未选择歌曲，默认播放第一首
        if self.play_index_now == -1:
            if self.playing is False:
                self.process_value = 0
                self.play_music(0)
                self.console_button_3.setIcon(qtawesome.icon('fa.stop', color='red', font=18))
                
        #已选择歌曲
        elif self.playing is False:
            self.playing = True
            self.console_button_3.setIcon(qtawesome.icon('fa.stop', color='red', font=18))
            self.player.play()
        else:
            self.playing = False
            self.console_button_3.setIcon(qtawesome.icon('fa.play', color='red', font=18))
            self.player.pause()

    #前一首✔
    def pre_music(self):  # 播放前一首
        if self.play_index_now <= 0:
            pop_prompt('温馨提示', '已经是第一首了~')
        else:
            self.play_music(self.play_index_now - 1)
    
    #后一首✔
    def next_music(self):  # 播放后一首
        if self.play_index_now >= self.num-1:
            pop_prompt('温馨提示', '已经是最后一首了~')
        else:
            self.play_music(self.play_index_now + 1)
    
    #获取歌曲信息✔
    def export_songs_details(self):
        result = r'https://www.8lrc.com'
        row = 0
        if not exists('./songsdetails/'):
            os.makedirs('./songsdetails/')
        workbook = xlsxwriter.Workbook('./songsdetails/'+self.keyword+'.xlsx')
        worksheet = workbook.add_worksheet('music')
        worksheet.write_row(row, 0, ['歌名', '歌曲url', '歌曲资源地址'])
        for i in self.resultlist:
            worksheet.write_row(row+1, 0, [i[0], result+self.tags[row]['href'], i[1]])
            row += 1
        workbook.close()
        if os.path.exists('./songsdetails/'+self.keyword+'.xlsx'):
            os.startfile('.\\songsdetails\\'+self.keyword+'.xlsx')
        else:
            pop_prompt('提示', '出了点小问题~')

    #获取歌词✔
    def export_songs_lyric(self):
        result = r'https://www.8lrc.com'
        pattern = r'"lrc":"(.*)","link"'
        num = 0
        if not exists('./lyric/'+self.keyword):
            os.makedirs('./lyric/'+self.keyword)
        for tag in self.tags[0:self.num]:
            html = requests.get(result + tag['href'], headers=self.Headers)
            soup = BeautifulSoup(html.text, 'html.parser')
            if soup.text.__contains__("404"): continue
            script = soup.select("body script")[3].get_text()
            lyric = re.search(pattern, script)
            if lyric:
                lyric = re.search(pattern, script).group(1)
                lyric = lyric.replace(r'\r\n', '\n')
                with open("lyric/"+self.keyword+'/'+self.resultlist[num][0]+'.txt', 'w+', -1, 'utf-8') as fp:
                    fp.write(lyric)
                    fp.close()
            else:
                print(self.resultlist[num][0]+":None")
            num += 1
        pop_prompt('提示', '导出成功')
        os.startfile(".\\lyric\\"+self.keyword)

    #下载歌曲✔
    def download(self):
        if self.play_index_now == -1: # 无播放歌曲
            pop_prompt('温馨提示', '当前暂无播放歌曲')
            return
        # 获取MP3下载连接中保存的MP3数据
        response = requests.get(self.resultlist[self.play_index_now][1], headers=self.Headers)
        # 保存歌曲
        filename = QFileDialog.getSaveFileName(self, '下载文件', '.', '音乐文件(*.MP3)')
        if filename[0] != '':
            sql = 'insert into downloads values("%s","%s", "%s")' % (
            self.username, self.resultlist[self.play_index_now][0], self.resultlist[self.play_index_now][1])
            #连接数据库，执行sql语句
            conn, cur = SQL.connect(sql)
            if conn:
                pop_prompt('温馨提示', '下载成功')
                cur.close()
                conn.close()
            else:
                pop_prompt('错误提示', '下载出错')
            #写入MP3数据到文件中
            with open(filename[0], 'wb') as m:
                m.write(response.content)

    #收藏歌曲✔
    def collect(self):
        if self.play_index_now == -1:
            pop_prompt('温馨提示', '当前暂无播放歌曲')
            return

        sql = ('insert into collection values("%s","%s", "%s")' %
               (self.username, self.resultlist[self.play_index_now][0], self.resultlist[self.play_index_now][1]))
        conn, cur = SQL.connect(sql)
        if conn:
            pop_prompt('提示', '收藏成功')
            cur.close()
            conn.close()
        else:
            pop_prompt('温馨提示', '收藏出错')

    # 词云✔
    def lyric_cloud(self):
        result = r'https://www.8lrc.com'  # 设置基础目标地址
        pattern = r'"lrc":"(.*)","link"'  # 设置正则表达式
        lyric = ""  # 先设置为空串
        for tag in self.tags[0:self.num]:
            html = requests.get(result + tag['href'], headers=self.Headers)
            # 使用tag中的后半段地址和基础地址拼成目标地址 并且设置请求头防止被网站卡 返回请求状态和封装代码信息
            soup = BeautifulSoup(html.text, 'html.parser')  # 使用'html.parser 解析html代码
            if soup.text.__contains__("404"): continue  # 处理一下404 找不到网页的错误
            script = soup.select("body script")[3].get_text()  # 使用select从被解析过的代码中筛选我们需要的body script的标签的第三个元素的文字信息
            pre_lyric = re.search(pattern, script)  # 从开头使用正则表达式筛选树文字中我们需要的信息
            if pre_lyric:
                lyric = lyric + pre_lyric.group(1)  # 拼出我们需要的串
        text = re.findall('[\u4e00-\u9fa5]+', lyric, re.S)  # 提取中文
        text = " ".join(text)  # 拼起来
        word = jieba.cut(text, cut_all=True)  # 分词
        new_word = []
        for i in word:
            if len(i) >= 2:
                new_word.append(i)  # 只添加长度大于2的词
        final_text = " ".join(new_word)  # 拼起来
        #去除中文停用词
        stopwords_path = 'cn_stopwords.txt'
        with open(stopwords_path, 'r', encoding='utf-8') as f:
            stop_words = [line.strip() for line in f.readlines()]

        word_cloud = WordCloud(background_color="white", width=800, height=600, max_words=100, max_font_size=80,
                               contour_width=1, contour_color='lightblue', stopwords=stop_words,
                               font_path="C:/Windows/Fonts/simfang.ttf").generate(final_text)  # 参数信息自己顾名思义

        word_cloud.to_file(self.keyword + '词云.png')  # 保存慈云图片文件
        os.startfile(self.keyword + '词云.png')  # 打开图片文件 

    #热门歌手饼图✔
    def hot_singer_song(self):
        url = 'https://www.9ku.com/geshou/all-all-liuxing.htm'
        base = 'https://www.9ku.com'
        singers_url = []
        songs_num = []
        proportion = []
        name = []
        all_num = 0
        html = requests.get(url, headers=self.Headers)
        soup = BeautifulSoup(html.text, 'html.parser')
        singers_body = soup.findAll(class_='t-i')
        for singer in singers_body[:10]:
            singers_url.append(base + singer['href'])
        for singer_url in singers_url:
            html = requests.get(singer_url, headers=self.Headers)
            soup = BeautifulSoup(html.text, 'html.parser')
            name.append(soup.find(class_="t-t clearfix").h1.text)
            songs = soup.findAll(class_="songNameA")
            songs_num.append(len(songs))
            all_num += len(songs)
        for i in songs_num:
            proportion.append(i/all_num)
        explode = [0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        plt.figure(figsize=(6, 9))  # 设置图形大小宽高
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文乱码问题
        plt.axes(aspect=1)  # 设置图形是圆的
        plt.pie(x=proportion, labels=name, explode=explode, autopct='%3.1f %%',
                shadow=True, labeldistance=1.2, startangle=0, pctdistance=0.8)
        plt.title("热门歌手歌曲量占比")
        plt.savefig("热门歌手歌曲量占比饼图.jpg")
        os.startfile("热门歌手歌曲量占比饼图.jpg")

    # 歌排名✔
    def pop_songs(self):
        row = 0
        base = 'http://m.yue365.com/'
        url = 'http://m.yue365.com/bang/box100_w.shtml'
        pattern = r'width:(.*)%'
        self.songs = []
        html = requests.get(url, headers=self.Headers)
        html.encoding = 'gb2312'
        soup = BeautifulSoup(html.text, 'lxml')
        songs = soup.findAll(class_='name')
        hot = soup.findAll('span', class_='dib')
        workbook = xlsxwriter.Workbook('popsongs.xlsx')
        first_format = workbook.add_format({'align': 'center'})
        second_format = workbook.add_format({'align': 'left'})
        worksheet = workbook.add_worksheet('pop500')
        worksheet.set_column(0, 0, 6)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 46)
        worksheet.set_column(3, 3, 10)
        worksheet.write_row(row, 0, ['排名', '歌名', '歌曲url'], first_format)
        for song in songs:
            self.songs.append(song.a.text)
            row += 1
            song_url = base + song.a['href']
            worksheet.write_row(row, 0, [row, song.a.text, song_url], second_format)
        workbook.close()
        os.startfile('popsongs.xlsx')

    # 歌手排名✔
    def pop_singers(self):
        url = 'https://www.9ku.com/geshou/all-all-liuxing.htm'
        base = 'https://www.9ku.com'
        self.singers_url = []
        html = requests.get(url, headers=self.Headers)
        soup = BeautifulSoup(html.text, 'html.parser')
        singers_body = soup.findAll(class_='t-i')
        for singer in singers_body[:50]:
            self.singers_url.append(base + singer['href'])
        workbook = xlsxwriter.Workbook('popsingers.xlsx')
        url_base = 'https://www.9ku.com'
        pop_prompt('温馨提示', '数据量较大，请耐心等待！')
        for singer_url in self.singers_url:
            html = requests.get(singer_url, headers=self.Headers)
            soup = BeautifulSoup(html.text, 'html.parser')
            if soup.find(class_="t-t clearfix") is None:
                continue
            name = soup.find(class_="t-t clearfix").h1.text
            worksheet = workbook.add_worksheet(name)
            worksheet.write_row(0, 0, ['歌名', '歌曲url', '歌词url'])
            worksheet.set_column(0, 0, 20)
            worksheet.set_column(1, 2, 40)
            songs = soup.findAll(class_="songNameA")
            lyrics = soup.findAll(class_="chi")
            row = 1
            for song in songs[:-18]:
                worksheet.write_row(row, 0,
                                    [song.text, url_base + song['href'], url_base + lyrics[row - 1]['href']])
                row += 1
        workbook.close()
        os.startfile('popsingers.xlsx')

    #查看收藏✔
    def get_collections(self):
        sql = 'select * from collection where user="%s"' % (self.username)
        conn, cur =SQL.connect(sql)
        if conn is None:
            pop_prompt('错误提示', '系统错误')
            return
        
        row = 0
        collections = cur.fetchall()
        cur.close()
        conn.close()
        workbook = xlsxwriter.Workbook(self.username+'\'s collections.xlsx')
        worksheet = workbook.add_worksheet('music')
        worksheet.write_row(row, 0, ['歌曲', '歌曲资源地址'])
        for collect in collections:
            row += 1
            worksheet.write_row(row, 0, [collect[1], collect[2]])
        workbook.close()
        os.startfile(self.username+'\'s collections.xlsx')

    #查看下载✔
    def get_downloads(self):
        sql = 'select * from downloads where user="%s"' % (self.username)
        conn, cur = SQL.connect(sql)
        if conn is None:
            pop_prompt('错误提示', '系统错误')
            return

        row = 0
        collections = cur.fetchall()
        cur.close()
        conn.close()
        workbook = xlsxwriter.Workbook(self.username + '\'s downloads.xlsx')
        worksheet = workbook.add_worksheet('music')
        worksheet.write_row(row, 0, ['歌曲', '歌曲资源地址'])
        for collect in collections:
            row += 1
            worksheet.write_row(row, 0, [collect[1], collect[2]])
        workbook.close()
        os.startfile(self.username + '\'s downloads.xlsx')

    #切换用户✔
    def change_account(self):
        self.playing = False #判断是否正在播放
        self.console_button_3.setIcon(qtawesome.icon('fa.play', color='red', font=18)) #调整播放按钮
        self.player.pause()#暂停播放
        self.close() # 关闭当前窗口
        dialog = LoginDialog() # 船舰登录窗口
        if dialog.exec_() == QDialog.Accepted: #判断是否登录成功
            gui = MainUi(dialog.get_username())  #创建播放器窗口
            gui.show()# 展示

    # 创建部件✔
    def build_widget(self, name=''):
        widget = QtWidgets.QWidget()
        if name:
            widget.setObjectName(name)
        layout = QtWidgets.QGridLayout()  # 创建部件的网格布局
        widget.setLayout(layout)  # 设置部件布局为网格布局
        return widget, layout

    # 创建按钮✔
    def build_button(self, layout, frow=0, fcol=0, rows=0, cols=0, event=None, text='', name='',
                     icon=None, icon_size=None):
        #button=None
        if icon:
            button = QtWidgets.QPushButton(icon, text)
        else:
            button = QtWidgets.QPushButton(text)
        if name:
            button.setObjectName(name)
        if event:
            button.clicked.connect(event)
        if icon_size:
            button.setIconSize(icon_size)
        if rows:
            layout.addWidget(button, frow, fcol, rows, cols)
        else:
            layout.addWidget(button, frow, fcol)
        return button

    #创建工具按钮✔
    def build_tool_button(self, text, layout, frow, fcol, event=None, icon_name='', icon_color='', icon_size=None, style=0):
        button = QtWidgets.QToolButton()
        button.setText(text)
        if event:
            button.clicked.connect(event)
        if icon_name:
            button.setIcon(qtawesome.icon(icon_name, color=icon_color))
        if icon_size:
            button.setIconSize(icon_size)

        button.setToolButtonStyle(style)
        layout.addWidget(button, frow, fcol)
        return button


class LoginDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFixedSize(960, 700)
        self.setWindowTitle('登录')

        #设置窗口背景
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap('1.jpg')))
        self.setPalette(palette)

        # 设置界面控件
        self.frame = QFrame(self)
        self.frame.move(260, 110)
        self.mainLayout = QVBoxLayout(self.frame)

        #设置输入框
        self.edit_name = self.set_inputbox("username")
        self.edit_pwd = self.set_inputbox("password")

        #设置按钮
        self.set_button("Login")
        self.set_button("Register")

        #设置控件间距
        self.mainLayout.setSpacing(60)

    #登录
    def login(self, event):  # 登录
        username = self.edit_name.text()
        password = self.edit_pwd.text()
        if username == "" or password == "":
            pop_prompt('温馨提示', '请输入用户名或密码')
            return

        sql = 'select * from user where username="%s"' % (username)
        conn, cur = SQL.connect(sql)
        if conn is None:
            pop_prompt('错误提示', '系统错误')
            return

        user = cur.fetchone()
        cur.close()
        conn.close()
        #登陆成功
        if username == user[0] and password == user[1]:
            pop_prompt('恭喜', '登陆成功')
            self.username = username
            self.accept()
        #用户名或者密码错误
        else:
            pop_prompt('错误提示', '用户名或者密码错误')
            self.edit_name.setText("")
            self.edit_pwd.setText("")
            return

    #注册
    def register(self, event):  # 注册
        username = self.edit_name.text()
        password = self.edit_pwd.text()
        #用户名或密码为空
        if username == "" or password == "":
            pop_prompt('温馨提示', '用户名或密码不能为空')
            return
        #用户名或密码过长
        if len(username) > 10 or len(password) > 16:
            pop_prompt('温馨提示', '用户名或密码过长')
            return

        sql = 'insert into user values("%s","%s")' % (username, password)
        conn, cur = SQL.connect(sql)
        if conn is None:
            pop_prompt('温馨提示', '用户名已经存在')
        else:
            pop_prompt('恭喜', '注册成功')
            cur.close()
            conn.close()

        self.edit_name.setText("")
        self.edit_pwd.setText("")

        # 设置控件透明度

    #设置输入框
    def set_inputbox(self, text):
        # 设置输入框
        edit = QLineEdit(self)  # 创建输入框
        edit.setPlaceholderText(text)  # 设置默认文字
        edit.setFont(QFont('微软雅黑', 22))  # 设置字体和大小
        if text == "password":
            edit.setEchoMode(QLineEdit.Password)
        self.mainLayout.addWidget(edit)  # 将部件加入布局
        return edit

    #设置按钮
    def set_button(self, text):
        btn = QPushButton(text)  # 按钮值设置Login
        btn.setFont(QFont('Microsoft YaHei', 22))  # 设置字体和大小
        self.mainLayout.addWidget(btn)  # 将部件加入布局

        # 绑定按钮事件
        if text == "Login":
            btn.clicked.connect(self.login)
        elif text == "Register":
            btn.clicked.connect(self.register)
        # return self.btn

    def get_username(self):
        return self.username
