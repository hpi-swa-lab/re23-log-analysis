import os


class FailureDataCollector(object):
    @property
    def graalpy_xml_files(self) -> list[(str, str)]:  # (package, file)
        pass

    @property
    def cpython_xml_files(self) -> list[(str, str)]:  # (package, file)
        pass


class FailureDataCollectorConstant(FailureDataCollector):
    def __init__(
        self, graalpy_xml_file, cpython_xml_file, graalpy_folder, cpython_folder
    ):
        self._graalpy_xml_file = graalpy_xml_file
        self._cpython_xml_file = cpython_xml_file
        self._graalpy_folder = graalpy_folder
        self._cpython_folder = cpython_folder

    @property
    def graalpy_xml_files(self):
        files = list()
        for path, _, _ in os.walk(self._graalpy_folder):
            package = path.split("/")[-1]
            files.append((package, os.path.join(path, self._graalpy_xml_file)))
        return files

    @property
    def cpython_xml_files(self):
        files = list()
        for path, _, _ in os.walk(self._cpython_folder):
            package = path.split("/")[-1]
            files.append((package, os.path.join(path, self._cpython_xml_file)))
        return files


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
            package = path.split("/")[-1]
            files.append((package, os.path.join(path, self.graalpy_xml_file)))
        return files

    @property
    def cpython_xml_files(self):
        files = list()
        for path, _, _ in os.walk(self.cpython_folder):
            package = path.split("/")[-1]
            files.append((package, os.path.join(path, self.cpython_xml_file)))
        return files
