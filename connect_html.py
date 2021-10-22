# HTMLアクセスの汎用メソッド群

from urllib import request
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def GetDriver(url, headless = True):
    # ブラウザのオプションを格納する変数をもらってきます。
    # Headlessモードを有効にする（コメントアウトするとブラウザが実際に立ち上がります）
    options = webdriver.ChromeOptions()
    options.set_headless(headless)
    # profile_path = "C:\\Users\\black\\AppData\\Local\\Google\\Chrome\\User Data"
    # os.makedirs(profile_path, exist_ok=True)
    # options.add_argument('--user-data-dir=' + profile_path)

    # ブラウザを起動する
    driver = webdriver.Chrome(chrome_options = options, executable_path = ChromeDriverManager().install())
    driver.set_page_load_timeout(120)
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
    try:
        driver.close()
        driver.quit()
    except:
        pass

def GetBeautifulSoupFromHTML(url):
    html = request.urlopen(url)
    return BeautifulSoup(html, 'html.parser')