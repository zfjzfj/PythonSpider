import requests
from bs4 import BeautifulSoup
import pymongo

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
}

base_url = 'http://maoyan.com/board/4?offset='

client = pymongo.MongoClient('localhost', 27017)
db = client['maoyan']
collection = db['TOP100']


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
    dd = soup.select('dd')
    for item in dd:
        yield {
            'name':item.select('.name')[0].get_text(),
            'star':item.select('.star')[0].get_text().strip(),
            'releasetime':item.select('.releasetime')[0].get_text(),
            'score':item.select('.score')[0].get_text()
        }

# 保存至数据库
def saveToDB(item):
    if collection.insert_one(item):
        print("保存成功！")
    else:
        print("保存失败！")

if __name__ == "__main__":
    for i in range(0,100,10):
        for item in parseHTML(getHTML(base_url, i)):
            print(item)
            saveToDB(item)