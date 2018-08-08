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

	print(all_content_html)