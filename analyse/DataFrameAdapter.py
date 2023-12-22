from ErrorAnalyzer import ErrorAnalyzer
import pandas as pd


class DataFrameAdapter(object):
    def __init__(self, analyzer: ErrorAnalyzer):
        self.analyzer: ErrorAnalyzer = analyzer

    def get_error_types_df(self):
        error_counts = self.analyzer.count_error_types()
        return (
            pd.DataFrame.from_dict(error_counts, orient="index", columns=["count"])
            .reset_index()
            .rename(columns={"index": "error type"})
            .sort_values(by=["count"], ascending=False)
        )

    def get_error_messages_df(self, minimum=3):
        error_counts = self.analyzer.count_error_messages()
        important_error_counts = {
            error: count for error, count in error_counts.items() if count >= minimum
        }
        return (
            pd.DataFrame.from_dict(
                important_error_counts, orient="index", columns=["count"]
            )
            .reset_index()
            .rename(columns={"index": "error message"})
            .sort_values(by=["count"], ascending=False)
        )

    def get_last_stacktrace_lines_df(self, minimum=3):
        error_counts = self.analyzer.count_last_lines()
        important_error_counts = {
            error: count for error, count in error_counts.items() if count >= minimum
        }
        return (
            pd.DataFrame.from_dict(
                important_error_counts, orient="index", columns=["count"]
            )
            .reset_index()
            .rename(columns={"index": "last stacktrace line"})
            .sort_values(by=["count"], ascending=False)
        )

    def get_packages_df(self):
        package_counts = self.analyzer.count_packages()
        return (
            pd.DataFrame.from_dict(package_counts, orient="index", columns=["count"])
            .reset_index()
            .rename(columns={"index": "package"})
            .sort_values(by=["count"], ascending=False)
        )
