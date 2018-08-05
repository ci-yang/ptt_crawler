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

def parse_articles(start, page, board, timeout=3):
	# 給定page數量從最新的頁面開始爬取
	# 爬的是個版頁面底下的所有文章標題
	print('Starting '+ board + ' ...')

	if(start == "Null"):
		return
	print(int(start), page)

	for i in range(int(start), int(start)-int(page), -1):
		index = i
		print('Processing index:', str(index))
		isTimeoutError = True			# handdle timeout exception
		while isTimeoutError:
			try:
				resp = requests.get(
					url = PTT_URL + '/bbs/' + board + '/index' + str(index) + '.html',
					cookies={'over18': '1'}, timeout=3
				)
				isTimeoutError = False
			except requests.exceptions.Timeout:
				# Timeout exception
				
				print("retry")
		if resp.status_code != 200:
			print('invalid url:', resp.url)
			continue
		soup = BeautifulSoup(resp.text, 'html.parser')
		divs = soup.find_all("div", "r-ent")

		for div in divs:
			href = div.find('a')['href']
			link = PTT_URL + href
			article_id = re.sub('\.html', '', href.split('/')[-1])
			#ptt_obj = parse(link, article_id, board)
			print('article id: ', article_id)

		time.sleep(0.1)

	print("Done wih all pages")


if __name__ == "__main__":
	# Enter board name you want to crawler
	board_input_Name = str(sys.argv[1])
	start = get_latest_page(board_input_Name)
	page = 1

	print("Index numbers: ", start)
	parse_articles(start, page, board_input_Name)

