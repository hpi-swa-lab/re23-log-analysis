from JunitXMLParser import JunitXMLParser
import os
from ErrorDocument import ErrorDocument
import matplotlib.pyplot as plt
from collections import Counter
import pandas
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from utils import create_heatmap, tokenize
import re 
class ErrorAnalyser(object):
    
    def __init__(self, files, error_documents = list()):
        self.files = files
        self.error_documents = error_documents

    def load(self):
        for package, file in self.files:
            if os.path.isfile(file):
                xml_parser = JunitXMLParser(file)
                for errorType, errorMessage, stackTrace in xml_parser.get_error_stacktraces():
                    errorDocument = ErrorDocument(package, errorType, errorMessage, stackTrace)
                    self.error_documents.append(errorDocument)
    
    def filter_error_type(self, error_type):
        error_documents = [errorDocument for errorDocument in self.error_documents if errorDocument.errorType is not None and re.match(error_type, errorDocument.errorType)]
        return ErrorAnalyser(self.files, error_documents)   
    
    def filter_error_message(self, error_message):
        error_documents = [errorDocument for errorDocument in self.error_documents if errorDocument.errorMessage is not None and re.match(error_message, errorDocument.errorMessage)]
        return ErrorAnalyser(self.files, error_documents)

    def filter_stacktrace(self, stacktrace):
        error_documents = [errorDocument for errorDocument in self.error_documents if errorDocument.stacktrace is not None and re.match(stacktrace, errorDocument.stacktrace)]
        return ErrorAnalyser(self.files, error_documents)
    
    def filtere_packages(self, packages):
        error_documents = [errorDocument for errorDocument in self.error_documents if errorDocument.packageName in packages]
        return ErrorAnalyser(self.files, error_documents)

    def plot_hist_error_types(self):
        error = [tokenize(errorDocument.errorType) for errorDocument in self.error_documents]
        error_counts = Counter(error)
        df = pandas.DataFrame.from_dict(error_counts, orient='index')
        df.plot(subplots=True, kind='bar', rot=0.0, title="Error types")
    
    def print_top_error_types(self, top=10):
        print("--- TOP {} ERROR TYPES ---".format(top))
        error = [tokenize(errorDocument.errorType) for errorDocument in self.error_documents]
        self._print_top_error(error, top)
    
    def plot_hist_error_messages(self):
        error = [tokenize(errorDocument.errorMessage) for errorDocument in self.error_documents]
        error_counts = Counter(error)
        df = pandas.DataFrame.from_dict(error_counts, orient='index')
        df.plot(subplots=True, kind='bar', title="Error messages")
    
    def print_top_error_messages(self, top=10):
        print("--- TOP {} ERROR MESSAGES ---".format(top))
        error = [tokenize(errorDocument.errorMessage) for errorDocument in self.error_documents]
        self._print_top_error(error, top)

    def plot_tfidf_error_messages(self):
        errors = [tokenize(errorDocument.errorMessage) for errorDocument in self.error_documents]
        self._plot_tfidf(errors, "TF-IDF Error Messages")
        
    def plot_tfidf_error_stacktraces(self):
        errors = [tokenize(errorDocument.stackTrace) for errorDocument in self.error_documents]
        self._plot_tfidf(errors, "TF-IDF Stacktraces")
    
    def plot_tfidf_last_stacktrace_line(self):
        errors = [tokenize(errorDocument.last_stacktrace_line) for errorDocument in self.error_documents]
        self._plot_tfidf(errors, "TF-IDF Last Stacktrace Line")

    def print_tfidf_error_stracktrace(self, bottom_limit, top_limit, top=10):
        print("--- SIMILAR ERROR STACKTRACES ---")
        errors = [tokenize(errorDocument.stackTrace) for errorDocument in self.error_documents]
        self._print_tfidf(errors, bottom_limit, top_limit, top)
    
    def print_tfidf_last_stacktrace_line(self, bottom_limit, top_limit, top=10):
        print("--- SIMILAR LAST STACKTRACE LINE ---")
        errors = [tokenize(errorDocument.last_stacktrace_line) for errorDocument in self.error_documents]
        self._print_tfidf(errors, bottom_limit, top_limit, top)
    
    def _print_tfidf(self,errors, bottom_limit, top_limit, top):
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(errors)
        arr = X.toarray()
        similarity = cosine_similarity(arr)
        interested_index = []
        for i in range(len(similarity)):
            for j in range(len(similarity[i]) - i - 1):
                if similarity[i][j] > bottom_limit and similarity[i][j] < top_limit:
                    interested_index.append((i, j))
        sorted_interested_index = sorted(interested_index, key=lambda x: similarity[x[0]][x[1]], reverse=True)
        for i, j in sorted_interested_index[:top]:
            print("Similarity: {}".format(similarity[i][j]))
            print("Error 1: {}".format(errors[i]))
            print("Error 2: {}".format(errors[j]))
            print("--------------------")
    
    def _plot_tfidf(self, errors, title):
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(errors)
        arr = X.toarray()
        labels = [error[:20] for error in errors]
        create_heatmap(cosine_similarity(arr), labels, title)
    
    def _print_top_error(self, errors, top):
        error_counts = Counter(errors)
        for error, count in error_counts.most_common(top):
            print("#{} - {}".format(count, error))