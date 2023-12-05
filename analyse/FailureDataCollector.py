import os

class FailureDataCollector(object):
    
    @property
    def graalpy_xml_files(self) -> list[(str, str)]: # (package, file)
        pass
    
    @property
    def cpython_xml_files(self) -> list[(str, str)]: # (package, file)
        pass
    
    @property
    def filter_error_type(self) -> str:
        pass
    
    @property
    def filter_error_message(self) -> str:
        pass
    
    @property
    def filter_error_stacktrace(self) -> str:
        pass

    @property
    def filter_package(self) -> str:
        pass

class FailureDataCollectorCliParser(FailureDataCollector):
    
    def __init__(self, args):
        self.args = args
    
    @property
    def graalpy_xml_file(self):
        return self.args.graalpy_xml

    @property
    def cpython_xml_file(self):
        return self.args.cpython_xml
    
    @property
    def graalpy_folder(self):
        return self.args.graalpy_folder
    
    @property
    def cpython_folder(self):
        return self.args.cpython_folder
    
    @property
    def graalpy_xml_files(self):
        files = list()
        for path, _, _ in os.walk(self.graalpy_folder):
            package = path.split('/')[-1]
            files.append((package, os.path.join(path, self.graalpy_xml_file)))
        return files
    
    @property
    def cpython_xml_files(self):
        files = list()
        for path, _, _ in os.walk(self.cpython_folder):
            package = path.split('/')[-1]
            files.append((package, os.path.join(path, self.cpython_xml_file)))
        return files 
    
    @property
    def filter_error_type(self):
        return self.args.filter_type
    
    @property
    def filter_error_message(self):
        return self.args.filter_message
    
    @property
    def filter_error_stacktrace(self):
        return self.args.filter_stacktrace

    @property
    def filter_package(self):
        return self.args.filter_package