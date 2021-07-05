from typing import Dict, List

from evaluation.report_analysis.eval_report_choice import EvalReportChoice


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

                name = f'{files_used[0]}-{files_used[1]}'

                if name not in file_pairs:
                    file_pairs[name] = {'First': 0, 'Second': 0, 'Both': 0, 'None': 0}

                if eval_report_choice == EvalReportChoice.FIRST:
                    file_pairs[name]['First'] += 1
                elif eval_report_choice == EvalReportChoice.SECOND:
                    file_pairs[name]['Second'] += 1
                elif eval_report_choice == EvalReportChoice.BOTH:
                    file_pairs[name]['Both'] += 1
                elif eval_report_choice == EvalReportChoice.NONE:
                    file_pairs[name]['None'] += 1

            entries_by_files[entries_by_file] = file_pairs

        return entries_by_files

    def get_results_per_file_pair(self) -> Dict[str, Dict[str, Dict[str, int]]]:

        entries_by_files = {}

        for entries_by_file in self.__eval_report_entries_by_files:
            file_pairs: Dict[str, Dict[str, int]] = {}

            for eval_report_entry in self.__eval_report_entries_by_files[entries_by_file]:

                files_used = [eval_report_entry[1], eval_report_entry[2]]
                files_used.sort()

                name = f'{files_used[0]}-{files_used[1]}'

                if name not in file_pairs:
                    file_pairs[name] = {'True': 0, 'False': 0}

                eval_report_result = bool(eval_report_entry[4])

                if eval_report_entry[4] == 'True':
                    eval_report_result = True
                elif eval_report_entry[4] == 'False':
                    eval_report_result = False

                if eval_report_result:
                    file_pairs[name]['True'] += 1
                elif not eval_report_result:
                    file_pairs[name]['False'] += 1

            entries_by_files[entries_by_file] = file_pairs

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
