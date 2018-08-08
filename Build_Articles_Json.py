import os
import re
import bs4
import sys
import json
import time
import requests
import pymysql.cursors
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

pushes_list = []

def getJSON(filename):
	# get JSON file
	with open(filename) as f:
		jsonStructure = json.load(f)

	return jsonStructure

#Judge the Push is response by author or user
def getMessageList(content_list):
	message_list = []
	content_string = ""
	for c in content_list:
		if(type(c) == bs4.element.Tag and c.find('span', 'push-tag')):
			if(content_string != ""):
				message_list.append(content_string)
				content_string = ""
				message_list.append(c)
			else:
				message_list.append(c)
		else:
			if(c.string):
				content_string = content_string + c.string
		if(content_list.index(c) == len(content_list)-1 and content_string is not ""):
			message_list.append(content_string)
	return message_list

#回傳內文以及推文的串列
def get_content_and_pushes(content_html):
	try:
		soup = BeautifulSoup(content_html, "lxml")
		main_content = soup.find(id="main-content")
		try:
			f2 = main_content.select(".f2") #去除有星號的字串 ex: *發信帖
			for f in f2:
				f.extract()
		except:
			pass
		try:
			f6 = main_content.select(".f6") #去除引述的文章內容
			for f in f6:
				f.extract()
		except:
			pass

		#print(main_content)
		content_list = main_content.contents
		message_list = getMessageList(content_list)

		if message_list:
			content = message_list
		else:
			content = ""
	except:
		content = ""

	return content


def creating_floors(message_list, article):
    p, b, n = 0, 0, 0
    floor = 0
    messages = []
    for push in message_list:
        if( type(push) == bs4.element.Tag and push.find('span', 'push-tag') ):
            push_tag = push.find('span', 'push-tag').string.strip(' \t\n\r')
            push_userid = push.find('span', 'push-userid').string.strip(' \t\n\r')
            push_content = push.find('span', 'push-content').strings
            push_content = ' '.join(push_content)[1:].strip(' \t\n\r')  # remove ':'
            push_ipdatetime = push.find('span', 'push-ipdatetime').string.strip(' \t\n\r')
            response_tag = "使用者回文"
            response_type = 1
            #messages.append( {'push_tag': push_tag, 'push_userid': push_userid, 'push_content': push_content, 'push_ipdatetime': push_ipdatetime, "回文類型": "使用者回文", "floor": floor} )
            if push_tag == u'推':
                push_type = 1
                p += 1
            elif push_tag == u'噓':
                push_type = 0
                b += 1
            else:
                push_type = 2
                n += 1
            
        else:
            #messages.append({'push_tag': "", 'push_userid': article["authorID"], 'push_content': push, 'push_ipdatetime': "", "回文類型": "作者回應", "floor": floor})
            push_tag = ""
            push_type = 3  #作者回文
            push_userid = article["authorID"]
            push_content = push
            push_ipdatetime = ""
            response_tag = "作者回應"
            response_type = 0
            
        
        data = {
            "tag": push_tag,
            "tag_type": push_type,
            "uID": push_userid,
            "content": push_content,
            "date": push_ipdatetime,
            "type_label": response_tag,
            "type": response_type,
            "floor": floor,
        }
        
        #messages.append(data)
        if( floor ):
            pushes_list.append(data)
        
        floor+=1

if __name__ == "__main__":
	# 讀取 crawler.py 生出來的 JSON 做資料清理及建立文章資料表
	# step1: load JSON
	try:
		filename = str(sys.argv[1])
	except IndexError:
		print("Please enter arguments!!")
		sys.exit()

	try:
		all_content_html = getJSON(filename)
	except FileNotFoundError:
		print("Wrong filename!")
		sys.exit()

	try:
		for article in all_content_html:
			content = get_content_and_pushes(article['content_html'])
			creating_floors(content, article)
		print(pushes_list)
	except:
		print("Error!!")
	

	#print(all_content_html)