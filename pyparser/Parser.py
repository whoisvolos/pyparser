from Result import Result
import sys


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

    def bind(self, other):
        '''
        Monadic bind op
        :param other: Function of type (A -> Parser<B>)
        :return: Parser<B>
        '''
        @Parser
        def bind(input):
            result = self(input)
            if result.is_failed:
                return result
            return other(result.value)(result.reminder)
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

    def then(self, other):
        @Parser
        def then(input):
            parsed = self(input)
            if parsed.is_successful:
                return other(parsed.reminder)
            else:
                return parsed
        return then

    def result(self, value):
        @Parser
        def result(input):
            parsed = self(input)
            if parsed.is_successful:
                return Result.success(value, parsed.reminder)
            else:
                return parsed
        return result

    def __mul__(self, other):
        return self.times(other)

    def __irshift__(self, other):
        return self.bind(other)

    def __or__(self, other):
        return self.either(other)

    def __gt__(self, other):
        return self.fmap(other)

    def __rshift__(self, other):
        return self.then(other)

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


class ParserFromGenerator:
    def __init__(self, generator):
        self.generator = generator

    def __call__(self, *args, **kwargs):
        @Parser
        def generator(input):
            iter = self.generator()
            value = None
            src = input
            while True:
                parser = iter.send(value)
                if not isinstance(parser, Parser):
                    return Result.success(parser, src)
                parsed = parser(src)
                if parsed.is_successful:
                    value = parsed.value
                    src = parsed.reminder
                else:
                    return parsed
        return generator