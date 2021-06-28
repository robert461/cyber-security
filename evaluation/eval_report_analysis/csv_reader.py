import csv
from pathlib import Path
from typing import List


class CsvReader:

    def __init__(self, eval_reports_path: Path):
        self.__eval_reports_path = eval_reports_path

    def read_all_eval_reports(self) -> List[List[List[str]]]:
        eval_reports = []

        for eval_report_name in self.__eval_reports_path.glob("*.csv"):

            eval_report = self.__read_file_as_csv(eval_report_name)

            eval_reports.append(eval_report)

        return eval_reports

    def __read_file_as_csv(self, filename) -> List[List[str]]:

        with open(f'{self.__eval_reports_path}/{filename}') as csv_file:

            csv_reader = csv.reader(csv_file, delimiter=';', quotechar='|')
            rows: List[List[str]] = []

            for reader_row in csv_reader:
                if not reader_row[0] == 'Example Name':
                    rows.append(reader_row)

            return rows
