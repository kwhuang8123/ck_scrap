from typing import _SpecialForm
import requests
from bs4 import BeautifulSoup
try:
    from service.setcode2name import setcode2name
except(ModuleNotFoundError):
    from setcode2name import setcode2name
import concurrent.futures

class goldfish:
    def getmid(set, name, f):
        global pricetype
        name = str(name)
        #name = name[2:-2]
        if 'AEther' in name:
            name = 'Aether'+name[6:]
        name = name.replace(' ', '+')
        name = name.replace(',', '')
        name = name.split('》')
        name = name[0]
        var = '' 
        foil = ''
        if 'Foil' in f:
            foil = ':Foil'
        if 'Retro' in f:
            var = '-retro'
        if set[3:6] == '-BT':
            var = '-var'
        setname = goldfish.getsetname(set)
        if setname == '404':
            pass

        url = 'https://www.mtggoldfish.com/price/' + setname + foil + '/' + name + var+ '#'#+pricetype
        res = requests.get(url, headers={'Connection':'close'})
        soup = BeautifulSoup(res.text, 'html.parser')
        
        a = soup.find_all('div', class_ = 'price-card-name-set-name')
        b = soup.find_all('div', class_ = 'price-box-price')

        
        if b:
            mid = b[0].text
            return mid
        else:
            pass

    def getsetname(self):
        setname = setcode2name(self[0:3])
        if setname == '':
            tmp = '404'
            return tmp 
        else:
            tmp = setname.replace(':', '')
            tmp = tmp.replace(' ', '+')
            return tmp
    
    def get_url(set, name, variation):#獲取網址
        name = str(name)
        
        if 'AEther' in name:
            name = 'Aether'+name[6:]
        name = name.replace(' ', '+')
        name = name.replace(',', '')
        name = name.replace("'", '')
        name = name.split('(')
        name = name[0]
        name = name.split('》')
        name = name[0]
        var = '' 
        foil = ''
        if 'Foil' in variation:#閃卡
            foil = ':Foil'
        if 'Retro' in variation:#擴圖
            var = '-retro'
        if set[3:6] == '-BT':
            var = '-var'
        setname = set
        if setname != '404':
            url = 'https://www.mtggoldfish.com/price/' + setname + foil + '/' + name + var + '#'#網址格式
            return url
    
    def get_price(url):
        if url :
            res = requests.get(url, headers={'Connection':'close'})
            soup = BeautifulSoup(res.text, 'html.parser')
            
            a = soup.find_all('div', class_ = 'price-card-name-set-name')#名稱
            b = soup.find_all('div', class_ = 'price-box-price')#中價

            
            if b:
                mid = b[0].text
                #print(mid)
                return mid
            else:
                pass