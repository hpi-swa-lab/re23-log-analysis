class ErrorDocument(object):
    
    def __init__(self, packageName, errorType, errorMessage, stackTrace):
        self.packageName = packageName
        self.errorType = errorType
        self.errorMessage = errorMessage
        self.stackTrace = stackTrace

    @property
    def last_stacktrace_line(self):
        """Get last non empty line of stacktrace"""
        i = -1
        while self.stackTrace.split('\n')[i] == '':
            i -= 1
        return self.stackTrace.split('\n')[i]
  