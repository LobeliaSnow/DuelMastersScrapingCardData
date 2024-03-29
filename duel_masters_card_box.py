# デュエルマスターズのカードデータをスクレイピング
import connect_html
from selenium.webdriver.support.ui import WebDriverWait
import psutil

import csv
import concurrent.futures
import time

# 環境変数
# enviorment.iniで変えるようにしてください
headless_mode = True
export_path = 'master'
thread_count = -1

def SettingEnviorment( headless, exp_path, threads):
    global headless_mode
    global export_path
    global thread_count
    headless_mode = headless
    export_path = exp_path
    thread_count = threads

# リストをN分割する関数
def SplitList(list, n):
    list_size = len(list)
    a = list_size // n
    b = list_size % n
    return [list[i*a + (i if i < b else b):(i+1)*a + (i+1 if i < b else b)] for i in range(n)]


# カード単位
class DuelMastersCard:
    def __init__(self, card_page, link):
        self.site_link = link
        # 以下能力取得
        try:
            name_data = card_page.select_one('#mainContent > section > table > tbody > tr.windowtitle > th').text
        except:
            return
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
        self.second_ability = ''
        for ability in ability_raw:
            self.second_ability += ability.text.replace('\n', '') + '\n'
        self.second_ability = self.second_ability.rstrip('\n')
        self.second_flavor = card_page.select_one('#mainContent > section > table:nth-of-type(2) > tbody > tr:nth-of-type(9) > td').text.replace('\n', '')
        self.second_pic_url = card_page.select_one('#mainContent > section > table:nth-of-type(2) > tbody > tr:nth-child(2) > td.cardarea > div > img').get('src')
        # 3D龍解用
        name_data = card_page.select_one('#mainContent > section > table:nth-of-type(3) > tbody > tr.windowtitle > th')
        if name_data is None:
            return
        index = name_data.text.rfind('(')
        self.third_name = name_data.text[:index]
        self.third_type = card_page.select_one('#mainContent > section > table:nth-of-type(3) > tbody > tr:nth-of-type(2) > td.typetxt').text
        self.third_civilization = card_page.select_one('#mainContent > section > table:nth-of-type(3) > tbody > tr:nth-of-type(2) > td.civtxt').text
        self.third_rarity = card_page.select_one('#mainContent > section > table:nth-of-type(3) > tbody > tr:nth-of-type(3) > td.raretxt').text
        self.third_power = card_page.select_one('#mainContent > section > table:nth-of-type(3) > tbody > tr:nth-of-type(3) > td.powertxt').text
        self.third_cost = card_page.select_one('#mainContent > section > table:nth-of-type(3) > tbody > tr:nth-of-type(4) > td.costtxt').text.split(' ')[0]
        self.third_mana = card_page.select_one('#mainContent > section > table:nth-of-type(3) > tbody > tr:nth-of-type(4) > td.manatxt').text
        self.third_race = card_page.select_one('#mainContent > section > table:nth-of-type(3) > tbody > tr:nth-of-type(5) > td').text
        ability_raw = card_page.select_one('#mainContent > section > table:nth-of-type(3) > tbody > tr:nth-of-type(7) > td')
        self.third_ability = ''
        for ability in ability_raw:
            self.third_ability += ability.text.replace('\n', '') + '\n'
        self.third_ability = self.third_ability.rstrip('\n')
        self.third_flavor = card_page.select_one('#mainContent > section > table:nth-of-type(3) > tbody > tr:nth-of-type(9) > td').text.replace('\n', '')
        self.third_pic_url = card_page.select_one('#mainContent > section > table:nth-of-type(3) > tbody > tr:nth-child(2) > td.cardarea > div > img').get('src')

    # printで表示するためのもの、デバッグ用
    def __str__(self):
        try:
            first_card = 'name : ' + self.name + '\n' + 'pack : ' + self.pack + '\n' + 'type : ' + self.type + '\n' + 'civilization : ' + self.civilization+ '\n' + 'rarity : ' + self.rarity + '\n' \
            + 'power : ' + self.power + '\n' + 'cost : ' + self.cost + '\n' + 'race : ' + self.race + '\n' + 'ability : ' + self.ability + '\n' + 'flavor : ' + self.flavor + '\n'
            ret_value =  'first card : \n' + first_card
        except:
            return 'unlink'
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

class DuelMastersUnlinkCard:
    def __init__(self):
        self.name = 'リンク切れカードです'
    
    def __str__(self):
        return self.name

 
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
            page_driver = connect_html.GetDriver('https://dm.takaratomy.co.jp' + data_link, headless_mode)
        else:
            # 現在のタブで
            page_driver.get('https://dm.takaratomy.co.jp' + data_link)
        card_page = connect_html.GetBeautifulSoupFromDriver(page_driver)
        try:
            # カード情報をスクレイピング
            card = DuelMastersCard(card_page, data_link)
            if card.name == "unlink":
                print("リンク切れ")
                temp_box.append(DuelMastersUnlinkCard())
            else:
                # デバッグ表示、気になる人はつけるとよい
                print(card)
                # カードボックスへプール
                temp_box.append(card)
        except:
            print("リンク切れ")
            temp_box.append(DuelMastersUnlinkCard())
    if page_driver is not None:
        connect_html.ReleaseDriver(page_driver)
    return temp_box

def GetCardList(html):
    return html.select("#cardlist > ul > li")

def TotalCardCount(html):
    return html.select_one('#total_count').text

