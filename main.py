import csv
import dataclasses
import sys
import time

import mysql.connector
from locust import task, User, constant, events


connection = mysql.connector.connect(
    user='user',
    password='password',
    host='localhost',
    database='sample'
)


@dataclasses.dataclass
class Log:
    time: str
    sql: str
    hash: str


class EchoUser(User):

    def wait_time(self):
        return 0.8

    def on_start(self):
        with open('parsed_general_log2.log') as f:
            reader = csv.reader(f)
            self._logs: list[Log] = [Log(time=row[0], sql=row[3], hash=row[4]) for row in reader]

    @task
    def execute_sql(self):
        cursor = connection.cursor(buffered=True)
        log: Log = self._logs.pop(0)
        start = time.time()
        cursor.execute(log.sql)
        end = time.time()

        connection.commit()
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
