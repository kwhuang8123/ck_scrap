# -*- coding: utf-8 -*-
"""0520Goldfish.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14pBqd_Pui4No_2cXF7bmV5ybMxLSC6mF
"""

# from google.colab import drive
# drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/My Drive/mtginvestment/ck

# Commented out IPython magic to ensure Python compatibility.
# %ls

# !apt-get update
# !apt install chromium-chromedriver
# !cp /usr/lib/chromium-browser/chromedriver /usr/bin
# !pip install selenium
# !pip install fake_useragent

from service.ck2gf import ck2gf
from service.goldfish  import goldfish
from bs4 import BeautifulSoup
from matplotlib.pyplot import table
from csv import reader
from multiprocessing import Pool
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from operator import itemgetter, attrgetter
import requests
import bs4
import re
import ast
import time
import random
import pandas as pd
import threading
import queue
import csv
import os

class Worker(threading.Thread):
  def __init__(self, queue):
    threading.Thread.__init__(self)
    self.queue = queue

  def run(self):
    while self.queue.qsize() > 0:
      # 取得新的資料

        arg = self.queue.get(timeout=15)


        ck.get_price(cardkingdom, arg)

class ck():
  def __init__(self):
      super().__init__()
      self.original = []
      self.raw_list = []  #[name, 未處理setname, ck_price]
      self.main_list = [] #[name, 處理好的setname, ck_price]
      self.result_list = []#[name, setname, ck_price, gf_price, rate]
      self.tmp_list = []
      self.None_list = []
      self.false_list = []
      self.wrong_page=[]
      self.status=False
      self.false_404=[]
      self.start_time = time.time()
      self.end_time = time.time()
      self.error=0
      self.false_url=[]
      self.watch_list=[]
      self.count=0
      self.Create_time=time.strftime("%Y%m%d", time.localtime()) #現在時間
      self.thread=4

  def start(self):#目前先用手動註解掉


      #爬取主要表格
      self.get_data()
      df = pd.DataFrame(self.raw_list)
      df.to_csv('/content/drive/MyDrive/mtginvestment/ck/raw_list_t.csv',index=False,header=False )

      #self.readcsv()       # 讀取已經存好的csv檔(全部執行的話就要註解調不然會有同時出現兩個)
      self.filter_data()     # 過濾掉價格小於2的資料
      self.search_thread()    # goldfish查詢
      self.save()
      self.end_time = time.time()

      print(len(self.raw_list),'筆Raw_list')
      print(self.num+'筆資料查詢成功')
      print(len(self.None_list),'筆原本轉換為None')
      print(len(self.false_list),'筆錯誤')
      print(len(self.watch_list),'筆觀察清單')
      print('共',self.count,'筆資料')
      print('運行時間:'+str('%.2f'%(self.end_time-self.start_time))+'秒')
      

  def get_data(self):
    self.cul=0

    def click(Thread,start,n):
        # url = 'https://www.cardkingdom.com/purchasing/mtg_singles?filter%5Bsort%5D=price_desc&page='
        url = 'https://www.cardkingdom.com/purchasing/mtg_singles?filter%5Bsort%5D=price_desc&filter%5Bsearch%5D=mtg_advanced&filter%5Bname%5D=&filter%5Bedition%5D=&filter%5Bformat%5D=standard&filter%5Bsingles%5D=1&filter%5Bprice_op%5D=gte&filter%5Bprice%5D=1.99&page='
        options = Options()
        #options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome( options=options,) # 'chromedriver'  ,service=Service(ChromeDriverManager().install())
        #先載入網站，一開始直接指定頁數會跳掉
        driver.get(url)
        for i in range(start,int(start+n)):
            new_url=url+str(i)
            try:
                driver.get(new_url)
                #此處有些微更改，新版selenium需使用By.來查詢類別
                iframe=driver.find_elements(By.CLASS_NAME,"itemContentWrapper")
                # iframe=driver.find_elements(By.CLASS_NAME,"sellDollarAmount")
                for j in iframe:
                    self.original.append(j.text)
                time.sleep(random.random())

            except:
                self.wrong_page.append(i)
                print(f'{Thread} Page {i} fail')
                continue

            print(f'{Thread} : {str(i)} / {start}-{start+n-1} {100*(i-start+1)/n}%  {self.cul+len(self.original)}')
        driver.close()
        print(f'{Thread} : {start}-{start+n-1} Done')
    #由於Image 需要時間載入 故用Multi-thred多開分頁方式加快運行
    # 建立 n 個子執行緒
    n_thread=self.thread
    threads = []
    for i,j in zip( range(0,n_thread) , range(1,100,int(100/n_thread)) ):#original用400
        threads.append(threading.Thread( target=click, args=("Thread-"+str(i) , j , 100/n_thread ) ) )
        threads[i].start()

        time.sleep(6)

    for i in range(n_thread):
      threads[i].join()
    #過濾資料
    self.re_data()

  def re_data(self):#正則 過濾資料
      for i in self.original:
          sepdata = str(re.findall('(.*)\n', i, re.MULTILINE))# e.g: 'Underground Sea\n3rd Edition (R)\nLand - Island Swamp\n$570.00 $741.00\nQty to Sell'
          sepdata = ast.literal_eval(sepdata)#str轉回list
          name = sepdata[0]
          edition = sepdata[1][:-4]
          price = str(re.findall('\$(.*)\$', str(sepdata[-2]), re.MULTILINE))
          price = price[2:-2]
          print(name, edition, price, sep='\t')
          tmp = [name, edition, price]
          self.raw_list.append(tmp)
      print("")
      print(self.raw_list)

  def readcsv(self):#
      import csv
      with open('/content/drive/MyDrive/mtginvestment/ck/raw_list_t.csv', 'r') as csvfile:#raw_list_t = 測試用的小資料
        csv_reader = reader(csvfile)
        tmp = csv_reader
        for i in tmp:
          self.raw_list.append(i)
        csvfile.close()

  def filter_data(self): #過濾price drop調小於2的資料跟大於1000的
      for i in range(len(self.raw_list)-1,0,-1):
        if bool(self.raw_list[i][2].count(',')) == True:
          del self.raw_list[i]
        if float(self.raw_list[i][2])<=2:
          del self.raw_list[i]
      print(len(self.raw_list) , '筆資料待查詢')

  def search_thread(self):
      url_list = []
      #修正版本名稱至可用goldfish查詢

      for i in self.raw_list:
        try:
          setname = ck2gf(i[1]) #如果有跳key error通常是連接詞的大小寫有錯 不想理他的話就直接建一個他的dict給404就好了
          setname = setname.replace(':', '')
          setname = setname.replace("'", '')
          setname = setname.replace(' ', '+')
          tmp = [i[0], setname, i[2]]
          self.main_list.append(tmp)
        except KeyError as error:
          pass

      #goldfish查詢
      for i in self.main_list:
          url = goldfish.get_url(i[1], i[0], '')
          tmp = [i[0], i[1], i[2], url]
          url_list.append(tmp)

      self.my_queue = queue.Queue()

      for i in url_list:
          self.my_queue.put(i)

      self.work()

      self.num = str(len(self.result_list))

  def get_price(self, url):
      #fake-useragent 套件可以隨機產生 User-Agent 字串
      ua = UserAgent()
      user_agent = ua.random
      headers = {'user-agent': user_agent}
      #false_list: 錯誤 常見部分:404, 200(但沒中價)
      #none_list: 自行過濾太複雜的版本

      if url[3] :#從url過濾是否能查到價格

          self.count+=1
          res = requests.get(url[3], headers=headers)
          soup = BeautifulSoup(res.text, 'html.parser')
          b = soup.find_all('div', class_ = 'price-box-price')#中價

          if b:# 有些它的版本沒有分那麼細 如果沒查到東西就先忽略
              mid = b[0].text
              if 'tix' not in mid:#沒閃的版本會查到mo價格
                      mid = mid.replace(',', '')
                      mid = mid[2:]
                      ck_price = float(url[2])
                      rate = ck_price / float(mid) * 30
                      tmp = [url[0], url[1], url[2], mid, '%.2f'%rate]
                      self.result_list.append(tmp)
                      print(self.count,tmp)
                      if rate>=20:
                        self.watch_list.append(tmp)
          else:
            print(self.count,"False", res.status_code, b)
            self.error+=1
            self.false_list.append([url[0], url[1], url[2], url[3], res.status_code])

      if url[3]==None:
        self.count+=1
        self.None_list.append(url)
        print(self.count, "None")

      time.sleep(4)

  def work(self):#應該有比較好的方法來開worker吧..

      # 建立 Worker
      my_worker1 = Worker(self.my_queue)
      my_worker2 = Worker(self.my_queue)
      my_worker3 = Worker(self.my_queue)
      my_worker4 = Worker(self.my_queue)
      my_worker5 = Worker(self.my_queue)
      my_worker6 = Worker(self.my_queue)

      # 讓 Worker 開始處理資料
      my_worker1.start()
      my_worker2.start()
      my_worker3.start()
      my_worker4.start()
      my_worker5.start()
      my_worker6.start()
      # 等待所有 Worker 結束
      my_worker1.join()
      my_worker2.join()
      my_worker3.join()
      my_worker4.join()
      my_worker5.join()
      my_worker6.join()

  def save(self):
      path = '/content/drive/MyDrive/mtginvestment/ck/data/'+self.Create_time
      if not os.path.isdir(path):
        os.mkdir(path)

      self.watch_list=sorted(self.watch_list, key = itemgetter(4),reverse=True)

      with open(path + '/result.csv', 'w',  newline='', encoding= 'utf-8') as output:
              csv_writer = csv.writer(output)
              for i in self.result_list:
                  csv_writer.writerow(i)
      with open(path + '/false_list.csv', 'w',  newline='', encoding= 'utf-8') as output_false_list:
              csv_writer = csv.writer(output_false_list)
              for i in self.false_list:
                  csv_writer.writerow(i)
      with open(path + '/None_list.csv', 'w',  newline='', encoding= 'utf-8') as output_None_list:
              csv_writer = csv.writer(output_None_list)
              for i in self.None_list:
                  csv_writer.writerow(i)
      with open(path + '/watch_list.csv', 'w',  newline='', encoding= 'utf-8') as output_watch_list:
              csv_writer = csv.writer(output_watch_list)
              for i in self.watch_list:
                  csv_writer.writerow(i)

if __name__ =='__main__':
    cardkingdom = ck()
    cardkingdom.start()

#original: 剛撈下來的資料
#raw_list: re的資料
#main_list: 經過re的資料
#false_url: 你的URL錯誤
#false_404: request成功 但是沒有撈到資料
#none_list: 你本來就寫404的
#watch_list: 你要的
#result: 成功的大表
