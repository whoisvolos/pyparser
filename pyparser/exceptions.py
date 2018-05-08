

class ParseException(BaseException):
    def __init__(self, message, errors=None):
        super(ParseException, self).__init__(message)
        self.errors = errors or []