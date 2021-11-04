from selenium.webdriver.support.ui import WebDriverWait

import configparser
import connect_html

from enum import Enum
from datetime import datetime as dt
import concurrent.futures

import os
import re
import csv

headless_mode = True
export_path = 'master'

def LoadEnviormentVariables(enviorment_path):
    global headless_mode
    global export_path
    if os.path.exists(enviorment_path):
        config = configparser.ConfigParser()
        config.read(enviorment_path)
        try:
            data = config.get("settings", "headless_mode")
            headless_mode = eval(data)
        except:
            pass
        try:
            data = config.get("settings", "export_path")
            export_path = data
        except:
            pass

class ProductType(Enum):
    EXPANSION = 0
    DECK = 1
    OTHERS = 2
def GetPriductName(product_type):
    product : str
    if product_type == ProductType.EXPANSION:
        product = 'expansion'
    elif product_type == ProductType.DECK:
        product = 'deck'
    elif product_type == ProductType.OTHERS:
        product = 'others'
    return product

def GetPriductPageDriver(product_type, page):
    return 'https://dm.takaratomy.co.jp/product/'+ GetPriductName(product_type) + '/page/' + str(page)

def JQueryWait(driver):
    # 以下ajaxの読み込み完了待ち
    wait = WebDriverWait(driver, 100)
    wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

class Product:
    def __init__(self, content_product):
        self.name : str
        self.type : str
        self.pic_link : str
        self.release_date = 0
        self.price = 0
        for content in content_product.contents:
            if content != '\n' and content != ' ':
                attr_type = content.attrs['class'][0]
                if attr_type == 'img':
                    self.ImgParse(content.contents)
                elif attr_type == 'pc_box':
                    self.InfoParse(content.contents)

    def IsCardProduct(self):
        # DMXXといったシリーズ以外はカード関係ないとみなしてスキップ
        return self.name.startswith('DM')

    def GetWriteData(self):
        return [self.name,self.pic_link,self.release_date,self.price]

    def ImgParse(self, img_contents):
        for content in img_contents:
            if content != '\n':
                self.pic_link = content.attrs['src']
        # print(img_content.attrs['alt'])

    def InfoInternalParse(self, internal_contents):
        for content in internal_contents:
            if content != '\n':
                if content.attrs['class'][0] == 'product_type':
                    for judge in content.contents:
                        if judge != '\n':
                            self.type = judge.contents[0]
                            break
                elif content.attrs['class'][0] == 'title':
                    # パック名
                    self.name = content.contents[0]
                elif content.attrs['class'][0] == 'infoContainer':
                    # 発売日
                    dateStr = ''
                    for date in content.contents:
                        if date != '\n' and date.contents[0].contents[0] == '発売日':
                            dateStr = date.contents[1].contents[0]
                            break
                    dateStr = re.search('[0-9 年 月 日 上 中 下 旬]+', dateStr)
                    buffer = dateStr.group()
                    if buffer[-1] == '月':
                        buffer += '1日'
                    elif buffer[-1] == '旬':
                        buffer = buffer.replace('上旬', '1日')
                        buffer = buffer.replace('中旬', '15日')
                        buffer = buffer.replace('下旬', '30日')
                    buffer = buffer.replace(' ', '')
                    date = dt.strptime(buffer, "%Y年%m月%d日")
                    self.release_date = int(date.year * 10000 + date.month * 100 + date.day)
                    # パックの値段
                    priceStr = ''
                    for date in content.contents:
                        if date != '\n' and date.contents[0].contents[0] == '希望小売価格':
                            priceStr = date.contents[1].contents[0]
                            break
                    priceStr = re.findall(r'([0-9,]+)円', priceStr)
                    self.price = int(priceStr[0].replace(',', ''))

    def InfoParse(self, info_contents):
        for content in info_contents:
            if content != '\n' and content.attrs['class'][0] == 'info':
                self.InfoInternalParse(content)

    def __str__(self):
        return self.name + '\n' + self.type +'\n' + self.pic_link +'\n' + str(self.release_date) +'\n' + str(self.price)

def CreateProductListCSV(product_type):
    page = 1
    product_list = []
    while True:
        print('ページ : ' + str(page))
        # chrome起動、操作権取得
        driver = connect_html.GetDriver(GetPriductPageDriver(product_type, page), headless_mode)
        JQueryWait(driver)
        html = connect_html.GetBeautifulSoupFromDriver(driver)
        try:
            product_list_box = html.select('#mainContent > section > div.sectionIn01 > div.itemList01')[0]
            for content in product_list_box.contents:
                if content != '\n':     
                    product = Product(content)       
                    print(product)
                    product_list.append(product)
            page = page + 1
        except:
            print('complete!')
            # 例外＝存在しないページ＝一覧の終了
            break
    product = GetPriductName(product_type)
    directory = export_path + '/product_list/'  
    if not os.path.exists(directory):
        os.makedirs(directory) 
    with open(directory + product + '.csv', 'w', newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['パック名','画像url','発売日','販売価格'])
        for product in product_list:
            if product.IsCardProduct():
                writer.writerow(product.GetWriteData())


# エントリポイント
if __name__ == '__main__':
    LoadEnviormentVariables("enviorment.ini")
    with concurrent.futures.ThreadPoolExecutor(max_workers = 1) as executor:
        executor.map(CreateProductListCSV,[ProductType.EXPANSION, ProductType.DECK, ProductType.OTHERS])
