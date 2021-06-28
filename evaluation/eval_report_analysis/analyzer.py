from typing import Dict, List

from evaluation.eval_report_analysis.eval_report_choice import EvalReportChoice


class EvalReportAnalyzer:

    def __init__(self, eval_reports: List[List[List[str]]]):

        self.__eval_report_entries = self.__flatten_eval_report_entries(eval_reports)

    def get_choices_per_file_pair(self) -> Dict[str, Dict[str, int]]:

        file_pairs: Dict[str, Dict[str, int]] = {}

        for eval_report_entry in self.__eval_report_entries:

            files_used = [eval_report_entry[1], eval_report_entry[2]]
            files_used.sort()

            name = f'{eval_report_entry[0]} {files_used[0]}-{files_used[1]}'

            if name not in file_pairs:
                file_pairs[name] = {'First': 0, 'Second': 0, 'Both': 0, 'None': 0}

            if eval_report_entry[3] == EvalReportChoice.TRUE:
                file_pairs[name]['First'] += 1
            elif eval_report_entry[3] == EvalReportChoice.FALSE:
                file_pairs[name]['Second'] += 1
            elif eval_report_entry[3] == EvalReportChoice.BOTH:
                file_pairs[name]['Both'] += 1
            elif eval_report_entry[3] == EvalReportChoice.NONE:
                file_pairs[name]['None'] += 1

        return file_pairs

    def get_results_per_file_pair(self) -> Dict[str, Dict[str, int]]:
        file_pairs: Dict[str, Dict[str, int]] = {}

        for eval_report_entry in self.__eval_report_entries:

            files_used = [eval_report_entry[1], eval_report_entry[2]]
            files_used.sort()

            name = f'{eval_report_entry[0]} {files_used[0]}-{files_used[1]}'

            if name not in file_pairs:
                file_pairs[name] = {'True': 0, 'False': 0}

            eval_report_result = bool(eval_report_entry[4])

            if eval_report_result:
                file_pairs[name]['True'] += 1
            elif not eval_report_result:
                file_pairs[name]['False'] += 1

        return file_pairs

    @staticmethod
    def __flatten_eval_report_entries(eval_reports: List[List[List[str]]]) -> List[List[str]]:

        flattened_eval_reports = \
            [eval_report_entry for eval_report in eval_reports for eval_report_entry in eval_report]

        return flattened_eval_reports
