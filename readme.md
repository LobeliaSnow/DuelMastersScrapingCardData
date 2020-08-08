# readme
- Python3.7で開発しています
- urllib,beautifusoup4,seleniumに依存しています
- これはデュエルマスターズのカードデータをすべてcsv化するプログラムです
- 絶対に強制終了しないでください、裏で非表示のchromeとchromedriveがゾンビ化します(タスクキルは可能だが量が膨大)
- ajaxの都合ですべてchromeで開きながら行っているため、非常に低速です
- 別途同階層にenviorment.iniを作成すれば、環境変数を設定できる
  - 例 enviorment.ini
  - [settings]  
  chrome_driver_path = C:\Users\XXX\AppData\Local\Programs\Python\Python37\Lib\site-packages\chromedriver_binary\chromedriver.exe
  headless_mode = True
  - chrome_driver_pathはchromedriverへのパス
  - headless_modeはchromeを非表示にするかどうか
