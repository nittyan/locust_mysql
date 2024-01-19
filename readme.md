# Locust_MySQL
MySQL の一般クエリーログ(ジェネラルログ)を使用して、一般クエリーログと同じ負荷をかけるサンプル。

# 実行
## コンテナの起動
```
docker compose up -d
docker ps
# 分散で負荷かけたい場合は locust-main、locust-replica が立ち上がってるか確認
# 立ち上がってない場合は少し時間をおいて
docker compose start
```
mysql へは適当にデータ投入する

## 一般クエリーログを正規化する
parse_general_log.py の file_name を適宜変えて
```
python parse_general_log.py
```
## クエリーの実行
conf.py へDBアクセスの設定を変更

main.py の一般クエリーログのログファイル名を書き換え

### シングルで実行
```
locust -f main.py
```
ブラウザで http://localhost:8089 へアクセス

### 分散実行
コンテナが実行されてることを確認して http://localhost:8088 へアクセス

## その他の実行
### 設定ファイルから実行
locust --config=設定ファイル

### 結果をcsv出力する
3秒実行してファイル名に結果を出力
locust -f テストファイル名 --csv=ファイル名 --headless -t3s


### オプション
https://docs.locust.io/en/stable/configuration.html
