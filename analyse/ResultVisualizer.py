from ErrorAnalyzer import ErrorAnalyzer
import pandas as pd
from utils import create_heatmap


class ResultVisualizer:
    """
    Class to visualize or print the results of the ErrorAnalyzer with different plots.
    """

    def __init__(self, analyzer: ErrorAnalyzer):
        self.analyzer: ErrorAnalyzer = analyzer

    def print_general_information(self):
        """
        Print information about the number of errors in the different categories.
        """
        (
            graalpy_error_count,
            both_error_count,
            cpython_error_count,
        ) = self.analyzer.general_information()
        print("Graalpy error count: {}".format(graalpy_error_count))
        print("Both error count: {}".format(both_error_count))
        print("Cpython error count: {}".format(cpython_error_count))

    def plot_hist_error_types(self):
        """
        Plot a histogram about the distribution of the error types.
        """
        error_counts = self.analyzer.count_error_types()
        df = pd.DataFrame.from_dict(error_counts, orient="index")
        df.plot(subplots=True, kind="bar", rot=0.0, title="Error types")

    def print_top_error_types(self, top=10):
        """
        Print the top error types.
        """
        print("--- TOP {} ERROR TYPES ---".format(top))
        error_counts = self.analyzer.count_error_types()
        self._print_top_error(error_counts, top)

    def plot_hist_error_messages(self, minimum=0):
        """
        Plot a histogram about the distribution of the error messages.
        """
        error_counts = self.analyzer.count_error_messages()
        important_error_counts = {
            error: count for error, count in error_counts.items() if count >= minimum
        }
        df = pd.DataFrame.from_dict(important_error_counts, orient="index")
        df.plot(subplots=True, kind="bar", title="Error messages")

    def print_top_error_messages(self, top=10):
        """
        Print the top error messages.
        """
        print("--- TOP {} ERROR MESSAGES ---".format(top))
        error_counts = self.analyzer.count_error_messages()
        self._print_top_error(error_counts, top)

    def plot_hist_last_stacktrace_lines(self, minimum=0):
        """
        Plot a histogram about the distribution of the last stacktrace lines.
        """
        error_counts = self.analyzer.count_last_lines()
        important_error_counts = {
            error: count for error, count in error_counts.items() if count >= minimum
        }
        df = pd.DataFrame.from_dict(important_error_counts, orient="index")
        df.plot(subplots=True, kind="bar", title="Last lines")

    def print_top_error_last_stacktrace_lines(self, top=10):
        """
        Print the top last stacktrace lines.
        """
        print("--- TOP {} LAST LINES ---".format(top))
        error_counts = self.analyzer.count_last_lines()
        self._print_top_error(error_counts, top)

    def plot_hist_packages(self):
        """
        Plot a histogram about the distribution of the packages.
        """
        package_counts = self.analyzer.count_packages()
        df = pd.DataFrame.from_dict(package_counts, orient="index")
        df.plot(subplots=True, kind="bar", title="Packages")

    def print_everything(self):
        """
        Print all graalpy error documents.
        """
        for errorDocument in self.analyzer.graalpy_error_documents:
            print(errorDocument)
            print()

    def plot_tfidf_error_messages(self):
        """
        Plot a heatmap about the similarity of the error messages.
        """
        errors, similarity = self.analyzer.calculate_similarity_messages()
        labels = [error[:20] for error in errors]
        create_heatmap(similarity, labels, "TF-IDF Error Messages")

    def plot_tfidf_error_stacktraces(self):
        """
        Plot a heatmap about the similarity of the complete stacktraces.
        """
        errors, similarity = self.analyzer.calculate_similarity_stacktraces()
        labels = [error[:20] for error in errors]
        create_heatmap(similarity, labels, "TF-IDF Stacktraces")

    def plot_tfidf_last_stacktrace_lines(self):
        """
        Plot a heatmap about the similarity of the last stacktraces lines.
        """
        errors, similarity = self.analyzer.calculate_similarity_last_stacktrace_lines()
        labels = [error[:20] for error in errors]
        create_heatmap(similarity, labels, "TF-IDF Last Stacktrace Line")

    def print_tfidf_error_stacktraces(self, bottom_limit, top_limit, top=10):
        """
        Print the top similar stacktraces.
        """
        print("--- SIMILAR ERROR STACKTRACES ---")
        errors, similarity = self.analyzer.calculate_similarity_stacktraces()
        self._print_tfidf(similarity, errors, bottom_limit, top_limit, top)

    def print_tfidf_last_stacktrace_lines(self, bottom_limit, top_limit, top=10):
        """
        Print the top similar last stacktraces lines.
        """
        print("--- SIMILAR LAST STACKTRACE LINE ---")
        errors, similarity = self.analyzer.calculate_similarity_last_stacktrace_lines()
        self._print_tfidf(similarity, errors, bottom_limit, top_limit, top)

    def _print_tfidf(self, similarity, errors, bottom_limit, top_limit, top):
        """
        Helpful function to print the top similar stacktraces or last stacktrace lines.
        """
        interested_index = []
        for i in range(len(similarity)):
            for j in range(len(similarity[i]) - i - 1):
                # Only interested in the top similar stacktraces
                if similarity[i][j] > bottom_limit and similarity[i][j] < top_limit:
                    interested_index.append((i, j))
        # Sort by similarity
        sorted_interested_index = sorted(
            interested_index, key=lambda x: similarity[x[0]][x[1]], reverse=True
        )
        for i, j in sorted_interested_index[:top]:
            print("Similarity: {}".format(similarity[i][j]))
            print("Error 1: {}".format(errors[i]))
            print("--------------------")
            print("Error 2: {}".format(errors[j]))
            print("####################")

    def _print_top_error(self, error_counts, top):
        """
        Helpful function to print the top error types, messages or last stacktrace lines.
        """
        for error, count in error_counts.most_common(top):
            print("#{} - {}".format(count, error))
