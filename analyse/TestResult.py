class TestResult(object):
    def __init__(self, wasExecuted, errors=-1, failures=-1, skipped=-1, tests=-1):
        self.wasExecuted = wasExecuted
        self.errors = errors
        self.failures = failures
        self.skipped = skipped
        self.tests = tests  
    
    @property
    def passed (self):
        return self.tests - self.skipped - self.failures - self.errors if self.wasExecuted else -1