# csv書き出し用関数
def WriteCardBoxHeader(writer):
    if writer is None:
        return
    writer.writerow(['収録弾', 'カード名', 'カードの種類', '文明', 'レアリティ', 'パワー', 'コスト', 'マナ','種族', '特殊能力', 'フレーバー', '画像リンク', 'カード名 2', 'カードの種類 2', '文明 2', 'レアリティ 2', 'パワー 2', 'コスト 2', 'マナ 2','種族 2', '特殊能力 2', 'フレーバー 2', '画像リンク 2','カード名 3', 'カードの種類 3', '文明 3', 'レアリティ 3', 'パワー 3', 'コスト 3', 'マナ 3','種族 3', '特殊能力 3', 'フレーバー 3', '画像リンク 3'])

def WriteCardCSV(writer, card, page):
    data = []
    empty = ['', '', '', '', '', '', '','', '', '', '']
    try:
        first_card = [card.pack, card.name, card.type, card.civilization, card.rarity, card.power, card.cost, card.mana, card.race, card.ability, card.flavor, card.pic_url]
        data.extend(first_card)
    except:
        data.append('')
        data.extend(empty)
        data[1] = 'unlink card page : ' + str(page)
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
    writer.writerow(data)

def WriteCardBoxCSV(writer, card_box, page):
    for card in card_box:
        WriteCardCSV(writer, card, page)


# カードボックス
class DuelMastersCardBox:
    def __init__(self, driver, start_index, write_file, target_name = None):
        # csvの書き込み用
        self.writer = csv.writer(write_file)
        # 以下スクレイピング用
        self.driver = driver
        html = connect_html.GetBeautifulSoupFromDriver(self.driver)
        page_box = html.select('#cardlist > div > div')
        for page in reversed(page_box[0].contents):
            if page != ' ':
                try:
                    self.page_count = page['data-page']
                except:
                    self.page_count = page.text
                break
        self.card_access_list = []
        self.card_box = []
        # 何ページ目から検索するか
        start_page = 1
        start_card = 0
        # 既存のCSVが存在している場合
        if start_index > 1:
            # デュエマに存在するカード枚数を取得
            card_total_count = TotalCardCount(html)
            # すでに最大枚数取得している場合は新規カードはないので終了
            if start_index >= int(card_total_count):
                print("既に最新のデータです")
                return
            # 復帰する必要が出てきたので、1ページに存在する最大数を取得
            page_card_max_count = len(html.select("#cardlist > ul > li"))
            # ページの復帰場所
            start_page = int(start_index / page_card_max_count) + 1
            # カードの復帰場所
            start_card = int(start_index % page_card_max_count)
        else:
            # 差分作成用にはヘッダーいらない
            if target_name == None:
                # ヘッダー作成
                WriteCardBoxHeader(self.writer)
        global thread_count
        # 0以下ならCPUにとって最適なコア数に
        if thread_count < 0:
            # CPUの論理コア数取得
            thread_count = psutil.cpu_count()
        # ページの復帰処理
        self.RecoverPage(self.driver, start_page)
        # ここで一旦待ち、ページのロードが終わっていない可能性
        time.sleep(1)
        # 各ページ用
        for page in range(start_page, int(self.page_count) + 1):
            print('page : ' + str(page) + '\n')
            # 次のページへジャンプ
            if int(page) > 1:
                html = self.PageJump(self.driver, page)
            # カードリスト取得
            card_list = GetCardList(html)
            # カードの復帰処理
            if start_card > 0:
                del card_list[0 : start_card]
                start_card = 0
            # カードリストから実際にカードを取得
            self.page_card_box = self.ScrapingCardInfo(card_list)
            # 対象カードが設定されているのであればそこで打ち止め
            hit = False
            if target_name != None:
                for index in range(0, len(self.page_card_box)):
                    if self.page_card_box[index].name == target_name:
                        hit = True
                        del self.page_card_box[index:]
                        break                        
            # csv書き出し
            if write_file is not None:
                WriteCardBoxCSV(self.writer, self.page_card_box, page)
            if hit:
                return

    # TODO PageJumpと統合
    def RecoverPage(self, driver, start_page):
        if int(start_page) <= 1:
            return
        # 2ページ目の要素を書き換え
        driver.execute_script("document.querySelector('#cardlist > div > div > a:nth-child(2)').dataset.page=" + str(start_page - 1) + ";")
        # 2ページ目の要素を書き換えたので2ページ目のボタンを押す
        link = self.driver.find_element_by_link_text(str(2))
        link.click()
        # 以下ajaxの読み込み完了待ち
        wait = WebDriverWait(driver, 100)
        wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

    def PageJump(self, page_driver, page):
        link = page_driver.find_element_by_link_text(str(page))
        link.click()
        # 以下ajaxの読み込み完了待ち
        wait = WebDriverWait(page_driver, 100)
        wait.until(lambda driver: page_driver.execute_script('return jQuery.active') == 0)
        wait.until(lambda driver: page_driver.execute_script('return document.readyState') == 'complete')
        # 更新されたページのhtmlを取得する
        return connect_html.GetBeautifulSoupFromDriver(page_driver)

    def ScrapingCardInfo(self, card_list):
        page_card_box = []
        # マルチスレッドモード
        if thread_count > 0:
            # スレッド数分に分割
            split_card_list = SplitList(card_list, thread_count)
            # マルチスレッドによるカードデータの収集
            with concurrent.futures.ThreadPoolExecutor(max_workers = thread_count) as executor:
                results = list(executor.map(CardPageProcedure, split_card_list))
            # 各スレッドの結果を結合
            for result in results:
                page_card_box.extend(result)
        else:
            # シングルスレッドモード
            page_card_box = CardPageProcedure(card_list)    
        return page_card_box
