# coding: utf-8
import re
import time
from lxml import etree
from trip.fliggy.spot import BuyDetail,spot_,productname,ticketkindname
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from trip.fliggy.sound_assist import Speak_assist
from trip.fliggy.sound_assist import Audio,ws_start,text


class Buy_Ticket:
    def __init__(self):
        opt = Options()
        opt.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(executable_path='chromedriver-win64/chromedriver.exe', chrome_options=opt)
        self.bd=BuyDetail()
    def main__(self,shop):
        url = self.bd.main_(spot_)
        res =self.bd.s_all(res=self.bd.select_(url=url,productname=productname,ticketkindname=ticketkindname))
        pos = 0
        for i in res:
           if shop in i:
               break
           pos+=1
        self.driver.get(re.findall(r'https.*', str(url), re.S)[0])
        time.sleep(10)
        action=ActionChains(self.driver)
        action.move_to_element(self.driver.find_elements_by_class_name('ticket-name')[0]).click().perform()
        time.sleep(1)
        self.driver.find_elements_by_class_name('jump-ticket-detail')[pos].click()
        self.driver.switch_to_window(self.driver.window_handles[1])
        time.sleep(10)
        # ActionChains(self.driver).move_to_element(self.driver.find_element_by_id('fm-login-id')).click().send_keys(user).perform()
        # ActionChains(self.driver).move_to_element(self.driver.find_element_by_id('fm-login-password')).click().send_keys(
        #     passwd).perform()
        # ActionChains(self.driver).move_to_element(self.driver.find_element_by_xpath('//*[@id="login-form"]/div[6]/button')).click().perform()
        # time.sleep(10)
        #门票种类点击
        #因为每个票种类挺多的，排列的规律不好弄，所以下面这种写法也只针对一部分的点击操作
        # source=etree.HTML(self.driver.page_source)
        # dd=source.xpath('//*[@id="content"]/div[3]/div[2]/div[7]/dl//dd')
        # dl = source.xpath('//*[@id="content"]/div[3]/div[2]/div[7]/dl')
        # dl_pos, ul_pos, count = 1, 1, 1
        # array = list()
        # eles = self.driver.find_elements_by_xpath('//*[@class="item-prop-val"]')
        # for ele in eles:
        #     res = ele.get_attribute('innerHTML')
        #     array.append(re.findall(r'<span class="prop-text">(.*?)<', res, re.S))
        # for index, i in enumerate(array):
        #     if ticketkindname in i:
        #         dl_pos = index
        #         ul_pos = i.index(ticketkindname) + 1
        # for d in dl:
        #     if d.xpath('./dd[' + str(dl_pos) + ']/ul/li[' + str(ul_pos) + ']//span//text()')[0] == 'ticketkindname':
        #         self.driver.find_element_by_xpath('//*[@id="content"]/div[3]/div[2]/div[7]/dl[' + str(count) + ']/dd[' + str(
        #             dl_pos) + ']/ul/li[' + str(ul_pos) + ']').click()
        #         break
        #     count += 1
        #旅游选项自己在页面自己点击 有100秒时间留给你
        time.sleep(100)
        self.driver.quit()



if __name__ == '__main__':
    # sound = Speak_assist()
    # audio4=Audio()
    sell_shop=input('请选择购买的商家(detail.csv):')
    # sound.run('请说要购买的商家')
    # print("请说要购买的商家",end = ':')
    # audio4.Start('output6.wav','out_change1.pcm')
    # time.sleep(1)
    # ws_start('out_change6.pcm')
    # sell_shop = text[0]
    # print(sell_shop)
    b_t = Buy_Ticket()
    b_t.main__(shop=sell_shop)
