import csv
import pandas as pd
import time
import requests
from lxml import etree
import re
from selenium import webdriver
from trip.fliggy.destination import DesTin
from trip.fliggy.sound_assist import Speak_assist,Audio,ws_start,text


#时间戳处理
ks = time.time()
ksts = '%s_%s' %(int(ks*1000),str(ks)[-3:])
header = {
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}

class BuyDetail:
    def __init__(self):
        self.driver = webdriver.PhantomJS(executable_path='phantomjs-2.1.1-windows/bin/phantomjs.exe')

    def main_(self,spot_):
        pd.set_option('max_colwidth', 1000)
        text = pd.read_csv('./place.csv', header=0)
        pos = 0
        for s in text['name']:
            if spot_ == s:
                break
            pos += 1
        url = str(text.loc[[pos], ['url']])
        return url

    def select_(self, url, productname, ticketkindname):
        res = requests.get('http://s.alitrip.com/scenic/item.htm?', headers=header,
                           params={
                               '_ksTS': ksts,
                               'callback': 'jsonp' + str(int(ksts[-3:]) + 1),
                               'format': 'json',
                               'sid': re.findall(r'=(\d+)', str(url), re.S)[0],
                               'ticketkindname': ticketkindname,
                               'productname': productname,
                               'jumpto': '1',
                               '_input_charset': 'utf-8'
                           })
        res = res.text.strip()
        return res

    def select_one(self,res):
        page_all = re.findall(r'"feedNum":(\d+)', res, re.S)
        numid = re.findall(r'"itemid":(.*?),', res, re.S)
        s = BuyDetail.s_all(self,res)
        for num, id in enumerate(numid):
            for i in range(0, int(page_all[num]) // 6 + 1):
                details = requests.get('http://s.alitrip.com/scenic/ajax/ticketFeed.htm?', headers={
                    'User-Agent':
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
                }, params={
                    '_ksTS': ksts,
                    'callback': 'jsonp' + str(int(ksts[-3:]) + 1),
                    'format': 'json',
                    'aucNumId': id,
                    'pagesize': '6',
                    'jumpto': str(i + 1),
                    '_input_charset': 'utf-8'
                })
                detail = re.findall(r'"raterUserNick":"(.*?)".*?:"(.*?)"', details.text, re.S)
                BuyDetail.writer_file(self,detail, num, s)
                df = pd.read_csv('./detail.csv', names=['user', 'evaluate', 'score', 'sell_shop', 'price'])
                df.drop_duplicates(inplace=True)
                df.to_csv('./detail.csv', index=False)

    def writer_file(self,text, num, s):
        if not text:
            with open('./detail.csv', 'a', encoding='utf-8') as f:
                wr = csv.writer(f)
                wr.writerows([('none', 'none') + s[num]])
        with open('./detail.csv', 'a', encoding='utf-8', newline='') as f:
            wr = csv.writer(f)
            for line in text:
                wr.writerows([line + s[num]])

    def s_all(self,res):
        return re.findall(r'"sellerScore":"(\d.*?)".*?:"(.*?)".*?:"(.*?)"', res, re.S)

    def items(self,url):
        self.driver.get(url)
        res = etree.HTML(self.driver.page_source)
        wrap = res.xpath('//*[@id="J_TicketListWrap"]')
        print("项目类型",end=':')
        for item in wrap:
            print(item.xpath('./li/div[1]/div[1]/span/text()'),end=' ')
        div=res.xpath('//*[@id="list"]/div[1]/div')
        print('\n'"票的类型",end=':')
        for type in div:
            print(type.xpath('./p/text()'),end = ' ')
        print()
        self.driver.quit()









sound=Speak_assist()
audio = Audio()
#place=input('请输入目的地：')
sound.run('请说出目的地')
print('请说出目的地',end = ':')
audio.Start('output.wav','out_change.pcm')
time.sleep(1)
ws_start('out_change.pcm')
place = text[0]
print(place)
text.clear()
# user = input('请输入账号：')
# passwd=input('请输入密码：')
audio1 = Audio()
sound.run('请说出账号')
print('请说出账号',end = ':')
audio1.Start('output1.wav','out_change1.pcm')
time.sleep(1)
ws_start('out_change1.pcm')
user = text[0]
print(user)
text.clear()
audio2 = Audio()
sound.run('请说出密码')
print('请说出密码',end = ':')
audio2.Start('output2.wav','out_change2.pcm')
time.sleep(1)
ws_start('out_change2.pcm')
passwd = text[0]
print(passwd)
text.clear()
#实例化对象
des=DesTin()
des.main(place=place, user=user, passwd=passwd)
spot_=input('请输入景点(place.csv):')
# audio1 = Audio()
# sound.run('请说出景点')
# print('请说出景点(place.csv)',end = ':')
# audio1.Start('output3.wav','out_change3.pcm')
# time.sleep(3)
# ws_start('out_change3.pcm')
# spot_ = text[0]
# print(spot_)
# text.clear()
buy = BuyDetail()
url=buy.main_(spot_)
buy.items(re.findall(r'https.*', str(url), re.S)[0])
productname=input('项目类型：')
# audio2 = Audio()
# sound.run('项目类型选择：')
# print('项目类型选择',end = ':')
# audio2.Start('output4.wav','out_change4.pcm')
# time.sleep(1)
# ws_start('out_change4.pcm')
# productname = text[0]
# print(productname)
ticketkindname=input('票的类型：')
# audio3 = Audio()
# sound.run('票的类型')
# print('票的类型',end = ':')
# audio3.Start('output5.wav','out_change5.pcm')
# time.sleep(1)
# ws_start('out_change5.pcm')
# ticketkindname = text[0]
# print(ticketkindname)
# text.clear()
res=buy.select_(url,productname,ticketkindname)
buy.select_one(res)




