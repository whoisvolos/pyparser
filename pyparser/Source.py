from .exceptions import ParseException


class Source:
    def __init__(self, string, position=None):
        self.string = string
        self.position = position or 0

    def advance(self, incr=1):
        if self.is_eof:
            raise ParseException('EOF')
        return Source(self.string, self.position + incr)

    @property
    def current(self):
        return self.string[self.position]

    @property
    def is_eof(self):
        return self.position == len(self.string)

    @property
    def reminder(self):
        return self.string[self.position:]

    def __str__(self):
        return 'StringSource({})'.format(self.reminder)