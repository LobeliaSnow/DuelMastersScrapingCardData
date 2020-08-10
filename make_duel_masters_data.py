# デュエルマスターズのカードデータをスクレイピング
import requests
from bs4 import BeautifulSoup
import connect_html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import configparser
import psutil

import os
import csv
import platform
import concurrent.futures
import time

# 環境変数
# enviorment.iniで変えるようにしてください
chrome_driver_path = 'chromedriver'
headless_mode = True
master_path = 'master.csv'
thread_count = -1

# リストをN分割する関数
def SplitList(list, n):
    list_size = len(list)
    a = list_size // n
    b = list_size % n
    return [list[i*a + (i if i < b else b):(i+1)*a + (i+1 if i < b else b)] for i in range(n)]

# 環境変数の読み込み
def LoadEnviormentVariables(enviorment_path):
    global chrome_driver_path
    global headless_mode
    global master_path
    global thread_count
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
        try:
            data = config.get("settings", "thread_count")
            thread_count = int(data)
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
            # 途中で改行を挟んでくる奴が発見されて、推定そこで例外を吐いたのでその対応
            try:
                self.ability += ability.text.replace('\n', '') + '\n'
            except:
                pass
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

# 各ページのカードリストを処理するための関数
def CardPageProcedure(card_list):
    page_driver = None
    temp_box = []
    for card in card_list:
        # 各カードへのリンク取得
        data_link = card.contents[0].get('href')
        print(data_link)
        if page_driver is None:
            # 新規タブで
            page_driver = connect_html.GetDriver('https://dm.takaratomy.co.jp' + data_link, chrome_driver_path, headless_mode)
        else:
            # 現在のタブで
            page_driver.get('https://dm.takaratomy.co.jp' + data_link)
        card_page = connect_html.GetBeautifulSoupFromDriver(page_driver)
        # カード情報をスクレイピング
        card = DuelMastersCard(card_page, data_link)
        # デバッグ表示、気になる人はつけるとよい
        print(card)
        # カードボックスへプール
        temp_box.append(card)
    connect_html.ReleaseDriver(page_driver)
    return temp_box


# カードボックス
class DuelMastersCardBox:
    def __init__(self, driver, start_index, writer):
        # csvの書き込み用
        self.writer = csv.writer(writer)
        # 以下スクレイピング用
        self.driver = driver
        html = connect_html.GetBeautifulSoupFromDriver(self.driver)
        self.page_count = html.select_one('#cardlist > div > div > a.nextpostslink').get('data-page')
        self.card_access_list = []
        self.card_box = []
        # 何ページ目から検索するか
        start_page = 1
        start_card = 1
        # 既存のCSVが存在している場合
        if start_index > 1:
            # デュエマに存在するカード枚数を取得
            card_total_count = html.select_one('#total_count').text
            # すでに最大枚数取得している場合は新規カードはないので終了
            if start_index == int(card_total_count):
                return
            # 復帰する必要が出てきたので、1ページに存在する最大数を取得
            page_card_max_count = len(html.select("#cardlist > ul > li"))
            # ページの復帰場所
            start_page = int(start_index / page_card_max_count) + 1
            # カードの復帰場所
            start_card = int(start_index % page_card_max_count)
        else:
            # ヘッダー作成
            self.WriteCardBoxHeader()
        global thread_count
        # 0以下ならCPUにとって最適なコア数に
        if thread_count < 0:
            # CPUの論理コア数取得
            thread_count = psutil.cpu_count()

        # ページの復帰処理
        if start_page > 1 and start_page != 2:
            # TODO 最適化
            # start_page-1の理由は一発目の処理時に次のページへ進むため
            for recover_index in range(2, start_page):
                if recover_index == start_page:
                    recover_index = start_page - 1
                # 2ページずつ飛ばす
                elif recover_index % 2 == 0 and recover_index != start_page:
                    continue
                try:
                    link = self.driver.find_element_by_link_text(str(recover_index))
                except:
                    #リンクが運悪く取得できなかった場合は一旦1秒待つ
                    time.sleep(1)
                    link = self.driver.find_element_by_link_text(str(recover_index))
                driver.execute_script("arguments[0].click();", link)              
                # 以下ajaxの読み込み完了待ち
                wait = WebDriverWait(driver, 15)
                wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        # ここで一旦待ち、ページのロードが終わっていない可能性
        time.sleep(1)
        # 各ページ用
        for page in range(start_page, int(self.page_count)):
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
            # カードリスト取得
            card_list = html.select("#cardlist > ul > li")
            # カードの復帰処理
            if start_card > 0:
                del card_list[0 : start_card - 1]
                start_card = 0
            self.page_card_box = []
            # マルチスレッドモード
            if thread_count > 0:
                # スレッド数分に分割
                split_card_list = SplitList(card_list, thread_count)
                # マルチスレッドによるカードデータの収集
                with concurrent.futures.ThreadPoolExecutor(max_workers = thread_count) as executor:
                    results = list(executor.map(CardPageProcedure, split_card_list))
                # 各スレッドの結果を結合
                for result in results:
                    self.page_card_box.extend(result)
            else:
                # シングルスレッドモード
                self.page_card_box = CardPageProcedure(card_list)
            # csv書き出し
            if writer is not None:
                self.WriteCardBoxCSV(self.page_card_box)
    
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
    # 検索開始するカードの位置、既存のカード枚数 + 1
    row_count = 1

    # 既存のファイルが存在するのであれば
    if os.path.exists(master_path):
        with open(master_path, 'r', newline="", encoding='utf-8') as file:
            reader = csv.reader(file)
            # ヘッダーが含まれて実際のカード枚数より1多いが、最後のカードの一つ先から読み込むので問題なし
            row_count = len(list(reader))
    # 復帰処理などの都合上、追記モードで開く
    with open(master_path, 'a', newline="", encoding='utf-8') as file:
        # カードボックス取得
        cardbox = DuelMastersCardBox(driver, row_count, file)
    
    # chromeの解放 これをしないとバックグラウンドプロセスにchrome driverとgoogle chromeが大量に発生する
    connect_html.ReleaseDriver(driver)
    