import csv

from ofxstatement.parser import CsvStatementParser
from ofxstatement.plugin import Plugin
from ofxstatement.statement import Statement, StatementLine


class KhPlugin(Plugin):
    """plugin for the hungarian k&h bank
    """

    def get_parser(self, filename):
        return KhParser(filename)


class KhParser(CsvStatementParser):
    date_format = "%Y.%m.%d"
    mappings = {
        "date": 0,
        "payee": 6,
        "memo": 9,
        "amount": 7,
        "id": 1
    }
    filename = None

    def __init__(self, filename):
        self.statement = Statement(None, None, 'HUF')
        self.filename = filename

    def parse(self):
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """
        with open(self.filename, "r") as f:
            self.fin = f
            return self.parse_csv_with_header()

    def parse_csv_with_header(self):
        reader = self.split_records()
        for line in reader:
            self.cur_record += 1
            if self.cur_record == 1:
                continue
            if not line:
                continue
            stmt_line = self.parse_record(line)
            if stmt_line:
                stmt_line.assert_valid()
                self.statement.lines.append(stmt_line)
        return self.statement

    def split_records(self):
        dialect = csv.excel_tab
        return csv.reader(self.fin, dialect)

    def parse_value(self, value, field):
        return super().parse_value(value, field)

    def parse_record(self, line):
        stmt_line = StatementLine()
        for field, col in self.mappings.items():
            if col >= len(line):
                raise ValueError("Cannot find column %s in line of %s items " % (col, len(line)))
            rawvalue = line[col]
            value = self.parse_value(rawvalue, field)
            setattr(stmt_line, field, value)
        return stmt_line
