import sys


class ParseException(BaseException):
    def __init__(self, message, errors=None):
        super(ParseException, self).__init__(message)
        self.errors = errors or []


class Source:
    def __init__(self, string, position=None):
        self.string = string
        self.position = position or 0

    def advance(self):
        if self.is_eof:
            raise ParseException('EOF')
        return Source(self.string, self.position + 1)

    @property
    def current(self):
        return self.string[self.position]

    @property
    def is_eof(self):
        return self.position == len(self.string)


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


class Parser:
    def __init__(self, fn):
        '''
        Creates Parser wrapper for parser function to create combinators in future
        :param fn: function of type (src: Source) -> Result
        '''
        self.fn = fn

    def __call__(self, input):
        return self.fn(input)

    def either(self, other):
        @Parser
        def either(input):
            result = self(input)
            return result if result.is_successful else other(input)
        return either

    def fmap(self, fn):
        '''
        Function application in case of successful parse (functor)
        :param fn: Function of type (A -> B)
        :return: Parser<B>
        '''
        @Parser
        def fmap(input):
            result = self(input)
            return Result.success(fn(result.value), result.reminder) if result.is_successful else result
        return fmap

    def bind(self, fn):
        '''
        Monadic bind op
        :param fn: Function of type (A -> Parser<B>)
        :return: Parser<B>
        '''
        @Parser
        def bind(input):
            result = self(input)
            if result.is_failed:
                return result
            return fn(result.value)(result.reminder)
        return bind

    def one_or_many(self, start):
        @Parser
        def one_or_many(input):
            parsed = Result.failure(None, input)
            result = []
            for i in xrange(0, start):
                parsed = self(parsed.reminder)
                if parsed.is_failed:
                    return Result.failure(parsed.error, input)
                else:
                    result.append(parsed.value)
            while parsed.is_successful:
                parsed = self(parsed.reminder)
                if parsed.is_successful:
                    result.append(parsed.value)
            return Result.success(result, parsed.reminder)
        return one_or_many

    def zero_or_many(self):
        @Parser
        def zero_or_many(input):
            result = []
            parsed = self(input)
            while parsed.is_successful:
                result.append(parsed.value)
                parsed = self(parsed.reminder)
            return Result.success(result, parsed.reminder)
        return zero_or_many

    def times(self, x):
        @Parser
        def times(input):
            result = []
            reminder = input
            for i in xrange(0, x):
                parsed = self(reminder)
                if parsed.is_successful:
                    result.append(parsed.value)
                    reminder = parsed.reminder
                else:
                    return parsed
            return Result.success(result, reminder)
        return times

    def __mul__(self, other):
        return self.times(other)

    def __irshift__(self, other):
        return self.bind(other)

    def __or__(self, other):
        return self.either(other)

    def __gt__(self, other):
        return self.fmap(other)

    def __getitem__(self, item):
        if isinstance(item, slice):
            start, stop = item.start, item.stop
        else:
            #raise Exception('Got {} instead of slice'.format(item))
            return item

        # parser[0:] - zero or many
        # parser[:] - shorthand for parser[0:]
        # parser[1:] - one or many
        # parser[:N] - from zero till N-1
        # parser[M:N] - from M till N-1
        # parser[:-1]
        if start == 0 and stop == sys.maxint:
            return self.zero_or_many()
        if start > 0 and stop == sys.maxint:
            return self.one_or_many(start)
        raise NotImplementedError('Slice is not supported')


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
        return Parsers.any_of(lambda c: c == chr, expected_str='\'{}\''.format(c))

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


src = Source('(()1')
opener = Parsers.any_of(lambda c: c == '(', expected_str='open paren')
closer = Parsers.any_of(lambda c: c == ')', expected_str='closed paren')

parser = opener | closer

parser1 = parser[:]
print parser1(src)

parser2 = parser[2:]
print parser2(src)

parser3 = parser[3:]
print parser3(src)

parser4 = (opener | closer)[1:] > ''.join
print parser4(src)

parser5 = opener * 2
print parser5(src)

parser6 = Parsers.string('(((')
print parser6(src)

parser7 = Parsers.string('(((') | Parsers.string('(()')
print parser7(src)

gen = (
    y for x in Parsers.string('(((')
      for y in Parsers.any_of(lambda _: _ == x)
)
for x in gen:
    print x
#print '[0:]', parser[0:]
#print '[:]', parser[:]
#print '[1:]', parser[1:]
#print '[:100]', parser[:100]
#print '[50:100]', parser[50:100]