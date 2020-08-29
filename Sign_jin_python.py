#!/usr/bin/env python
# -*- coding: gb2312 -*-
#
#
#  2.py
#  
#  Copyright 2020 天琼懵 <天琼懵@DESKTOP-03B3450>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import sys
import requests
import json
import yaml
#import oss2
#from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
#from urllib3.exceptions import InsecureRequestWarning


# 获取当前utc时间，并格式化为北京时间
def getTimeStr():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")
    
# 输出调试信息，并及时刷新缓冲区
def log(content):
    print(getTimeStr() + ' ' + str(content))
    sys.stdout.flush()

# debug模式
debug = False
if debug:
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

apies={}
apies['login-url']='https://authserver.hactcm.edu.cn/authserver/login?service=https%3A%2F%2Fhactcm.cpdaily.com%2Fportal%2Flogin'
#apis['host']=

def getSession(loginUrl):
	params = {
		'login_url': loginUrl,
		# 保证学工号和密码正确下面两项就不需要配置
		'needcaptcha_url': '',
		'captcha_url': '',
		'username': '2018181003',
		'password': '306810'
		}
	cookies = {}
	# 借助上一个项目开放出来的登陆API，模拟登陆
	res = requests.post('http://www.zimo.wiki:8080/wisedu-unified-login-api-v1.0/api/login', params, verify=not debug)
	print(res)
	cookieStr = str(res.json()['cookies'])
	log(cookieStr)
	if cookieStr == 'None':
		log(res.json())
		return None
# 解析cookie
	for line in cookieStr.split(';'):
		name, value = line.strip().split('=', 1)
		cookies[name] = value
	session = requests.session()
	session.cookies = requests.utils.cookiejar_from_dict(cookies)
	return session

#表单登陆，需要修改
def queryForm(session, apis):
	host ='hactcm.cpdaily.com' 
	headers = {
		'Accept': 'application/json, text/plain, */*',
		'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 yiban/8.1.11 cpdaily/8.1.11 wisedu/8.1.11',
		'content-type': 'application/json',
		'Accept-Encoding': 'gzip,deflate',
		'Accept-Language': 'zh-CN,en-US;q=0.8',
		'Content-Type': 'application/json;charset=UTF-8'
		}
	queryCollectWidUrl = 'https://{host}/wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList'.format(host=host)
	params = {
		'pageSize': 6,
		'pageNumber': 1
		}
	if 'hactcm' in host:
		session.get("https://authserver.hactcm.edu.cn/authserver/login?service=https%3A%2F%2Fhactcm.cpdaily.com%2Fportal%2Flogin")
	res = session.post(queryCollectWidUrl, headers=headers, data=json.dumps(params), verify=not debug)
	log("res.json 前")
	log(session)
	print(res.json())
	if len(res.json()['datas']['rows']) < 1:
		return ("查询失败123")
	
	collectWid = res.json()['datas']['rows'][0]['wid']
	formWid = res.json()['datas']['rows'][0]['formWid']
	
	detailCollector = 'https://{host}/wec-counselor-collector-apps/stu/collector/detailCollector'.format(host=host)
	res = session.post(url=detailCollector, headers=headers,data=json.dumps({"collectorWid": collectWid}), verify=not debug)
	schoolTaskWid = res.json()['datas']['collector']['schoolTaskWid']
	
	getFormFields = 'https://{host}/wec-counselor-collector-apps/stu/collector/getFormFields'.format(host=host)
	res = session.post(url=getFormFields, headers=headers, data=json.dumps({"pageSize": 100, "pageNumber": 1, "formWid": formWid, "collectorWid": collectWid}), verify=not debug)
	
	form = res.json()['datas']['rows']
	return {'collectWid': collectWid, 'formWid': formWid, 'schoolTaskWid': schoolTaskWid, 'form': form}


#begin

log('当前用户：'+'first' )
apis=apies
log('脚本开始执行。。。')
log('开始模拟登陆。。。')
session = getSession(apis['login-url'])
log(session)
if session != None:
	log('模拟登陆成功。。。')
	log('正在查询最新待填写问卷。。。')
	params = queryForm(session, apis)
	print(params)
