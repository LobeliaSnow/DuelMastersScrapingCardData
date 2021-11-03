import connect_html
from selenium.webdriver.support.ui import WebDriverWait
from enum import Enum
import concurrent.futures

import csv

class ProductType(Enum):
    EXPANSION = 0
    DECK = 1
    OTHERS = 2

def GetPriductPageDriver(product_type, page):
    product : str
    if product_type == ProductType.EXPANSION:
        product = 'expansion'
    elif product_type == ProductType.DECK:
        product = 'deck'
    elif product_type == ProductType.OTHERS:
        product = 'others'
    return 'https://dm.takaratomy.co.jp/product/'+ product + '/page/' + str(page)

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
                    pass
                    # todo 数値分離
                    # 発売日
                    # print(content.contents[1].contents[1].contents[0])
                    # self.release_date = content.contents[1].contents[1].contents[0]
                    # パックの値段
                    # print(content.contents[3].contents[1].contents[0])
                    # self.price = content.contents[3].contents[1].contents[0]

    def InfoParse(self, info_contents):
        for content in info_contents:
            if content != '\n' and content.attrs['class'][0] == 'info':
                self.InfoInternalParse(content)

    def __str__(self):
        return self.name + '\n' + self.type +'\n' + self.pic_link +'\n' + str(self.release_date) +'\n' + str(self.price)

def CreateProductListCSV(product_type):
    page = 1
    while True:
        driver = connect_html.GetDriver(GetPriductPageDriver(product_type, page), True)
        # chrome起動、操作権取得
        JQueryWait(driver)
        html = connect_html.GetBeautifulSoupFromDriver(driver)
        try:
            product_list_box = html.select('#mainContent > section > div.sectionIn01 > div.itemList01')[0]
            product_list = []
            for content in product_list_box.contents:
                if content != '\n':     
                    product = Product(content)       
                    print(product)
                    product_list.append(product)
            page = page + 1
        except:
            # 存在しないページ＝一覧の終了
            break

# エントリポイント
if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers = 1) as executor:
        executor.map(CreateProductListCSV,[ProductType.EXPANSION, ProductType.DECK, ProductType.OTHERS])
