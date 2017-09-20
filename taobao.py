import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymongo

chrome = webdriver.Chrome()
wait = WebDriverWait(chrome, 10)
conn = pymongo.MongoClient()
db = conn['taobao']
collection = db['meishi']


def search_keyword(keyword="美食"):
    try:
        chrome.get('https://www.taobao.com/')
        inputbox = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#q')))
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_TSearchForm > div.search-button > button')))
        inputbox.clear()
        inputbox.send_keys(keyword)
        button.click()

        totalPages = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total'))).text
        totalPages = re.search('(\d+)', totalPages).group(1)
        return totalPages

    except TimeoutException:
        return search_keyword(keyword)

def next_page(page_number):
    try:
        inputbox = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        inputbox.clear()
        inputbox.send_keys(page_number)
        button.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number)))
    except TimeoutException:
        next_page(page_number)

def parse_page():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items')))
    html = chrome.page_source
    soup = BeautifulSoup(html, 'lxml')
    items = soup.select('#mainsrp-itemlist .items .item')
    for item in items:
        product = {
            'name':item.select('.title')[0].get_text().strip(),
            'price':item.select('.g_price-highlight > strong')[0].get_text(),
            'deal-cnt':item.select('.deal-cnt')[0].get_text(),
            'shop':item.select('.shop')[0].get_text().strip(),
            'location':item.select('.location')[0].get_text()
        }
        print(product)
        save_to_DB(product)

def save_to_DB(item):
    if (collection.insert(item)):
        print('保存成功！')
    else:
        print("保存失败！")

def main():
    total = int(search_keyword())
    for i in range(2, total + 1):
        next_page(i)
        parse_page()

if __name__ == "__main__":
    main()

