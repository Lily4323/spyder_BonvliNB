import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import random
from time import sleep

# 请求头
header = {
	'Cookie':'bid=UTsYtc9i21Y; douban-fav-remind=1; ll="108288"; _pk_id.100001.4cf6=5b4162575b007e4e.1698648070.; __utmz=223695111.1698648070.1.1.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __yadk_uid=pnE9oLNGBuRt3vc0upTHudiTrJhYvJEf; _vwo_uuid_v2=D1D4592EBBD56A27F8D9F0E23D20B99BF|cc44663736cf5d1a3737ef03f24a6505; dbcl2="275496867:5S3p5dL/XJ4"; push_noty_num=0; push_doumail_num=0; __utmv=30149280.27549; ck=G32V; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1698841008%2C%22https%3A%2F%2Fkkb-production.jupyter-proxy.kaggle.net%2F%22%5D; _pk_ses.100001.4cf6=1; ap_v=0,6.0; __utma=30149280.2108357166.1697710054.1698669281.1698841008.5; __utmc=30149280; __utmz=30149280.1698841008.5.3.utmcsr=kkb-production.jupyter-proxy.kaggle.net|utmccn=(referral)|utmcmd=referral|utmcct=/; __utma=223695111.526866128.1698648070.1698669281.1698841011.4; __utmb=223695111.0.10.1698841011; __utmc=223695111; __utmb=30149280.4.10.1698841008; frodotk_db="403478f4e05410eec09d6adea0fc32ca"',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Host': 'movie.douban.com',
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15',
	'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
	'Referer': 'https://movie.douban.com/subject/35267224/?from=showing',
	'Connection': 'keep-alive'
}

def trans_star(v_str):
	"""转换评论星级"""
	v_str = v_str[0]
	if v_str == 'allstar10':
		return '1星'
	elif v_str == 'allstar20':
		return '2星'
	elif v_str == 'allstar30':
		return '3星'
	elif v_str == 'allstar40':
		return '4星'
	elif v_str == 'allstar50':
		return '5星'
	else:
		return '未知'


def get_shortcontent(v_movie_id):
	"""爬取短评数据"""
	for page in range(1, max_page + 1):  # 爬取前n页
		requests.packages.urllib3.disable_warnings()
		# 请求地址
		url = 'https://movie.douban.com/subject/{}/comments?start={}&limit=20&status=P&sort=new_score'.format(
			v_movie_id, (page - 1) * 20)
		# 发送请求
		response = requests.get(url, headers=header, verify=False)
		print(response.status_code)
		# 解析页面数据
		soup = BeautifulSoup(response.text, 'html.parser')
		# 所有评论数据
		reviews = soup.find_all('div', {'class': 'comment'})
		print('开始爬取第{}页，共{}条评论'.format(page, len(reviews)))
		sleep(random.uniform(1, 2))
		# 定义空列表用于存放数据
		user_name_list = []  # 评论者昵称
		star_list = []  # 评论星级
		time_list = []  # 评论时间
		#ip_list = []  # 评论者ip属地
		vote_list = []  # 有用数
		content_list = []  # 评论内容
		for review in reviews:
			# 评论者昵称
			user_name = review.find('span', {'class': 'comment-info'}).find('a').text
			user_name_list.append(user_name)
			# 评论星级
			star = review.find('span', {'class': 'comment-info'}).find_all('span')[1].get('class')
			star = trans_star(star)
			star_list.append(star)
			# 评论时间
			time2 = review.find('span', {'class': 'comment-time'}).text.strip()
			print('评论时间：', time2)
			time_list.append(time2)
			# 评论者IP属地
			#ip = review.find('span', {'class': 'comment-location'}).text
			#ip_list.append(ip)
			# 有用数
			vote = review.find('span', {'class': 'votes vote-count'}).text
			vote_list.append(vote)
			# 评论内容
			content = review.find('span', {'class': 'short'}).text
			content = content.replace(',', '，').replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '')
			content_list.append(content)
		df = pd.DataFrame(
			{
				'页码': page,
				'评论者昵称': user_name_list,
				'评论星级': star_list,
				'评论时间': time_list,
				#'评论者IP属地': ip_list,
				'有用数': vote_list,
				'评论内容': content_list,
			}
		)
		# 设置csv文件表头
		if os.path.exists(result_file):
			header = False
		else:
			header = True
		# 保存到csv文件
		df.to_csv(result_file, mode='a+', header=header, index=False, encoding='utf_8_sig')
		print('文件保存成功：', result_file)


if __name__ == '__main__':
	# 电影id
	movie_id = '1849031'
	# 最大爬取页
	max_page = 15  # 最大为30页
	# 保存文件名
	result_file = '豆瓣短评_{}_前{}页.csv'.format(movie_id, max_page)
	# 如果csv文件存在，先删除之
	if os.path.exists(result_file):
		os.remove(result_file)
		print('结果文件存在，已删除: {}'.format(result_file))
	# 循环爬取短评
	get_shortcontent(movie_id)
