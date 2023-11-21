import codecs
import csv
import hashlib
import re

from re import Pattern

REG = r'\A(?P<time>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[A-Z]+)\s+(?P<id>\d+)\s+(?P<command>\w+)\b(?P<argument>.*)'
pattern: Pattern = re.compile(REG)


def parse_general_log(file_name: str):
    logs = normalize_general_log(file_name)

    with open(f'normalized_{file_name}', 'w', newline='') as f:
        writer = csv.writer(f)

        for log in logs:
            m = pattern.match(log)
            if m:
                time = m.group('time')
                id = m.group('id')
                command = m.group('command')
                argument = m.group('argument').strip()
                sql_id = hashlib.sha256(argument.encode()).hexdigest().strip()
                writer.writerow([time, id, command, argument, sql_id])


def normalize_general_log(file_name: str) -> list[str]:
    with codecs.open(file_name, 'r', 'utf-8') as f:
        new_lines = []
        lines: list[str] = f.readlines()
        cursor = 0
        while len(lines) > cursor:
            new_line, cursor = normalize_sql(lines, cursor)
            new_lines.append(new_line)

        return new_lines


def normalize_sql(lines: list[str], cursor: int) -> tuple[str, int]:
    line = lines[cursor].strip().replace('\n', '')
    if len(lines) == cursor + 1:
        return line, cursor + 1

    next_line = lines[cursor + 1]
    if pattern.match(next_line):
        return line, cursor + 1

    new_line, cursor = normalize_sql(lines, cursor + 1)
    return line + ' ' + new_line, cursor


if __name__ == '__main__':
    file_name = 'general.log'
    parse_general_log(file_name)
