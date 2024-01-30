from JunitXMLParser import JunitXMLParser
import os
from functools import reduce
from ErrorDocument import ErrorDocument
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from utils import tokenize
import re
from FailureDataCollector import FailureDataCollector
from tqdm import tqdm


class ErrorAnalyzer(object):
    """
    Class to calculate different statistics about the errors in the test runs.
    """

    def __init__(
        self,
        data_collector: FailureDataCollector,
        graalpy_error_documents=None,
        cpython_error_documents=None,
    ):
        self.data_collector: FailureDataCollector = data_collector
        # If no error documents are given, load them from the files
        if graalpy_error_documents is None:
            self.graalpy_error_documents = self.load(
                self.data_collector.graalpy_xml_files
            )
        else:
            self.graalpy_error_documents = graalpy_error_documents
        if cpython_error_documents is None:
            self.cpython_error_documents = self.load(
                self.data_collector.cpython_xml_files
            )
        else:
            self.cpython_error_documents = cpython_error_documents

    def load(self, files):
        error_documents = list()
        for package, file in tqdm(files):
            if os.path.isfile(file):
                xml_parser = JunitXMLParser(file)

                for (
                    testName,
                    errorType,
                    errorMessage,
                    stackTrace,
                ) in xml_parser.get_failure_stacktraces():
                    # Create a new error document for each failure
                    errorDocument = ErrorDocument(
                        testName, package, errorType, errorMessage, stackTrace
                    )
                    error_documents.append(errorDocument)
                for (
                    testName,
                    errorType,
                    errorMessage,
                    stackTrace,
                ) in xml_parser.get_error_stacktraces():
                    # Create a new error document for each error
                    errorDocument = ErrorDocument(
                        testName, package, errorType, errorMessage, stackTrace
                    )
                    error_documents.append(errorDocument)
        return error_documents

    def general_information(self):
        graalpy_error_count = len(self.error_documents)
        # Count the number of cpython errors that are also in the graalpy errors
        both_error_count = len(
            [
                errorDocument
                for errorDocument in self.cpython_error_documents
                if errorDocument.name
                in [
                    errorDocument.name for errorDocument in self.cpython_error_documents
                ]
            ]
        )
        # Calculate the number of cpython errors that are not in the graalpy errors
        cpython_error_count = len(self.cpython_error_documents) - both_error_count
        return (graalpy_error_count, both_error_count, cpython_error_count)

    def _filter(self, filter_function):
        """
        General filter function that filters the error documents from both implementations by a given filter function.
        Returns a new ErrorAnalyzer object only with the filtered error documents.
        """
        graalpy_error_documents = [
            errorDocument
            for errorDocument in self.graalpy_error_documents
            if filter_function(errorDocument)
        ]
        cpython_error_documents = [
            errorDocument
            for errorDocument in self.cpython_error_documents
            if filter_function(errorDocument)
        ]
        return ErrorAnalyzer(
            self.data_collector, graalpy_error_documents, cpython_error_documents
        )

    def filter_error_type(self, error_type):
        """
        Filter the error documents by the error type.
        Returns a new ErrorAnalyzer object only with the filtered error documents.
        """
        filter_function = (
            lambda errorDocument: errorDocument.errorType is not None
            and tokenize(error_type) in tokenize(errorDocument.errorType)
        )
        return self._filter(filter_function)

    def filter_error_message(self, error_message):
        """
        Filter the error documents by the error message.
        Returns a new ErrorAnalyzer object only with the filtered error documents.
        """
        filter_function = (
            lambda errorDocument: errorDocument.errorMessage is not None
            and tokenize(error_message) in tokenize(errorDocument.errorMessage)
        )
        return self._filter(filter_function)

    def filter_stacktrace(self, stacktrace):
        """
        Filter the error documents by the error stacktrace.
        Returns a new ErrorAnalyzer object only with the filtered error documents.
        """
        filter_function = (
            lambda errorDocument: errorDocument.stackTrace is not None
            and tokenize(stacktrace) in tokenize(errorDocument.stackTrace)
        )
        return self._filter(filter_function)

    def filter_packages(self, package):
        """
        Filter the error documents by the package.
        Returns a new ErrorAnalyzer object only with the filtered error documents.
        """
        filter_function = (
            lambda errorDocument: errorDocument.packageName is not None
            and tokenize(package) in tokenize(errorDocument.packageName)
        )
        return self._filter(filter_function)

    def _group(self, grouping_function, error_property, grouping_value):
        # Collect all error documents that match the grouping function
        grouped_error_documents = [
            errorDocument
            for errorDocument in self.graalpy_error_documents
            if grouping_function(errorDocument)
        ]
        grouped_error_names = [
            errorDocument.name for errorDocument in grouped_error_documents
        ]
        # Collect all error documents that match the grouping function and are also in the cpython error documents to avoid double counting
        grouped_cpython_error_documents = [
            errorDocument
            for errorDocument in self.cpython_error_documents
            if errorDocument.name in grouped_error_names
        ]
        # Remove grouped error documents from graalpy error documents
        graalpy_error_documents_without_group = [
            errorDocument
            for errorDocument in self.graalpy_error_documents
            if errorDocument.name not in grouped_error_names
        ]
        group_size = len(grouped_error_documents) - len(grouped_cpython_error_documents)
        # Create a new error document that represents the group and add it to the graalpy error documents
        new_graalpy_error_document = ErrorDocument(
            **{
                error_property: grouping_value,
                "value": group_size,
                "name": "group_{}_{}".format(error_property, grouping_value),
            }
        )
        # Return a new ErrorAnalyzer object with the new graalpy error documents
        return ErrorAnalyzer(
            self.data_collector,
            [*graalpy_error_documents_without_group, new_graalpy_error_document],
            self.cpython_error_documents,
        )

    def group_error_type(self, error_type):
        grouping_function = (
            lambda errorDocument: errorDocument.errorType is not None
            and tokenize(error_type) in tokenize(errorDocument.errorType)
        )
        return self._group(grouping_function, "errorType", error_type)

    def group_error_message(self, error_message):
        grouping_function = (
            lambda errorDocument: errorDocument.errorMessage is not None
            and tokenize(error_message) in tokenize(errorDocument.errorMessage)
        )
        return self._group(grouping_function, "errorMessage", error_message)

    def group_last_lines(self, last_line):
        grouping_function = (
            lambda errorDocument: errorDocument.last_stacktrace_line is not None
            and tokenize(last_line) in tokenize(errorDocument.last_stacktrace_line)
        )
        return self._group(grouping_function, "stackTrace", last_line)

    def group_packages(self, package):
        grouping_function = (
            lambda errorDocument: errorDocument.last_stacktrace_line is not None
            and tokenize(package) in tokenize(errorDocument.package)
        )
        return self._group(grouping_function, "packageName", package)

    def _count(agg, curr):
        """
        Use this function to count the number of occurrences of a value in a list of tuples.
        """
        error, value = curr
        if error in agg:
            agg[error] += value
        else:
            agg[error] = value
        return agg

    def count_error_types(self):
        error = [
            (tokenize(errorDocument.errorType), errorDocument.value)
            for errorDocument in self.error_documents
        ]
        error_counts = reduce(ErrorAnalyzer._count, error, dict())
        return error_counts

    def count_error_messages(self):
        error = [
            (tokenize(errorDocument.errorMessage), errorDocument.value)
            for errorDocument in self.error_documents
        ]
        error_counts = reduce(ErrorAnalyzer._count, error, dict())
        return error_counts

    def count_packages(self):
        packages = [
            (tokenize(errorDocument.packageName), errorDocument.value)
            for errorDocument in self.error_documents
        ]
        packages_counts = reduce(ErrorAnalyzer._count, packages, dict())
        return packages_counts

    def count_last_lines(self):
        last_lines = [
            (tokenize(errorDocument.last_stacktrace_line), errorDocument.value)
            for errorDocument in self.error_documents
        ]
        last_line_counts = reduce(ErrorAnalyzer._count, last_lines, dict())
        return last_line_counts

    def _calculate_similarity(self, errors):
        """
        Calculate the similarity between the given errors.
        """
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(errors)
        arr = X.toarray()
        return cosine_similarity(arr)

    def calculate_similarity_stacktraces(self):
        errors = [errorDocument.stackTrace for errorDocument in self.error_documents]
        return (
            errors,
            self._calculate_similarity([tokenize(error) for error in errors]),
        )

    def calculate_similarity_last_stacktrace_lines(self):
        errors = [
            errorDocument.last_stacktrace_line for errorDocument in self.error_documents
        ]
        return (
            errors,
            self._calculate_similarity([tokenize(error) for error in errors]),
        )

    def calculate_similarity_messages(self):
        errors = [errorDocument.errorMessage for errorDocument in self.error_documents]
        return (
            errors,
            self._calculate_similarity([tokenize(error) for error in errors]),
        )

    @property
    def error_documents(self):
        """
        Returns a list of all error documents from graalpy.
        Removes all error documents that are also in cpython.
        """
        error_documents = list()
        cpython_failures_names = [
            errorDocument.name for errorDocument in self.cpython_error_documents
        ]
        for errorDocument in self.graalpy_error_documents:
            # Only add error documents that are not in cpython
            # Identifies an error document by the identifier name
            if (
                errorDocument.name is None
                or errorDocument.name == ""
                or errorDocument.name not in cpython_failures_names
            ):
                error_documents.append(errorDocument)
        return error_documents
