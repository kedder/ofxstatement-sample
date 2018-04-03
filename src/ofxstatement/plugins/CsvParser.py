import csv

from ofxstatement.parser import CsvStatementParser
from ofxstatement.statement import Statement, StatementLine


def is_valid(statement_line):
    try:
        statement_line.assert_valid()
        return True
    except AssertionError:
        return False


def create_statement(statement_lines):
    statement = Statement()
    for statement_line in statement_lines:
        if is_valid(statement_line):
            statement.lines.append(statement_line)
    return statement


class CsvParser(CsvStatementParser):
    def my_parse(self, file_stream, csv_dialect):
        lines = csv.reader(file_stream, csv_dialect)
        records = self.parse_lines(lines)
        return create_statement(records)

    def parse_lines(self, lines):
        records = []
        for line in lines:
            records += self.parse_record(line)
        return records

    def parse_value(self, value, field):
        return super().parse_value(value, field)

    def parse_record(self, line):
        statement_line = StatementLine()
        for field, col_number in self.mappings.items():
            state = State(field, self.parse_value)

            raw_value = self.get_nth_value(line, col_number)
            value = raw_value.flatmap(state.execute)
            setattr(statement_line, field, value)
        return statement_line

    @staticmethod
    def get_nth_value(line, col_number):
        if col_number >= len(line):
            return Nothing
        return Just(line[col_number])


class State(object):
    def __init__(self, state, fun):
        self.state = state
        self.fun = fun

    def execute(self, value):
        self.fun(value, self.state)


class Maybe(object):
    def flatmap(self, f):
        if isinstance(self, Nothing):
            return Nothing
        return f(self.value)


class Just(Maybe):
    def __init__(self, value):
        self.value = value


class Nothing(Maybe):
    pass
