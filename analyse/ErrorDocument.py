class ErrorDocument(object):
    """
    Internal representation of an error document.
    """

    def __init__(
        self,
        name="",
        packageName="",
        errorType="",
        errorMessage="",
        stackTrace="",
        value=1,
    ):
        self.packageName = packageName
        self.errorType = errorType
        self.errorMessage = errorMessage
        self.stackTrace = stackTrace
        self.name = name
        # Value is used to count the number of errors.
        # It's different when using grouping
        self.value = value

    @property
    def last_stacktrace_line(self):
        """Get last non empty line of stacktrace"""
        i = -1
        while self.stackTrace.split("\n")[i] == "":
            i -= 1
        return self.stackTrace.split("\n")[i]

    def __str__(self):
        return "{}x{}({} # {}): {}\n{}".format(
            self.value,
            self.errorType,
            self.packageName,
            self.name,
            self.errorMessage,
            self.stackTrace,
        )
