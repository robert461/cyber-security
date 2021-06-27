from pathlib import Path

from evaluation.eval_report_analysis.analyzer import EvalReportAnalyzer
from evaluation.eval_report_analysis.csv_reader import CsvReader
from evaluation.eval_report_analysis.visualizer import EvalReportVisualizer


def main():

    eval_reports_path = Path('../eval_reports')

    csv_reader = CsvReader(eval_reports_path)
    eval_reports = csv_reader.read_all_eval_reports()

    analyzer = EvalReportAnalyzer(eval_reports)

    choices_per_file_pair = analyzer.get_choices_per_file_pair()

    visualizer = EvalReportVisualizer()
    visualizer.draw_pandas_barh(choices_per_file_pair, 'choices_per_file_pair', 8)


if __name__ == "__main__":
    main()
