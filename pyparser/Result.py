

class Result:
    def __init__(self, value, success, error, reminder):
        self.value = value
        self.success = success
        self.error = error
        self.reminder = reminder

    @staticmethod
    def failure(error, reminder):
        return Result(None, False, error, reminder)

    @staticmethod
    def success(value, reminder):
        return Result(value, True, None, reminder)

    @property
    def is_successful(self):
        return self.error == None

    @property
    def is_failed(self):
        return self.error != None

    def __str__(self):
        if self.error:
            return 'Failure({})'.format(self.error)
        else:
            return 'Success({})'.format(self.value)