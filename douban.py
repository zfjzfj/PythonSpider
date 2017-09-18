import requests
from bs4 import BeautifulSoup
import pymongo
import re

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
}

base_url = 'https://movie.douban.com/top250?start='

client = pymongo.MongoClient()
db = client['Movies']
collection = db['DouBanTOP100']


# 获取到网页源码
def getHTML(base_url, offset = 0):
    url = base_url + str(offset)
    try:
        response = requests.get(url,headers=headers)
    except requests.HTTPError as e:
        return None
    else:
        return response.text

# 解析获取到的页面源码
def parseHTML(html):
    soup = BeautifulSoup(html,'lxml')
    dd = soup.select('li .info')
    for item in dd:
        quote = item.select('.quote')[0].get_text().strip() if item.select('.quote') else ''
        name = item.select('.hd .title')[0].get_text().strip()
        star = item.select('.bd p')[0].get_text().strip()
        score = item.select('.star .rating_num')[0].get_text().strip()
        star = re.sub('(\xa0)+?|<br>|(\s){2,}', '', star,re.S)
        yield {
            'name':name,
            'star':star,
            'quote':quote,
            'score':score
        }

# 保存至数据库
def saveToDB(item):
    if collection.insert_one(item):
        print("保存成功！")
    else:
        print("保存失败！")

if __name__ == "__main__":
    for i in range(0,225,25):
        for item in parseHTML(getHTML(base_url, i)):
            print(i//25+1,item)
            saveToDB(item)