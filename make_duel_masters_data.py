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
from selenium.webdriver.support.select import Select
import configparser
import psutil

import os
import csv
import stat
import duel_masters_card_box

# 環境変数
# enviorment.iniで変えるようにしてください
chrome_driver_path = 'chromedriver'
headless_mode = True
export_path = 'master'
thread_count = -1

# 環境変数の読み込み
def LoadEnviormentVariables(enviorment_path):
    global chrome_driver_path
    global headless_mode
    global export_path
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
            data = config.get("settings", "export_path")
            export_path = data
        except:
            pass
        try:
            data = config.get("settings", "thread_count")
            thread_count = int(data)
        except:
            pass
    duel_masters_card_box.SettingEnviorment(chrome_driver_path,headless_mode,export_path,thread_count)

def UpdateMasterData(driver, file_path, first_card):
    # 更新の必要有り無しを調べる
    html = connect_html.GetBeautifulSoupFromDriver(driver)
    card_list = duel_masters_card_box.GetCardList(html)
    del card_list[1:]
    card_box = duel_masters_card_box.CardPageProcedure(card_list)
    print('top card : ' + card_box[0].name)
    print('data top card : ' + first_card)
    if card_box[0].name != first_card:
        print("更新が必要")
        diff_path = file_path + '.diff'
        # 差分ファイルの作成
        with open(diff_path, 'w', newline="", encoding='utf-8') as file:
            duel_masters_card_box.DuelMastersCardBox(driver, 1, file)
        diff_data = []
        # 実際のファイル読み込み
        with open(diff_path, 'r', newline="", encoding='utf-8') as file:
            diff_reader = csv.reader(file)
            diff_data = list(diff_reader)
        #     # if not os.access(export_path, os.W_OK):
        #     #     os.chmod(export_path, stat.S_IWRITE)
        #     with open(file_path, 'r', newline="", encoding='utf-8') as file:
        #         reader = csv.reader(file)
        #         exist_data = list(reader)
        #         del exist_data[0]
        #         print('new card count : ' + str(len(diff_data)))
        #         data.extend(diff_data)
        #         data.extend(exist_data)
        os.remove(diff_path)
        # 結合したものをcsv化
        with open(file_path, 'w', newline = "", encoding = 'utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(diff_data)
        return len(diff_data)
    return 0

def PageCroll(driver, file_path):
    # 検索開始するカードの位置、既存のカード枚数 + 1
    row_count = 1
    first_card = None
    # 既存のファイルが存在するのであれば
    if os.path.exists(file_path):
        with open(file_path, 'r', newline="", encoding='utf-8') as file:
            reader = csv.reader(file)
            matrix = list(reader)
            row_count = len(matrix)
            if row_count > 1:
                first_card = matrix[1][1]
                value = UpdateMasterData(driver, file_path, first_card)
                if value > 1:
                    row_count = value

    # 復帰処理などの都合上、追記モードで開く
    with open(file_path, 'a', newline="", encoding='utf-8') as file:
        # カードボックス取得
        cardbox = duel_masters_card_box.DuelMastersCardBox(driver, row_count, file)
    print('complete')


# エントリポイント
if __name__ == '__main__':
    LoadEnviormentVariables("enviorment.ini")
    # chrome起動、操作権取得
    driver = connect_html.GetDriver('https://dm.takaratomy.co.jp/card/', chrome_driver_path, headless_mode)
    html = connect_html.GetBeautifulSoupFromDriver(driver)
    # https://yuki.world/selenium-select/#t_valuexSelectselect_by_value
    products = driver.find_element_by_xpath('//*[@id="search_cond"]/div[1]/div[2]/select')
    select_products = Select(products)
    all_options = select_products.options
    for option in all_options:
        if option.get_attribute('value') == '':
            continue
        # print(option.text) # 選択肢のテキスト
        # print(option.get_attribute('outerHTML')) # HTMLタグ
        id = option.get_attribute('value')
        select_products.select_by_value(id)
        search_button = driver.find_element_by_xpath('//*[@id="search_cond"]/div[3]/input[1]')
        search_button.click()
        # 以下ajaxの読み込み完了待ち
        wait = WebDriverWait(driver, 100)
        wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        print(id) # value属性の値
        product_name = option.get_attribute('text')
        PageCroll(driver, export_path + '/' + product_name + '.csv')
        print(product_name + ' complete')
    # chromeの解放 これをしないとバックグラウンドプロセスにchrome driverとgoogle chromeが大量に発生する
    connect_html.ReleaseDriver(driver)