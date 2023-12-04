import argparse
import os 
from ErrorAnalyser import ErrorAnalyser
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--graalpy-files', default='graalpy-test-results.xml', help='name of the JunitXML-files with graalpy results')
parser.add_argument('--filter-error-type', help='filter error type by regex')
parser.add_argument('--filter-error-message', help='filter error message by regex')
parser.add_argument('--filter-error-stacktrace', help='filter stacktrace by regex')
parser.add_argument('--input', help='name of result folder')


if __name__ == "__main__":
    args = parser.parse_args()

    input_folder = args.input
    graalpy_files = args.graalpy_files

    files = list()
    for path, subdirs, _ in os.walk(input_folder):
        package = path.split('/')[-1]
        files.append((package, os.path.join(path, graalpy_files)))
    
    analyser = ErrorAnalyser(files)
    analyser.load()
    if args.filter_error_type:
        print("Filtering error type by {}".format(args.filter_error_type))
        analyser = analyser.filter_error_type(args.filter_error_type)
    if args.filter_error_message:
        analyser = analyser.filter_error_message(args.filter_error_message)
    if args.filter_error_stacktrace:
        analyser = analyser.filter_stacktrace(args.filter_error_stacktrace)
    #analyser.print_everything()
    #analyser.plot_hist_packages()
    #analyser.plot_hist_error_types()
    #analyser.plot_hist_error_messages()
    #analyser.print_top_error_messages()
    #analyser.plot_tfidf_error_messages()
    #analyser.plot_tfidf_error_stacktraces()
    #analyser.print_tfidf_error_stracktrace(0.8, 0.95)
    #analyser.print_tfidf_last_stacktrace_line(0.8, 0.95)
    #analyser.plot_tfidf_last_stacktrace_line()
    plt.show()
