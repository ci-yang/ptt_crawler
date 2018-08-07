import os
import re
import sys
import json
import time
import requests
import pymysql.cursors
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

PTT_URL = 'https://www.ptt.cc'

def removeSybol(author_name):
	#去除作者的暱稱，去除用()掛號起來的內容
	
	left = author_name.find('\u0028')
	if(left is not -1):
		author_simple_name = author_name[:left]
		return author_simple_name
	else:
		return author_name

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
	result = []
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
			try:
				href = div.find('a')['href']
				link = PTT_URL + href
				article_id = re.sub('\.html', '', href.split('/')[-1])
				ptt_obj = parse(link, article_id, board)
				print('article id: ', article_id)
				#print(ptt_obj)
				result.append(ptt_obj)
			except TypeError:
				print("Article maybe deleted!!")

		time.sleep(0.1)

	print("Done wih all pages")
	return result


def parse(link, article_id, board, timeout=3):
	# 爬取每篇文章的內容
	
	author = ''
	title = ''
	date = ''
	
	print('Processing article: ', article_id)

	isTimeoutError = True			# handdle timeout exception
	while isTimeoutError:
		try:
			resp = requests.get(url=link, cookies={'over18': '1'}, timeout=timeout)
			isTimeoutError = False
		except requests.exceptions.Timeout:
			# Timeout exception
			
			print("retry")

	if resp.status_code != 200:
		print('invalid url:', resp.url)

	soup = BeautifulSoup(resp.text, 'html.parser')
	try:
		main_content = soup.find(id="main-content")
		metas = main_content.select('div.article-metaline')
	except:
		return
	
	isReference = 0
	ref_author_name = ''
	ref_author_ID = ''

	if metas:
		author = metas[0].select('span.article-meta-value')[0].string if metas[0].select('span.article-meta-value')[0] else author
		title = metas[1].select('span.article-meta-value')[0].string if metas[1].select('span.article-meta-value')[0] else title
		date = metas[2].select('span.article-meta-value')[0].string if metas[2].select('span.article-meta-value')[0] else date

		# remove meta nodes
		
		for meta in metas:
			meta.extract()
		for meta in main_content.select('div.article-metaline-right'):
			meta.extract()

	# 做完之後剩下內文跟推文
	# 將內文所有結構存起來
	content_html = main_content

	# remove and keep push nodes
	try:
		pushes = main_content.find_all('div', class_='push')
	except:
		pushes = None

	#IP
	try:
		ip = main_content.find(text=re.compile(u'※ 發信站:'))
		ip = re.search('[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*', ip).group()
	except:
		ip = "None"

	#引述的文章作者
	ref_text = main_content.find(text=re.compile(u'※ 引述'))

	if(ref_text is not None):
		left = ref_text.find('\u300a')
		right = ref_text.find('\u300b')

		if(left and right):
			isReference = 1
			ref_author_name = ref_text[left+1:right]
			ref_author_ID = removeSybol(ref_author_name)
		else:
			ref_author_name = ''
			ref_author_ID = ''
	else:
		ref_text = ""
		isReference = 0

	# push messages
	messages = []
	p, b, n = 0, 0, 0		# push tag, boo tag, arraw tag
	if( pushes ):
		for push in pushes:
			if not push.find('span', 'push-tag'):
				continue
			try:
				push_tag = push.find('span', 'push-tag').string.strip(' \t\n\r')
				push_userid = push.find('span', 'push-userid').string.strip(' \t\n\r')

				# if find is None: find().strings -> list -> ' '.join; else the current way
				push_content = push.find('span', 'push-content').strings
				push_content = ' '.join(push_content)[1:].strip(' \t\n\r')  # remove ':'
				push_ipdatetime = push.find('span', 'push-ipdatetime').string.strip(' \t\n\r')
				messages.append( {'push_tag': push_tag, 'push_userid': push_userid, 'push_content': push_content, 'push_ipdatetime': push_ipdatetime} )
			except:
				pass
			if push_tag == u'推':
				p += 1
			elif push_tag == u'噓':
				b += 1
			else:
				n += 1

	data = {
		"author": author,                       #作者
		"authorID": removeSybol(author),		#去除括弧的作者ID
		"title": title,                         #標題
		"date": date,                           #時間
		"ip": ip,                               #IP
		"article_url": link,                    #文章地址
		"content_html": str(content_html),      #原始內文html結構
		"isReference": isReference,             #使否引述文章
		"ref_text": ref_text,                   #原始引述字串
		"ref_author_ID": ref_author_ID,         #引述的作者ＩＤ
		"ref_author_name": ref_author_name,     #引述的作者ID + 暱稱
		"messages": messages,                   #回文的內容
		"total_messages": p+b+n,                #回文總數
		"push_amount": p,                       #推文數
		"boo_amount": b,                        #噓文數
		"arrow_amount": n                       #箭頭數
	}
	
	return data


if __name__ == "__main__":
	# Enter board name you want to crawler
	try:
		board_input_Name = str(sys.argv[1])
		start = get_latest_page(board_input_Name)
		page = 1
		# page = int(start) - 1			#if you want to crawler all articles of this board

		if(start is not "Null"):
			print("Index numbers: ", int(start)-1)
			data = parse_articles(int(start)-1, page, board_input_Name)
		else:
			data = {
				"status": "error"
			}

		with open(board_input_Name + '-' + str(int(start)-page) + '-' + str(int(start)-1) + '.json', 'w') as outfile:
			json.dump(data, outfile)
	except IndexError:
		print("Please check paramaters.")

