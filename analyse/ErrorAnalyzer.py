from JunitXMLParser import JunitXMLParser
import os
from ErrorDocument import ErrorDocument
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from utils import tokenize
import re 
from FailureDataCollector import FailureDataCollector

class ErrorAnalyzer(object):
    
    def __init__(self, data_collector: FailureDataCollector, graalpy_error_documents = None, cpython_error_documents = None):
        self.data_collector: FailureDataCollector = data_collector
        if graalpy_error_documents is None:
            self.graalpy_error_documents = list()
            self.load(self.data_collector.graalpy_xml_files, self.graalpy_error_documents)
        else:
            self.graalpy_error_documents = graalpy_error_documents
        if cpython_error_documents is None:
            self.cpython_error_documents = list()
            self.load(self.data_collector.cpython_xml_files, self.cpython_error_documents)
        else:
            self.cpython_error_documents = cpython_error_documents

    def load(self, files, error_documents):
        for package, file in files:
            if os.path.isfile(file):
                xml_parser = JunitXMLParser(file)
                for testName, errorType, errorMessage, stackTrace in xml_parser.get_error_stacktraces():
                    errorDocument = ErrorDocument(testName, package, errorType, errorMessage, stackTrace)
                    error_documents.append(errorDocument)
    
    def _filter(self, filter_function):
        graalpy_error_documents = [errorDocument for errorDocument in self.graalpy_error_documents if filter_function(errorDocument)]
        cpython_error_documents = [errorDocument for errorDocument in self.cpython_error_documents if filter_function(errorDocument)]
        return ErrorAnalyzer(self.data_collector, graalpy_error_documents, cpython_error_documents)
    
    def filter_error_type(self, error_type):
        filter_function = lambda errorDocument: errorDocument.errorType is not None and re.search(error_type, errorDocument.errorType) is not None
        return self._filter(filter_function)
    
    def filter_error_message(self, error_message):
        filter_function = lambda errorDocument: errorDocument.errorMessage is not None and re.search(error_message, errorDocument.errorMessage) is not None
        return self._filter(filter_function)

    def filter_stacktrace(self, stacktrace):
        filter_function = lambda errorDocument: errorDocument.stackTrace is not None and re.search(stacktrace, errorDocument.stackTrace) is not None
        return self._filter(filter_function)
    
    def filter_packages(self, packages):
        filter_function = lambda errorDocument: errorDocument.packageName in packages
        return self._filter(filter_function)

    def count_error_types(self):
        error = [tokenize(errorDocument.errorType) for errorDocument in self.error_documents]
        error_counts = Counter(error)
        return error_counts
    
    def count_error_messages(self):
        error = [tokenize(errorDocument.errorMessage) for errorDocument in self.error_documents]
        error_counts = Counter(error)
        return error_counts
    
    def count_packages(self):
        packages = [errorDocument.packageName for errorDocument in self.error_documents]
        package_counts = Counter(packages)
        return package_counts
    
    def _calculate_similarity(self, errors):
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(errors)
        arr = X.toarray()
        return cosine_similarity(arr)

    def calculate_similarity_stacktraces(self):
        errors = [errorDocument.stackTrace for errorDocument in self.error_documents]
        return (errors, self._calculate_similarity([tokenize(error) for error in errors]))

    def calculate_similarity_last_stacktrace_lines(self):
        errors = [errorDocument.last_stacktrace_line for errorDocument in self.error_documents]
        return (errors, self._calculate_similarity([tokenize(error) for error in errors]))
    
    def calculate_similarity_messages(self):
        errors = [errorDocument.errorMessage for errorDocument in self.error_documents]
        return (errors, self._calculate_similarity([tokenize(error) for error in errors]))

    @property
    def error_documents(self):
        error_documents = list()
        cpython_failures_names = [errorDocument.name for errorDocument in self.cpython_error_documents]
        for errorDocument in self.graalpy_error_documents:
            if errorDocument.name in cpython_failures_names:
                error_documents.append(errorDocument)
        return error_documents