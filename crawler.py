import os
import re
import sys
import json
import time
import requests
import pandas as pd
import pymysql.cursors
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

PTT_URL = 'https://www.ptt.cc'

def get_latest_page(boardName):
	# get the latest page number of specific board
	 
	isTimeoutError = True			# handdle timeout exception
	while isTimeoutError:
		try:
			resp = requests.get(
				url = PTT_URL + '/bbs/' + boardName + '/index' + '.html',
				cookies={'over18': '1'}, timeout=3
			)
			isTimeoutError = False
		except requests.exceptions.Timeout:
			# Timeout exception
			
			print("retry")

	soup = BeautifulSoup(resp.text, 'html.parser')
	divs = soup.find_all("div", "btn-group-paging")

	try:
		# 找到上一頁的按鈕
		
		index_link = soup.find_all(text=re.compile("上"))[0].parent.get('href')
		pattern = re.compile(r"[0-9]+")
		index = pattern.search(index_link).group(0)

		# 最新的頁面通常不足一頁，因此先不要從最新的開始撈
		# index =  int(index) + 1          #最新的頁面
		
	except IndexError:
		index = "Null"

	return index

if __name__ == "__main__":
	# Enter board name you want to crawler
	board_input_Name = str(sys.argv[1])

	print("Index numbers: ", get_latest_page(board_input_Name))

