import requests
from bs4 import BeautifulSoup
import pymongo
import json

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
}

base_url = 'https://www.toutiao.com/search_content/'

client = pymongo.MongoClient()
db = client['Movies']
collection = db['MaoYanTOP100']


# 获取到网页源码
def getJSON(base_url, offset=0, keyword='街拍'):
    query = {
        'offset': str(offset),
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1'
    }
    try:
        response = requests.get(base_url,headers=headers,params=query)
    except requests.HTTPError as e:
        return None
    else:
        return json.loads(response.text)

# 解析获取到的页面源码
def parseJSON(json):
    data = json.get('data')
    for item in data:
        yield {
            'media_name':item.get('media_name'),
            'image_detail':item.get('image_detail')
        }

# 获取图片地址
def getPIC(item):
    if item.get('media_name'):
        return {
            'name':item.get('media_name'),
            'picture':[i.get('url_list') for i in item.get('image_detail')]
        }

if __name__ == "__main__":
    for i in parseJSON(getJSON(base_url)):
        print(getPIC(i))