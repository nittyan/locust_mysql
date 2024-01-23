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


class DBClient(User):

    def wait_time(self):
        return self._wait_times.pop(0)

    def on_start(self):
        self._queue_pool = QueuePool(get_connection, pool_size=10)

        with open('normalized_general.log') as f:
            reader = csv.reader(f)
            self._logs: list[Log] = [Log(time=row[0], sql=row[3], hash=row[4]) for row in reader]
            self._wait_times: list[float] = []
            for index in range(len(self._logs) - 1):
                delta = datetime.datetime.fromisoformat(self._logs[index + 1].time) - datetime.datetime.fromisoformat(self._logs[index].time)
                self._wait_times.append(delta.total_seconds())

    @task
    def execute_sql(self):
        connection = self._queue_pool.connect()
        cursor = connection.cursor(buffered=True)
        log: Log = self._logs.pop(0)
        start = time.time()
        cursor.execute(log.sql)
        end = time.time()

        result = 0
        if cursor.rowcount:
            if not log.sql.lower().find('insert') > 0:
                result = cursor.fetchall()

        events.request.fire(
            request_type='sql',
            name=log.hash,
            response_time=float(end - start) * 1000,
            response_length=sys.getsizeof(result),
            # exception=
        )
        cursor.close()
        if not self._logs:
            self.stop()
