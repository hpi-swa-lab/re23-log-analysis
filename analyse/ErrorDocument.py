class ErrorDocument(object):
    
    def __init__(self, packageName, errorType, errorMessage, stackTrace):
        self.packageName = packageName
        self.errorType = errorType
        self.errorMessage = errorMessage
        self.stackTrace = stackTrace
    
  