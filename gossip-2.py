#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  2 13:51:26 2024

@author: chuntamy
"""
import requests
from bs4 import BeautifulSoup
import json
import datetime



# cookie
url = "https://www.ptt.cc/bbs/Gossiping/index.html"
payload = {
    'from': '/bbs/Gossiping/index.html',
    'yes': 'yes' 
}
data = []   #全部文章的資料
num = 0

rs = requests.session() #session紀錄cookie
response = rs.post("https://www.ptt.cc/ask/over18", data=payload)


for i in range(2): #爬取兩頁
    response = rs.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # print(soup.prettify()) #結構樹

    links = soup.find_all("div", class_="title") #找出每篇文章的連結
    for link in links:
        #如果文章已被刪除，連結為None
        if link.a != None:
            article_data = {}   # 單篇文章的資料放入{}
            page_url = "https://www.ptt.cc/"+link.a["href"]

            # 進入文章頁面
            response = rs.get(page_url)
            result = BeautifulSoup(response.text, "html.parser")
            # print(soup.prettify())

            # 找出作者、標題、時間、留言
            main_content = result.find("div", id="main-content")
            article_info = main_content.find_all("span", class_="article-meta-value")
            author = article_info[0].string
            title = article_info[2].string  
            time = article_info[3].string   
        
            article_data["author"] = author
            article_data["title"] = title
            article_data["time"] = time

            # 貼文內容
            all_text = main_content.text.split() #以--切割，抓最後一個--前的所有內容
            print(all_text)
            article_data["content"] = all_text

            #所有留言
            comment_dic = {} 
            push_dic = []
            arrow_dic = []
            shu_dic = []
            
            comments = main_content.find_all("div", class_="push")
            for comment in comments:
                push_tag = comment.find("span", class_="push-tag").string  #分類標籤
                push_userid = comment.find("span", class_="push-userid").string  #ID
                push_content = comment.find("span", class_="push-content").string   #留言內容
                push_time = comment.find("span", class_="push-ipdatetime").string   #留言時間
                #print(push_tag, push_userid, push_content, push_time)

                dict1 = {"push_userid": push_userid,
                         "push_content": push_content, "push_time": push_time}
                if push_tag == "推 ":
                    push_dic.append(dict1)
                if push_tag == "→ ":
                    arrow_dic.append(dict1)
                if push_tag == "噓 ":
                    shu_dic.append(dict1)

            # print(push_dic)
            # print(arrow_dic)
            # print(shu_dic)
            # print("--------")

            comment_dic["推"] = push_dic
            comment_dic["→"] = arrow_dic
            comment_dic["噓"] = shu_dic
            article_data["comment"] = comment_dic

            #print(article_data)
            data.append(article_data)
            num += 1
            print("第 "+str(num)+" 篇文章完成!")
            
            now = datetime.datetime.now()
            file_name=f"第"+str([num])+" 篇文章.txt"
            with open(file_name,"w") as f:
                json.dump(article_data, f, indent=2,
                  sort_keys=True, ensure_ascii=False)
            print(article_data.columns)
    # 找到上頁的網址，並更新url
    url = "https://www.ptt.cc/"+soup.select_one("a").get("href")
#['title']['time']['author']['content']['comment']
