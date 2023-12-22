import argparse
import os
from ErrorAnalyzer import ErrorAnalyzer
from FailureDataCollector import FailureDataCollectorCliParser
import matplotlib.pyplot as plt
from ResultVisualizer import ResultVisualizer

parser = argparse.ArgumentParser(description="Analyse graalpy failures")
parser.add_argument(
    "-gx",
    "--graalpy-xml",
    help="Name of the JunitXML-file with graalpy results",
    default="graalpy-test-results.xml",
)
parser.add_argument(
    "-cx",
    "--cpython-xml",
    help="Name of the JunitXML-file with cpython results",
    default="cpython-test-results.xml",
)
parser.add_argument(
    "-gf",
    "--graalpy-folder",
    help="Name of the folder with graalpy results",
    required=True,
)
parser.add_argument(
    "-cf",
    "--cpython-folder",
    help="Name of the folder with cpython results",
    required=True,
)

parser.add_argument(
    "-p",
    "--print-general-information",
    help="print general information about the test results",
    action="store_true",
)

parser.add_argument("-ft", "--filter-type", help="filter error type by regex")
parser.add_argument("-fm", "--filter-message", help="filter error message by regex")
parser.add_argument("-fs", "--filter-stacktrace", help="filter stacktrace by regex")
parser.add_argument("-fp", "--filter-package", help="filter package by regex")

parser.add_argument(
    "-sh",
    "--show-hist",
    help="show histogram of error types, message, package and last stacktrace line",
    action="store_true",
)
parser.add_argument(
    "-sht",
    "--show-hist-type",
    help="show histogram of error types",
    action="store_true",
)
parser.add_argument(
    "-gt",
    "--group-type",
    help="group failures with passing regex expression of the error type for error type histogram (list possible)",
    nargs="+",
)
parser.add_argument(
    "-shm",
    "--show-hist-message",
    help="show histogram of error messages",
    action="store_true",
)
parser.add_argument(
    "-gm",
    "--group-message",
    help="group failures with passing regex expression of the error message for error message histogram (list possible)",
    nargs="+",
)
parser.add_argument(
    "-shp",
    "--show-hist-package",
    help="show histogram of packages",
    action="store_true",
)
parser.add_argument(
    "-gp",
    "--group-package",
    help="group failures with passing regex expression of the error package for package histogram (list possible)",
    nargs="+",
)
parser.add_argument(
    "-shl",
    "--show-hist-last-lines",
    help="show histogram of last stacktrace lines",
    action="store_true",
)
parser.add_argument(
    "-gl",
    "--group-last-lines",
    help="group failures with passing regex expression of the last stacktrace line for the last stacktrace line histogram (list possible)",
    nargs="+",
)

parser.add_argument(
    "-ptt", "--print-top-types", help="print top error types", action="store_true"
)
parser.add_argument(
    "-ptm", "--print-top-messages", help="print top error messages", action="store_true"
)
parser.add_argument(
    "-ptl",
    "--print-top-last-lines",
    help="print top last stacktrace lines",
    action="store_true",
)
parser.add_argument(
    "-pe", "--print-everything", help="print everything", action="store_true"
)

parser.add_argument(
    "--plot-tfidf-messages", help="plot tfidf of error messages", action="store_true"
)
parser.add_argument(
    "--plot-tfidf-stacktraces",
    help="plot tfidf of error stacktraces",
    action="store_true",
)
parser.add_argument(
    "--plot-tfidf-last-lines",
    help="plot tfidf of last error stacktrace lines",
    action="store_true",
)

parser.add_argument(
    "--print-tfidf-stacktraces",
    help="print tfidf of error stacktraces",
    action="store_true",
)
parser.add_argument(
    "--print-tfidf-last-lines",
    help="print tfidf of last error stacktrace lines",
    action="store_true",
)

if __name__ == "__main__":
    args = parser.parse_args()

    cli_parser = FailureDataCollectorCliParser(args)
    root_analyzer = ErrorAnalyzer(cli_parser)
    if args.filter_type:
        root_analyzer = root_analyzer.filter_error_type(args.filter_type)
    if args.filter_message:
        root_analyzer = root_analyzer.filter_error_message(args.filter_message)
    if args.filter_stacktrace:
        root_analyzer = root_analyzer.filter_stacktrace(args.filter_stacktrace)
    if args.filter_package:
        root_analyzer = root_analyzer.filter_packages(args.filter_package)

    if args.show_hist_type or args.show_hist:
        analyzer = root_analyzer
        for error_type in args.group_type or list():
            analyzer = analyzer.group_error_type(error_type)
        visualizer = ResultVisualizer(analyzer)
        visualizer.plot_hist_error_types()
    if args.show_hist_message or args.show_hist:
        analyzer = root_analyzer
        for error_message in args.group_message or list():
            analyzer = analyzer.group_error_message(error_message)
        visualizer = ResultVisualizer(analyzer)
        visualizer.plot_hist_error_messages()
    if args.show_hist_package or args.show_hist:
        analyzer = root_analyzer
        for package in args.group_package or list():
            analyzer = analyzer.group_packages(package)
        visualizer = ResultVisualizer(analyzer)
        visualizer.plot_hist_packages()
    if args.show_hist_last_lines or args.show_hist:
        analyzer = root_analyzer
        for last_line in args.group_last_lines or list():
            analyzer = analyzer.group_last_lines(last_line)
        visualizer = ResultVisualizer(analyzer)
        visualizer.plot_hist_last_stacktrace_lines()

    visualizer = ResultVisualizer(root_analyzer)
    if args.print_general_information:
        visualizer.print_general_information()
    if args.print_top_types:
        visualizer.print_top_error_types()
    if args.print_top_messages:
        visualizer.print_top_error_messages()
    if args.print_top_last_lines:
        visualizer.print_top_error_last_stacktrace_lines()
    if args.print_everything:
        visualizer.print_everything()
    if args.plot_tfidf_messages:
        visualizer.plot_tfidf_error_messages()
    if args.plot_tfidf_stacktraces:
        visualizer.plot_tfidf_error_stacktraces()
    if args.plot_tfidf_last_lines:
        visualizer.plot_tfidf_last_stacktrace_lines()
    if args.print_tfidf_stacktraces:
        visualizer.print_tfidf_error_stacktraces(0.8, 0.95)
    if args.print_tfidf_last_lines:
        visualizer.print_tfidf_last_stacktrace_lines(0.8, 0.95)
    plt.show()
