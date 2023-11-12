## 実行
### シンプル実行
web ui から設定をいじって実行
locust -f テストファイル名

### 設定ファイルから実行
locust --config=設定ファイル

### 結果をcsv出力する
3秒実行してファイル名に結果を出力
locust -f テストファイル名 --csv=ファイル名 --headless -t3s


### オプション
https://docs.locust.io/en/stable/configuration.html
