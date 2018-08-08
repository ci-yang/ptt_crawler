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
			print(content)
	except:
		print("Error!!")
	

	#print(all_content_html)