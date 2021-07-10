from collections import OrderedDict
from typing import Dict, List

from evaluation.report_analysis.eval_report_choice import EvalReportChoice
from evaluation.report_analysis.eval_report_result import EvalReportResult


class EvalReportAnalyzer:

    def __init__(self, eval_reports: List[List[List[str]]]):

        eval_report_entries = self.__flatten_eval_report_entries(eval_reports)

        self.__eval_report_entries_by_files = self.__sort_eval_report_entries_by_file(eval_report_entries)

    def get_choices_per_file_pair(self) -> Dict[str, Dict[str, Dict[str, int]]]:

        entries_by_files = {}

        for entries_by_file in self.__eval_report_entries_by_files:
            file_pairs: Dict[str, Dict[str, int]] = {}

            for eval_report_entry in self.__eval_report_entries_by_files[entries_by_file]:

                files_used = [eval_report_entry[1], eval_report_entry[2]]
                files_used.sort()

                eval_report_choice = eval_report_entry[3]

                # switch first with second if list was sorted
                if not files_used == [eval_report_entry[1], eval_report_entry[2]]:
                    if eval_report_choice == EvalReportChoice.FIRST:
                        eval_report_choice = EvalReportChoice.SECOND
                    elif eval_report_choice == EvalReportChoice.SECOND:
                        eval_report_choice = EvalReportChoice.FIRST

                if len(files_used[1]) == 1:
                    files_used[1] = f'0{files_used[1]}'

                name = f'{files_used[0]}-{files_used[1]}'

                if name not in file_pairs:
                    file_pairs[name] = {key: 0 for key in EvalReportChoice}

                if EvalReportChoice.has_value(eval_report_choice):
                    file_pairs[name][eval_report_choice] += 1
                else:
                    print(f'eval report choice "{eval_report_choice}" does not match EvalReportChoice')

            ordered_file_pairs = OrderedDict(sorted(file_pairs.items()))

            entries_by_files[entries_by_file] = ordered_file_pairs

        return entries_by_files

    def get_results_per_file_pair(self) -> Dict[str, Dict[str, Dict[str, int]]]:

        entries_by_files = {}

        for entries_by_file in self.__eval_report_entries_by_files:
            file_pairs: Dict[str, Dict[str, int]] = {}

            for eval_report_entry in self.__eval_report_entries_by_files[entries_by_file]:

                files_used = [eval_report_entry[1], eval_report_entry[2]]
                files_used.sort()

                if len(files_used[1]) == 1:
                    files_used[1] = f'0{files_used[1]}'

                name = f'{files_used[0]}-{files_used[1]}'

                if name not in file_pairs:
                    file_pairs[name] = {key: 0 for key in EvalReportResult}

                eval_result = eval_report_entry[4]
                if EvalReportResult.has_value(eval_result):
                    file_pairs[name][eval_result] += 1
                else:
                    print(f'eval report result "{eval_result}" does not match EvalReportResult')

            ordered_file_pairs = OrderedDict(sorted(file_pairs.items()))

            entries_by_files[entries_by_file] = ordered_file_pairs

        return entries_by_files

    @staticmethod
    def __flatten_eval_report_entries(eval_reports: List[List[List[str]]]) -> List[List[str]]:

        flattened_eval_reports = \
            [eval_report_entry for eval_report in eval_reports for eval_report_entry in eval_report]

        return flattened_eval_reports

    @staticmethod
    def __sort_eval_report_entries_by_file(eval_report_entries: List[List[str]]):
        entries_by_files: Dict[str, List[List[str]]] = {}

        for eval_report_entry in eval_report_entries:
            filename = eval_report_entry[0]

            if filename not in entries_by_files:
                entries_by_files[filename] = []

            entries_by_files[filename].append(eval_report_entry)

        return entries_by_files
