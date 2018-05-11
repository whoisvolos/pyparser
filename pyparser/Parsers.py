from Result import Result
from Parser import Parser
from .exceptions import ParseException


class Parsers:
    @staticmethod
    def any_of(predicate, expected_str=None):
        @Parser
        def any_of(input):
            if input.is_eof:
                return Result.failure(ParseException('EOF'), input)
            current = input.current
            if not predicate(current):
                return Result.failure(ParseException('Bad symbol at position {pos}, got \'{curr}\'{exp}'.format(
                    pos=input.position,
                    curr=current,
                    exp='' if expected_str is None else ', expected: {}'.format(expected_str)
                )), input)
            return Result.success(current, input.advance())
        return any_of

    @staticmethod
    def char(chr):
        return Parsers.any_of(lambda c: c == chr, expected_str='\'{}\''.format(chr))

    @staticmethod
    def eof():
        @Parser
        def eof(input):
            if input.is_eof:
                return Result.success(None, input)
            else:
                return Result.failure(ParseException('Expected end of file (EOF)'), input)
        return eof

    @staticmethod
    def any():
        @Parser
        def any(input):
            return Result.success(None, input) if input.is_eof else Result.success(input.current, input.advance())
        return any

    @staticmethod
    def string(arg):
        @Parser
        def string(input):
            reminder = input
            builder = []
            for idx in xrange(0, len(arg)):
                if not reminder.is_eof:
                    builder.append(reminder.current)
                    reminder = reminder.advance()
                else:
                    return Result.failure(ParseException('Got EOF while parsing \'{}\''.format(arg)), input)
            builder = ''.join(builder)
            if arg == builder:
                return Result.success(builder, reminder)
            else:
                return Result.failure(ParseException('\'{}\' not found'.format(arg)), input)
        return string

    @staticmethod
    def whitespace():
        return Parsers.any_of(lambda c: c.isspace(), expected_str='whitespace')

    @staticmethod
    def regex(r):
        @Parser
        def regex(input):
            pass
        pass