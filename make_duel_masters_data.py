# デュエルマスターズのカードデータをスクレイピング
import requests
from bs4 import BeautifulSoup
import connect_html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import configparser
import os
import csv

# 環境変数
# enviorment.iniで変えるようにしてください
chrome_driver_path = 'chromedriver'
headless_mode = True
master_path = 'master.csv'

# TODO マルチスレッド

# 環境変数の読み込み
def LoadEnviormentVariables(enviorment_path):
    global chrome_driver_path
    global headless_mode
    global master_path
    # 環境変数用ファイルの存在を確認
    if os.path.exists(enviorment_path):
        config = configparser.ConfigParser()
        config.read(enviorment_path)
        try:
            data = config.get("settings", "chrome_driver_path")
            chrome_driver_path = data
        except:
            pass
        try:
            data = config.get("settings", "headless_mode")
            headless_mode = eval(data)
        except:
            pass
        try:
            data = config.get("settings", "master_path")
            master_path = data
        except:
            pass

# カード単位
class DuelMastersCard:
    def __init__(self, card_page, link):
        self.site_link = link
        # 以下能力取得
        name_data = card_page.select_one('#mainContent > section > table > tbody > tr.windowtitle > th').text
        index = name_data.rfind('(')
        self.name , self.pack = name_data[:index], name_data[index:]
        self.type = card_page.select_one('#mainContent > section > table > tbody > tr:nth-of-type(2) > td.typetxt').text
        self.civilization = card_page.select_one('#mainContent > section > table > tbody > tr:nth-of-type(2) > td.civtxt').text
        self.rarity = card_page.select_one('#mainContent > section > table > tbody > tr:nth-of-type(3) > td.raretxt').text
        self.power = card_page.select_one('#mainContent > section > table > tbody > tr:nth-of-type(3) > td.powertxt').text
        self.cost = card_page.select_one('#mainContent > section > table > tbody > tr:nth-of-type(4) > td.costtxt').text.split(' ')[0]
        self.mana = card_page.select_one('#mainContent > section > table:nth-of-type(1) > tbody > tr:nth-of-type(4) > td.manatxt').text
        self.race = card_page.select_one('#mainContent > section > table > tbody > tr:nth-of-type(5) > td').text
        ability_raw = card_page.select_one('#mainContent > section > table > tbody > tr:nth-of-type(7) > td')
        self.ability = ''
        for ability in ability_raw:
            self.ability += ability.text.replace('\n', '') + '\n'
        self.ability = self.ability.rstrip('\n')
        self.flavor = card_page.select_one('#mainContent > section > table > tbody > tr:nth-of-type(9) > td').text.replace('\n', '')
        self.pic_url = card_page.select_one('#mainContent > section > table > tbody > tr:nth-child(2) > td.cardarea > div > img').get('src')
        # 以下ツインパクト、ドラグハート、サイキック用
        name_data = card_page.select_one('#mainContent > section > table:nth-of-type(2) > tbody > tr.windowtitle > th')
        if name_data is None:
            return
        index = name_data.text.rfind('(')
        self.second_name = name_data.text[:index]
        self.second_type = card_page.select_one('#mainContent > section > table:nth-of-type(2) > tbody > tr:nth-of-type(2) > td.typetxt').text
        self.second_civilization = card_page.select_one('#mainContent > section > table:nth-of-type(2) > tbody > tr:nth-of-type(2) > td.civtxt').text
        self.second_rarity = card_page.select_one('#mainContent > section > table:nth-of-type(2) > tbody > tr:nth-of-type(3) > td.raretxt').text
        self.second_power = card_page.select_one('#mainContent > section > table:nth-of-type(2) > tbody > tr:nth-of-type(3) > td.powertxt').text
        self.second_cost = card_page.select_one('#mainContent > section > table:nth-of-type(2) > tbody > tr:nth-of-type(4) > td.costtxt').text.split(' ')[0]
        self.second_mana = card_page.select_one('#mainContent > section > table:nth-of-type(2) > tbody > tr:nth-of-type(4) > td.manatxt').text
        self.second_race = card_page.select_one('#mainContent > section > table:nth-of-type(2) > tbody > tr:nth-of-type(5) > td').text
        ability_raw = card_page.select_one('#mainContent > section > table:nth-of-type(2) > tbody > tr:nth-of-type(7) > td')
        self.ability = ''
        for ability in ability_raw:
            self.ability += ability.text.replace('\n', '') + '\n'
        self.second_ability = self.ability.rstrip('\n')
        self.second_flavor = card_page.select_one('#mainContent > section > table:nth-of-type(2) > tbody > tr:nth-of-type(9) > td').text.replace('\n', '')
        self.second_pic_url = card_page.select_one('#mainContent > section > table:nth-of-type(2) > tbody > tr:nth-child(2) > td.cardarea > div > img').get('src')
        # 3D龍解用
        name_data = card_page.select_one('#mainContent > section > table:nth-of-type(6) > tbody > tr.windowtitle > th')
        if name_data is None:
            return
        index = name_data.text.rfind('(')
        self.third_name = name_data.text[:index]
        self.third_type = card_page.select_one('#mainContent > section > table:nth-of-type(6) > tbody > tr:nth-of-type(2) > td.typetxt').text
        self.third_civilization = card_page.select_one('#mainContent > section > table:nth-of-type(6) > tbody > tr:nth-of-type(2) > td.civtxt').text
        self.third_rarity = card_page.select_one('#mainContent > section > table:nth-of-type(6) > tbody > tr:nth-of-type(3) > td.raretxt').text
        self.third_power = card_page.select_one('#mainContent > section > table:nth-of-type(6) > tbody > tr:nth-of-type(3) > td.powertxt').text
        self.third_cost = card_page.select_one('#mainContent > section > table:nth-of-type(6) > tbody > tr:nth-of-type(4) > td.costtxt').text.split(' ')[0]
        self.third_mana = card_page.select_one('#mainContent > section > table:nth-of-type(6) > tbody > tr:nth-of-type(4) > td.manatxt').text
        self.third_race = card_page.select_one('#mainContent > section > table:nth-of-type(6) > tbody > tr:nth-of-type(5) > td').text
        ability_raw = card_page.select_one('#mainContent > section > table:nth-of-type(6) > tbody > tr:nth-of-type(7) > td')
        self.ability = '\"'
        for ability in ability_raw:
            self.ability += ability.text.replace('\n', '') + '\n'
        self.third_ability = self.ability.rstrip('\n')
        self.third_ability += '\"'
        self.third_flavor = card_page.select_one('#mainContent > section > table:nth-of-type(6) > tbody > tr:nth-of-type(9) > td').text.replace('\n', '')
        self.third_pic_url = card_page.select_one('#mainContent > section > table:nth-of-type(6) > tbody > tr:nth-child(2) > td.cardarea > div > img').get('src')

    # printで表示するためのもの、デバッグ用
    def __str__(self):
        first_card = 'name : ' + self.name + '\n' + 'pack : ' + self.pack + '\n' + 'type : ' + self.type + '\n' + 'civilization : ' + self.civilization+ '\n' + 'rarity : ' + self.rarity + '\n' \
        + 'power : ' + self.power + '\n' + 'cost : ' + self.cost + '\n' + 'race : ' + self.race + '\n' + 'ability : ' + self.ability + '\n' + 'flavor : ' + self.flavor + '\n'
        ret_value =  'first card : \n' + first_card
        try:
            second_card = 'name : ' + self.second_name + '\n' + 'type : ' + self.second_type + '\n' + 'civilization : ' + self.second_civilization+ '\n' + 'rarity : ' + self.second_rarity + '\n' \
            + 'power : ' + self.second_power + '\n' + 'cost : ' + self.second_cost + '\n' + 'race : ' + self.second_race + '\n' + 'ability : ' + self.second_ability + '\n' + 'flavor : ' + self.second_flavor + '\n'
        except:
            return ret_value
        ret_value += '\n' + second_card
        try:
            third_card = 'name : ' + self.third_name + '\n' + 'type : ' + self.third_type + '\n' + 'civilization : ' + self.third_civilization+ '\n' + 'rarity : ' + self.third_rarity + '\n' \
            + 'power : ' + self.third_power + '\n' + 'cost : ' + self.third_cost + '\n' + 'race : ' + self.third_race + '\n' + 'ability : ' + self.third_ability + '\n' + 'flavor : ' + self.third_flavor + '\n'
        except:
            return ret_value
        ret_value += '\n' + third_card
        return ret_value

