# デュエルマスターズのカードデータをスクレイピング
import requests
from bs4 import BeautifulSoup
import connect_html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# 環境変数
# 自身のローカル環境に合わせて変えてください
chrome_driver_path = 'chromedriver'
headless_mode = True

# TODO ツインパクト対応 / 画像DL / csv書き出し
# TODO マルチスレッド

def LoadEnviormentVariables(enviorment_path):
    global chrome_driver_path
    # 環境変数用ファイルの存在を確認
    if os.path.exists(enviorment_path):
        with open(enviorment_path) as f:
            # 現在はchromedriverのパスのみ外部ファイル化しているのでこれだけ
            chrome_driver_path = f.readlines()[0].rstrip('\n')

class DuelMastersCard:
    def __init__(self, card_page):
        self.card_page = card_page
        # 以下能力取得
        self.name = self.card_page.select_one('#mainContent > section > table > tbody > tr.windowtitle > th').text
        self.type = self.card_page.select_one('#mainContent > section > table > tbody > tr:nth-of-type(2) > td.typetxt').text
        self.civilization = self.card_page.select_one('#mainContent > section > table > tbody > tr:nth-of-type(2) > td.civtxt').text
        self.rarity = self.card_page.select_one('#mainContent > section > table > tbody > tr:nth-of-type(3) > td.raretxt').text
        self.power = self.card_page.select_one('#mainContent > section > table > tbody > tr:nth-of-type(3) > td.powertxt').text
        self.cost = self.card_page.select_one('#mainContent > section > table > tbody > tr:nth-of-type(4) > td.costtxt').text
        self.race = self.card_page.select_one('#mainContent > section > table > tbody > tr:nth-of-type(5) > td').text
        ability_raw = self.card_page.select_one('#mainContent > section > table > tbody > tr:nth-child(7) > td')
        self.ability = ''
        for ability in ability_raw:
            self.ability += ability.text + '\n'
        self.flavor = self.card_page.select_one('#mainContent > section > table > tbody > tr:nth-child(9) > td').text

    # printで表示するためのもの、デバッグ用
    def __str__(self):
        return 'name : ' + self.name + '\n' + 'type : ' + self.type + '\n' + 'civilization : ' + self.civilization+ '\n' + 'rarity : ' + self.rarity + '\n' \
        + 'power : ' + self.power + '\n' + 'cost : ' + self.cost + '\n' + 'race : ' + self.race + '\n' + 'ability : ' + self.ability + '\n' + 'flavor : ' + self.flavor + '\n'

class DuelMastersCardBox:
    def __init__(self, driver):
        self.driver = driver
        html = connect_html.GetBeautifulSoupFromDriver(self.driver)
        self.page_count = html.select_one('#cardlist > div > div > a.nextpostslink').get('data-page')
        self.card_access_list = []
        self.card_box = []
        for page in range(1, int(self.page_count)):
            # 次のページへジャンプ
            if int(page) > 1:
                link = self.driver.find_element_by_link_text(str(page))
                link.click()
                # 以下ajaxの読み込み完了待ち
                wait = WebDriverWait(driver, 15)
                wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                # 更新されたページのhtmlを取得する
                html = connect_html.GetBeautifulSoupFromDriver(self.driver)
            # カードリストを順次探索
            self.card_access_list.append(html.select("#cardlist > ul > li"))
            card_list = self.card_access_list[page - 1]
            for card in card_list:
                # 各カードへのリンク取得
                data_link = card.contents[0].get('href')
                # 新たにchromeを開き、対象のカードページへジャンプする
                element_driver = connect_html.GetDriver('https://dm.takaratomy.co.jp' + data_link, chrome_driver_path, headless_mode)
                card_page = connect_html.GetBeautifulSoupFromDriver(element_driver)
                # カード情報をスクレイピング
                card = DuelMastersCard(card_page)
                # カードページを開いているchromeを閉じる
                connect_html.ReleaseDriver(element_driver)
                # デバッグ表示、気になる人はつけるとよい
                print(card)
                # カードボックスへプール
                self.card_box.append(card)
                break
            break

if __name__ == '__main__':
    LoadEnviormentVariables("enviorment.txt")
    # chrome起動、操作権取得
    driver = connect_html.GetDriver('https://dm.takaratomy.co.jp/card/', chrome_driver_path, headless_mode)
    # カードボックス取得
    cardbox = DuelMastersCardBox(driver)
    # chromeの解放 これをしないとバックグラウンドプロセスにchrome driverとgoogle chromeが大量に発生する
    connect_html.ReleaseDriver(driver)
    