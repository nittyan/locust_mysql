import csv
import dataclasses
import datetime
import sys
import time

import mysql.connector
from locust import task, User, events
from sqlalchemy.pool import QueuePool

import conf


def get_connection():
    return mysql.connector.connect(
        user=conf.user,
        password=conf.password,
        host=conf.host,
        database=conf.database,
        port=conf.port
    )


@dataclasses.dataclass
class Log:
    time: str
    sql: str
    hash: str


class LazyLogReader:

    def __init__(self, path: str):
        self._path = path

    def read_log(self) -> Log:
        with open(self._path, 'r') as f:
            reader = csv.reader(f)
            for line in reader:
                yield Log(time=line[0], sql=line[3], hash=line[4])


class DBClient(User):

    def wait_time(self):
        if len(self._logs) > 1:
            return (datetime.datetime.fromisoformat(self._logs[1].time) - datetime.datetime.fromisoformat(self._logs[0].time)).total_seconds()
        return 0

    def on_start(self):
        self._queue_pool = QueuePool(get_connection, pool_size=10)
        reader = LazyLogReader('normalized_general.log')
        self._log_gen = reader.read_log()
        # 最初の3行分だけ先に読み込む
        self._logs: list[Log] = [next(self._log_gen), next(self._log_gen), next(self._log_gen)]

    @task
    def execute_sql(self):
        connection = self._queue_pool.connect()
        cursor = connection.cursor(buffered=True)
        log: Log = self._logs.pop(0)
        try:
            next_log = next(self._log_gen)
            if next_log:
                self._logs.append(next_log)
        except StopIteration:
            # generator が値を返さない場合は処理を無視
            pass

        start = time.time()
        try:
            cursor.execute(log.sql)

            result = 0
            if cursor.rowcount:
                if not log.sql.lower().find('insert') > 0:
                    result = cursor.fetchall()

            events.request.fire(
                request_type='sql',
                name=log.hash,
                response_time=float(time.time() - start) * 1000,
                response_length=sys.getsizeof(result),
            )
        except Exception as e:
            events.request.fire(
                request_type='sql',
                name=log.hash,
                response_time=float(time.time() - start) * 1000,
                response_length=0,
                excption=e
            )

        finally:
            cursor.close()

        if not self._logs:
            self.stop()
