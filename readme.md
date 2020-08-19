# readme
- Python3.7で開発しています
- urllib,beautifusoup4,selenium,configparser,psutilに依存しています
- これはデュエルマスターズのカードデータをすべてcsv化するプログラムです
- 現在、タカラトミーのページでいくつかリンク切れを起こしています、対象のカードにつきましては別ファイルの手動対応リスト.txtを確認ください
- 絶対に強制終了しないでください、裏で非表示のchromeとchromedriveがゾンビ化します(タスクキルは可能だが量が膨大)
- ajaxの都合ですべてchromeで開きながら行っているため、非常に低速です
- 別途同階層にenviorment.iniを作成すれば、環境変数を設定できます
  - 例 enviorment.ini
  - [settings]  
  chrome_driver_path = C:\Users\XXX\AppData\Local\Programs\Python\Python37\Lib\site-packages\chromedriver_binary\chromedriver.exe  
  headless_mode = True  
  master_path = master.csv  
  thread_count = -1
  - chrome_driver_pathはchromedriverへのパス
  - headless_modeはchromeを非表示にするかどうか
  - thread_countは何スレッド使用して動かすかの設定、-1でCPUの論理コア数分、0でシングルスレッドモード、それ以上でその数分のスレッドの生成
- 途中でエラーで落ちても、その場所まで復元できるようにはなっています
- 現状更新機能が付いていないです、追加予定の機能ですが現状で更新したい場合は別ファイルとして作成するしかありません。
- 無理に既存ファイルに書こうとすると末尾が重複しますのでご注意ください
- このプログラムの利用に対する責任を作者は一切持ちません、すべて自己責任での利用をよろしくお願いいたします
