# HTMLアクセスの汎用メソッド群

from urllib import request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def GetDriver(url,driver_path = 'chromedriver', headless = True):
    # ブラウザのオプションを格納する変数をもらってきます。
    options = Options()
    # Headlessモードを有効にする（コメントアウトするとブラウザが実際に立ち上がります）
    options.set_headless(headless)
    # ブラウザを起動する
    driver = webdriver.Chrome(chrome_options = options, executable_path = driver_path)
    # ブラウザでアクセスする
    driver.get(url)
    return driver

def GetBeautifulSoupFromDriver(driver):
    # HTMLを文字コードをUTF-8に変換してから取得します。
    html = driver.page_source.encode('utf-8')
    # BeautifulSoupで扱えるようにパースします
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def ReleaseDriver(driver):
    driver.close()
    driver.quit()


def GetBeautifulSoupFromHTML(url):
    html = request.urlopen(url)
    return BeautifulSoup(html, 'html.parser')