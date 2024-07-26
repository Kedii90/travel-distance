# coding: utf-8
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from lxml import etree
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from queue import Queue
from selenium.webdriver.common.action_chains import ActionChains
from concurrent.futures import ThreadPoolExecutor
import csv

class DesTin:
    def __init__(self):
        opt = Options()
        opt.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(executable_path='chromedriver-win64/chromedriver.exe', chrome_options=opt)

    def main(self,place, user, passwd):
        self.driver.get(
            'https://travelsearch.fliggy.com/index.htm?spm=181.61408.a1z7d.5.650e5e9elrqZHf&searchType=product&keyword=' + place + '&category=SCENIC')
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        ActionChains(self.driver).move_to_element(self.driver.find_element_by_id('fm-login-id')).click().send_keys(user).perform()
        ActionChains(self.driver).move_to_element(self.driver.find_element_by_id('fm-login-password')).click().send_keys(
            passwd).perform()
        # action = ActionChains(driver)
        # action.click_and_hold(driver.find_element_by_xpath("//div[@id='nc_1__scale_text']/span")).perform()
        # time.sleep(2)
        # action.move_by_offset(379,0)
        # time.sleep(1)
        # action.release().perform()
        # time.sleep(10)
        # ActionChains(driver).click_and_hold(driver.find_element_by_xpath('//*[@id="nc_1_n1z"]')).move_by_offset(xoffset=360,yoffset=0).perform()
        # time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="login-form"]/div[6]/button').click()
        time.sleep(10)
        # driver.switch_to_window(driver.window_handles[0])
        # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'active-icon'))
        )
        self.driver.switch_to_window(self.driver.window_handles[0])
        self.driver.refresh()
        res = etree.HTML(self.driver.page_source)
        div1 = res.xpath('//*[@id="content"]/div[5]//div[@class="page-num-content"]')
        page, a, ls = 0, 0, 0
        q = Queue()
        for i in div1:
            ls = i.xpath('./a/text()')
        #print(ls)
        a = int(ls[-2])
        #print(a)
        for i in range(a):
            time.sleep(0.5)
            self.driver.switch_to_window(self.driver.window_handles[0])
            res = etree.HTML(self.driver.page_source)
            div = res.xpath('//*[@id="content"]/div[5]/div[1]/div[1]/div')
            place_url, place_name = 0, 0
            for div_li in div:
                place_url = div_li.xpath('.//div[@class="product-left"]/a/@href')
                place_name = div_li.xpath('.//h3[@class="main-title"]/div/text()')
            q.put((place_name, place_url))
            #print(place_name,place_url)
            if i < a - 1:
                time.sleep(0.5)
                ActionChains(self.driver).move_to_element(self.driver.find_element_by_class_name('page-next')).click().perform()
                # print(driver.current_url)
        self.driver.quit()
        with ThreadPoolExecutor(10) as task:
            while not q.empty():
                task.submit(self.write, q.get())
        DesTin.deal_detail(self)
    def deal_detail(self):
        text = pd.read_csv('./place.csv',names=['name','url'],encoding='utf-8')
        count= 0
        for s in text['name']:
            if s.startswith('['):
                text.drop([count], inplace=True)
            count += 1
        text = text.reset_index(drop=True)
        text.to_csv('./place.csv',index=False)

    def write(self,message):
        place_name,place_url=message
        with open('./place.csv', 'a', encoding='utf-8', newline='') as f:
            writer_ = csv.writer(f)
            for i in range(len(place_url)):
                writer_.writerows([(place_name[i], place_url[i])])