# カードボックス
class DuelMastersCardBox:
    def __init__(self, driver, write_file):
        self.writer = csv.writer(write_file)
        self.WriteCardBoxHeader()
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
            self.page_card_box = []
            for card in card_list:
                # 各カードへのリンク取得
                data_link = card.contents[0].get('href')
                # 新たにchromeを開き、対象のカードページへジャンプする
                element_driver = connect_html.GetDriver('https://dm.takaratomy.co.jp' + data_link, chrome_driver_path, headless_mode)
                card_page = connect_html.GetBeautifulSoupFromDriver(element_driver)
                # カード情報をスクレイピング
                card = DuelMastersCard(card_page, data_link)
                # カードページを開いているchromeを閉じる
                connect_html.ReleaseDriver(element_driver)
                # デバッグ表示、気になる人はつけるとよい
                print(card)
                # カードボックスへプール
                self.page_card_box.append(card)
            # csv書き出し
            if write_file is not None:
                self.WriteCardBoxCSV(self.page_card_box)
            self.card_box.append(self.page_card_box.append(card))


    # 以下csv書き出し用関数
    def WriteCardBoxHeader(self):
        if self.writer is None:
            return
        self.writer.writerow(['収録弾', 'カード名', 'カードの種類', '文明', 'レアリティ', 'パワー', 'コスト', 'マナ','種族', '特殊能力', 'フレーバー', '画像リンク', 'カード名 2', 'カードの種類 2', '文明 2', 'レアリティ 2', 'パワー 2', 'コスト 2', 'マナ 2','種族 2', '特殊能力 2', 'フレーバー 2', '画像リンク 2','カード名 3', 'カードの種類 3', '文明 3', 'レアリティ 3', 'パワー 3', 'コスト 3', 'マナ 3','種族3 ', '特殊能力 3', 'フレーバー 3', '画像リンク 3'])
    
    def WriteCardCSV(self, card):
        data = []
        first_card = [card.pack, card.name, card.type, card.civilization, card.rarity, card.power, card.cost, card.mana, card.race, card.ability, card.flavor, card.pic_url]
        data.extend(first_card)
        empty = ['', '', '', '', '', '', '','', '', '', '']
        try:
            second_card = [card.second_name, card.second_type, card.second_civilization, card.second_rarity, card.second_power, card.second_cost, card.second_mana, card.second_race, card.second_ability, card.second_flavor, card.second_pic_url]
            data.extend(second_card)
        except:
            data.extend(empty)
        try:
            third_card = [card.third_name, card.third_type, card.third_civilization, card.third_rarity, card.third_power, card.third_cost, card.third_mana, card.third_race, card.third_ability, card.third_flavor, card.third_pic_url]
            data.extend(third_card)
        except:
            data.extend(empty)            
        self.writer.writerow(data)

    def WriteCardBoxCSV(self, card_box):
        for card in card_box:
            self.WriteCardCSV(card)


# エントリポイント
if __name__ == '__main__':
    LoadEnviormentVariables("enviorment.ini")
    # chrome起動、操作権取得
    driver = connect_html.GetDriver('https://dm.takaratomy.co.jp/card/', chrome_driver_path, headless_mode)
    with open(master_path, 'w', newline="", encoding='utf-8') as file:
        # カードボックス取得
        cardbox = DuelMastersCardBox(driver, file)
    # chromeの解放 これをしないとバックグラウンドプロセスにchrome driverとgoogle chromeが大量に発生する
    connect_html.ReleaseDriver(driver)
    