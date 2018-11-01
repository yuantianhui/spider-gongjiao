import requests
from bs4 import BeautifulSoup
import json,re,os

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
}

def parse_first_page(url):
	r = requests.get(url=url, headers=headers)
	soup = BeautifulSoup(r.text, 'lxml')
	# 得到所有的以数字开头的链接
	number_a_list = soup.select('.bus_kt_r1 > a')
	# 得到所有的以字母开头的链接
	char_a_list = soup.select('.bus_kt_r2 > a')
	all_a_list = number_a_list + char_a_list
	all_href_list = []
	# 得到所有a对象的href属性
	for oa in all_a_list:
		href = url.rstrip('/') + oa['href']
		all_href_list.append(href)
	# print(len(char_a_list))
	return all_href_list

def parse_second_page(url, nchref):
	r = requests.get(url=nchref, headers=headers)
	soup = BeautifulSoup(r.text, 'lxml')
	# 获取所有的以某某开头的链接
	a_list = soup.select('#con_site_1 > a')
	# 获取得到所有的公交链接
	href_list = []
	for oa in a_list:
		href = url.rstrip('/') + oa['href']
		href_list.append(href)
	return href_list

def parse_third_page(href, fp):
	r = requests.get(url=href, headers=headers)
	soup = BeautifulSoup(r.text, 'lxml')
	# 获取线路名称
	route_name = soup.select('.bus_i_t1 > h1')[0].string
	print('正在爬取---%s---......' % route_name)
	# 获取运行时间
	try:
		run_time = soup.select('.bus_i_content > p')[0].string
	except Exception as e:
		run_time = 'unknown'
	# 获取票价信息
	try:
		piao_info = soup.select('.bus_i_content > p')[1].string
	except Exception as e:
		piao_info = 'unknown'
	# 获取公交公司
	try:
		company = soup.select('.bus_i_content > p > a')[0].string
	except Exception as e:
		company = 'unknown'
	# 获取更新时间
	try:
		update_time = soup.select('.bus_i_content > p')[3].string.lstrip('最后更新：')
	except Exception as e:
		update_time = 'unknown'
	# 获取路线长度
	try:
		route_length = soup.select('.bus_label > p')[0].string.strip('全程公里。')
	except Exception as e:
		route_length = 'unknown'
	# 获取上行总站个数
	try:
		up_total = soup.select('.bus_line_top > span')[0].string.strip('共站').strip()
	except Exception as e:
		up_total = 0
	# 获取上行站牌
	up_site_name_list = []
	# 获取得到所有站牌
	all_a_list = soup.select('.bus_line_site > .bus_site_layer > div > a')
	# 获取得到上行所有站牌
	up_a_list = all_a_list[:int(up_total)]
	for oa in up_a_list:
		up_site_name_list.append(oa.string)
		
	try:
		# 获取下行总站个数
		down_total = soup.select('.bus_line_top > span')[1].string.strip('共站').strip()
		# 获取下行站牌
		down_a_list = all_a_list[int(up_total):]
		down_site_name_list = []
		for oa in down_a_list:
			down_site_name_list.append(oa.string)
	except Exception as e:
		down_total = '没有下行'
		down_site_name_list = []
	
	# 将信息保存到字典中
	item = {
		'线路名称': route_name,
		'运行时间': run_time,
		'票价信息': piao_info,
		'公交公司': company,
		'更新时间': update_time,
		'线路长度': route_length,
		'上行站个数': up_total,
		'上行站牌': up_site_name_list,
		'下行站个数': down_total,
		'下行站牌': down_site_name_list,
	}
	string = json.dumps(item, ensure_ascii=False)
	fp.write(string + '\n')
	print('结束爬取---%s---' % route_name)
def parse_allcitys_names():
	url = 'http://js.8684.cn/citys/city_boxInf.min.js'
	r = requests.get(url=url, headers=headers)
	content = r.text
	string = content.split('=')[-1].rstrip(';')
	# 正则提取所有城市拼音
	pattern = re.compile(r'([a-z]+):')
	# print(string)
	ret = pattern.findall(string)
	return ret
	# print(ret)


def main():
	names =parse_allcitys_names()
	for cityname in names:
		print('正在爬取--%s--的全部公交信息' %cityname)
		dir ='E:\python\第四阶段\day6\gongjiao\\'
		fp = open(dir+cityname+'.txt', 'w', encoding='utf8')
		url = 'http://'+cityname+'.8684.cn/'
		# 向一级页面发送请求，得到所有的以数字开头或者字母开头列表
		number_char_href_list = parse_first_page(url)
		# 遍历这个列表，依次向每个url发送请求
		for nchref in number_char_href_list:
			# 向二级页面，发送请求，得到所有的以1 2 3开头的所有公交url
			href_list = parse_second_page(url, nchref)
			# 遍历所有的href_list，依次向每个公交url发送请求，挨个解析
			for href in href_list:
				parse_third_page(href, fp)
		fp.close()
		print('结束爬取--%s--全部公交信息' % cityname)
		# time.sleep(1)


if __name__ == '__main__':
	main()