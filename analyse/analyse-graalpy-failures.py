import argparse
import os 
from ErrorAnalyser import ErrorAnalyser
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--graalpy-files', default='graalpy-test-results.xml', help='name of the JunitXML-files with graalpy results')
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
    #analyser.plot_hist_error_types()
    #analyser.plot_hist_error_messages()
    #analyser.print_top_error_messages()
    #analyser.plot_tfidf_error_messages()
    #analyser.plot_tfidf_error_stacktraces()
    #analyser.print_tfidf_error_stracktrace()
    #analyser.print_tfidf_last_stacktrace_line(0.8, 0.95)
    #analyser.plot_tfidf_last_stacktrace_line()
    plt.show()
