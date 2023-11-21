from JunitXMLParser import JunitXMLParser
import os
from ErrorDocument import ErrorDocument

class ErrorAnalyser(object):
    
    def __init__(self, files):
        self.files = files
        self.error_documents = list()
    
    def load(self):
        for package, file in self.files:
            if os.path.isfile(self.files):
                xml_parser = JunitXMLParser(file)
                for errorType, errorMessage, stackTrace in xml_parser.get_error_stacktraces():
                    errorDocument = ErrorDocument(package, errorType, errorMessage, stackTrace)
                    self.error_documents.append(errorDocument)
            