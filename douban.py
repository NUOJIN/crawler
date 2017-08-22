#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 10:42:25 2017

@author: nokicheng
"""

#抓取数据
from urllib import request##爬取已上映电影
resp = request.urlopen('http://movie.douban.com/nowplaying/nanjing/')
html_data = resp.read().decode('utf-8')

from bs4 import BeautifulSoup as bs##分析html数据
soup = bs(html_data,'html.parser')
nowplaying_movie = soup.find_all('div',id='nowplaying')
nowplaying_movie_list = nowplaying_movie[0].find_all('li',class_='list-item')
nowplaying_list = []
for item in nowplaying_movie_list:
    nowplaying_dict = {}
    nowplaying_dict['id'] = item['data-subject']
    for tag_img_item in item.find_all('img'):
        nowplaying_dict['name'] = tag_img_item['alt']
        nowplaying_list.append(nowplaying_dict)
        
eachCommentList = []
for start in range(20):
    requrl = 'http://movie.douban.com/subject/'+nowplaying_list[9]['id']+'/comments?start='+str(start)+'&limit=20'
    resp = request.urlopen(requrl)
    html_data = resp.read().decode('utf-8')
    soup = bs(html_data,'html.parser')
    comment_div_list = soup.find_all('div',class_='comment')
    for item in comment_div_list:
        if item.find_all('p')[0].string is not None:
            eachCommentList.append(item.find_all('p')[0].string)
        
#清洗数据
comments = ""
for k in range(len(eachCommentList)):
    comments = comments + (str(eachCommentList[k])).strip()
import re ##去除标点
pat = re.compile(r'[\u4e00-\u9fa5]+')
filterdata = re.findall(pat,comments)
cleaned_comments = ''.join(filterdata) 

import jieba
import pandas as pd
segment = jieba.lcut(cleaned_comments)
words_df = pd.DataFrame({'segment':segment})##消除停用词
stopwords = pd.read_csv('stopwords.txt',index_col=False,quoting=3,sep='\t',names=['stopword'],encoding='utf-8')
words_df = words_df[~words_df.segment.isin(stopwords.stopword)]

#词频统计
import numpy as np
words_stat = words_df.groupby(by=['segment'])['segment'].agg({'计数':np.size})
words_stat = words_stat.reset_index().sort_values(by=["计数"],ascending=False)

#制作词云
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['figure.figsize'] = (10.0,5.0)
from wordcloud import WordCloud
wordcloud = WordCloud(font_path='STHeiti Medium.ttc',background_color='white',max_font_size=80)
word_frequence = {x[0]:x[1]for x in words_stat.head(1000).values}
word_frequence_list = []
for key in word_frequence:
    temp = (key,word_frequence[key])
    word_frequence_list.append(temp)

wordcloud = wordcloud.fit_words(word_frequence)
plt.imshow(wordcloud)
plt.axis('off')
plt.savefig('/Users/nokicheng/desktop/wolf_warrior.png')