from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from pyquery import PyQuery as pc
from config import *
import pymongo

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]



browser = webdriver.Chrome()
wait = WebDriverWait(browser,20)

def search():
    browser.get('https://www.taobao.com')
    _input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#q'))
    )
    submit = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button'))
    )
    _input.send_keys('meishi')
    submit.click()
    total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total')))
    get_products()
    return total.text

def next_page(page_num):
    _input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input'))
    )
    submit = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit'))
    )
    _input.clear()
    _input.send_keys(page_num)
    submit.click()
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_num)))
    get_products()

def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    html = browser.page_source
    doc = pc(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image' : item.find('.pic .img').attr('src'),
            'price' : item.find('.price').text(),
            'deal' : item.find('.deal-cnt').text()[:-3],
            'title' : item.find('.title').text(),
            'shop' : item.find('.shopname').text(),
            'location' : item.find('.location').text()
        }
        save_to_mongo(product)
        print(product)
        print('\n')

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('succeed')

def main():
    total = search()
    res = re.compile('\d+')
    total = int(res.search(total).group())
    #total = (re.compile('(\d+)').search(total).group(1))
    #print(total)
    for i in range(2, 3 + 1):
        next_page(i)

if __name__ =='__main__':
    main()
