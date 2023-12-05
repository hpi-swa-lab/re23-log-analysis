import argparse
import os 
from ErrorAnalyzer import ErrorAnalyzer
from FailureDataCollector import FailureDataCollectorCliParser
import matplotlib.pyplot as plt
from ResultVisualizer import ResultVisualizer

parser = argparse.ArgumentParser(description='Analyse graalpy failures')
parser.add_argument("-gx", "--graalpy-xml", help="Name of the JunitXML-file with graalpy results", default='graalpy-test-results.xml')
parser.add_argument("-cx", "--cpython-xml", help="Name of the JunitXML-file with cpython results", default='cpython-test-results.xml')
parser.add_argument("-gf", "--graalpy-folder", help="Name of the folder with graalpy results")
parser.add_argument("-cf", "--cpython-folder", help="Name of the folder with cpython results")

parser.add_argument('-ft', '--filter-type', help='filter error type by regex')
parser.add_argument('-fm', '--filter-message', help='filter error message by regex')
parser.add_argument('-fs', '--filter-stacktrace', help='filter stacktrace by regex')
parser.add_argument('-fp', '--filter-package', help='filter package by regex')

parser.add_argument('-sht', '--show-hist-type', help='show histogram of error types', action='store_true')
parser.add_argument('-shm', '--show-hist-message', help='show histogram of error messages', action='store_true')
parser.add_argument('-shp', '--show-hist-package', help='show histogram of packages', action='store_true')

parser.add_argument('-ptt', '--print-top-types', help='print top error types', action='store_true')
parser.add_argument('-ptm', '--print-top-messages', help='print top error messages', action='store_true')
parser.add_argument('-pe', '--print-everything', help='print everything', action='store_true')

parser.add_argument('--plot-tfidf-messages', help='plot tfidf of error messages', action='store_true')
parser.add_argument('--plot-tfidf-stacktraces', help='plot tfidf of error stacktraces', action='store_true')
parser.add_argument('--plot-tfidf-last-lines', help='plot tfidf of last error stacktrace lines', action='store_true')

parser.add_argument('--print-tfidf-stacktraces', help='print tfidf of error stacktraces', action='store_true')
parser.add_argument('--print-tfidf-last-lines', help='print tfidf of last error stacktrace lines', action='store_true')

if __name__ == "__main__":
    args = parser.parse_args()

    cli_parser = FailureDataCollectorCliParser(args)
    analyzer = ErrorAnalyzer(cli_parser)
    if args.filter_type:
        analyzer = analyzer.filter_error_type(args.filter_type)
    if args.filter_message:
        analyzer = analyzer.filter_error_message(args.filter_message)
    if args.filter_stacktrace:
        analyzer = analyzer.filter_stacktrace(args.filter_stacktrace)
    if args.filter_package:
        analyzer = analyzer.filter_packages(args.filter_package)

    visualizer = ResultVisualizer(analyzer)
    if args.show_hist_type:
        visualizer.plot_hist_error_types()
    if args.show_hist_message:
        visualizer.plot_hist_error_messages()
    if args.show_hist_package:
        visualizer.plot_hist_packages()
    if args.print_top_types:
        visualizer.print_top_error_types()
    if args.print_top_messages:
        visualizer.print_top_error_messages()
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
