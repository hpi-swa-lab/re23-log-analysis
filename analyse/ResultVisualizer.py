from ErrorAnalyzer import ErrorAnalyzer
import pandas as pd
from utils import create_heatmap

class ResultVisualizer:
    def __init__(self, analyzer: ErrorAnalyzer):
        self.analyzer: ErrorAnalyzer = analyzer

    def print_general_information(self):
        graalpy_error_count, both_error_count, cpython_error_count = self.analyzer.general_information()
        print("Graalpy error count: {}".format(graalpy_error_count))
        print("Both error count: {}".format(both_error_count))
        print("Cpython error count: {}".format(cpython_error_count))

    def plot_hist_error_types(self):
        error_counts = self.analyzer.count_error_types()
        df = pd.DataFrame.from_dict(error_counts, orient='index')
        df.plot(subplots=True, kind='bar', rot=0.0, title="Error types")
    
    def print_top_error_types(self, top=10):
        print("--- TOP {} ERROR TYPES ---".format(top))
        error_counts = self.analyzer.count_error_types()
        self._print_top_error(error_counts, top)
    
    def plot_hist_error_messages(self, minimum=3):
        error_counts = self.analyzer.count_error_messages()
        important_error_counts = {error: count for error, count in error_counts.items() if count >= minimum}
        df = pd.DataFrame.from_dict(important_error_counts, orient='index')
        df.plot(subplots=True, kind='bar', title="Error messages")
    
    def print_top_error_messages(self, top=10):
        print("--- TOP {} ERROR MESSAGES ---".format(top))
        error_counts = self.analyzer.count_error_messages()
        self._print_top_error(error_counts, top)
    
    def plot_hist_last_stacktrace_lines(self, minimum=3):
        error_counts = self.analyzer.count_last_lines()
        important_error_counts = {error: count for error, count in error_counts.items() if count >= minimum}
        df = pd.DataFrame.from_dict(important_error_counts, orient='index')
        df.plot(subplots=True, kind='bar', title="Last lines")
    
    def print_top_error_last_stacktrace_lines(self, top=10):
        print("--- TOP {} LAST LINES ---".format(top))
        error_counts = self.analyzer.count_last_lines()
        self._print_top_error(error_counts, top)
    
    def plot_hist_packages(self):
        package_counts = self.analyzer.count_packages()
        df = pd.DataFrame.from_dict(package_counts, orient='index')
        df.plot(subplots=True, kind='bar', title="Packages")
    
    def print_everything(self):
        for errorDocument in self.analyzer.graalpy_error_documents:
            print(errorDocument)
            print()

    def plot_tfidf_error_messages(self):
        errors, similarity = self.analyzer.calculate_similarity_messages()
        labels = [error[:20] for error in errors]
        create_heatmap(similarity, labels, "TF-IDF Error Messages")
        
    def plot_tfidf_error_stacktraces(self):
        errors, similarity = self.analyzer.calculate_similarity_stacktraces()
        labels = [error[:20] for error in errors]
        create_heatmap(similarity, labels, "TF-IDF Stacktraces")
    
    def plot_tfidf_last_stacktrace_lines(self):
        errors, similarity = self.analyzer.calculate_similarity_last_stacktrace_lines()
        labels = [error[:20] for error in errors]
        create_heatmap(similarity, labels, "TF-IDF Last Stacktrace Line")

    def print_tfidf_error_stacktraces(self, bottom_limit, top_limit, top=10):
        print("--- SIMILAR ERROR STACKTRACES ---")
        errors, similarity = self.analyzer.calculate_similarity_stacktraces()
        self._print_tfidf(similarity, errors, bottom_limit, top_limit, top)
    
    def print_tfidf_last_stacktrace_lines(self, bottom_limit, top_limit, top=10):
        print("--- SIMILAR LAST STACKTRACE LINE ---")
        errors, similarity = self.analyzer.calculate_similarity_last_stacktrace_lines()
        self._print_tfidf(similarity, errors, bottom_limit, top_limit, top)
    
    def _print_tfidf(self, similarity, errors, bottom_limit, top_limit, top):
        interested_index = []
        for i in range(len(similarity)):
            for j in range(len(similarity[i]) - i - 1):
                if similarity[i][j] > bottom_limit and similarity[i][j] < top_limit:
                    interested_index.append((i, j))
        sorted_interested_index = sorted(interested_index, key=lambda x: similarity[x[0]][x[1]], reverse=True)
        for i, j in sorted_interested_index[:top]:
            print("Similarity: {}".format(similarity[i][j]))
            print("Error 1: {}".format(errors[i]))
            print("--------------------")
            print("Error 2: {}".format(errors[j]))
            print("####################")

    
    def _print_top_error(self, error_counts, top):
        for error, count in error_counts.most_common(top):
            print("#{} - {}".format(count, error))