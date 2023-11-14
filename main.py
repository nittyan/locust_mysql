import csv
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


class EchoUser(User):
    # wait_time = constant(0.8)

    def wait_time(self):
        return 0.8

    def on_start(self):
        with open('parsed_general_log2.log') as f:
            reader = csv.reader(f)
            self._sqls = [(row[3], row[4]) for row in reader]

    @task
    def execute_sql(self):
        cursor = connection.cursor(buffered=True)
        sql: tuple[str, str] = self._sqls.pop(0)
        start = time.time()
        cursor.execute(sql[0])
        end = time.time()

        connection.commit()
        result = 0
        if cursor.rowcount:
            if not sql[0].lower().find('insert') > 0:
                result = cursor.fetchall()

        events.request.fire(
            request_type='sql',
            name=sql[1],
            response_time=float(end - start) * 1000,
            response_length=sys.getsizeof(result),
            # exception=
        )
        cursor.close()
        if not self._sqls:
            self.stop()
