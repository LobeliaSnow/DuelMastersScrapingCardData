# readme
- これはデュエルマスターズのカードデータをすべてcsv化するプログラムです
- Python3.7で開発しています(Python3.9で実行可能なことを確認済み)
- requests,beautifusoup4,selenium,configparser,psutilに依存しています、Python3系でpip installしてから使用してください
- 現在、タカラトミーのページでいくつかリンク切れを起こしています、カード名がunlink cardとして保存されますので、必要であれば手動対応お願いします。
- 強制終了しないでください、裏で非表示のchromeとchromedriveがゾンビ化する可能性があります(タスクキルは可能だが量が膨大)
- ajaxの都合ですべてchromeで開きながら行っているため、非常に低速です
- 別途同階層にenviorment.iniを作成すれば、実行時の設定ができます
  - 例 enviorment.ini
  - [settings]  
  chrome_driver_path = C:\Users\XXX\AppData\Local\Programs\Python\Python37\Lib\site-packages\chromedriver_binary\chromedriver.exe  
  headless_mode = True  
  export_path = master  
  thread_count = -1
  - chrome_driver_pathはchromedriverへのパス
  - headless_modeはchromeを非表示にするかどうか
  - thread_countは何スレッド使用して動かすかの設定、-1でCPUの論理コア数分、0でシングルスレッドモード、それ以上でその数分のスレッドの生成
- 途中でエラーで落ちても、その場所から復元できるようにはなっています
- このプログラムの利用に対する責任を作者は一切持ちません、すべて自己責任での利用をよろしくお願いいたします
