import sys
import re

from pyparser.exceptions import ParseException
from pyparser.Result import Result
from pyparser import Parsers
from pyparser.Source import Source
from pyparser.Parser import ParserFromGenerator


esc = Parsers.char('\\') >> (Parsers.char('\"') | Parsers.char('\\') | Parsers.char('\''))
alpha = Parsers.any_of(lambda c: c != '\'' and c != '"' and c != '\\')


class NumberExpr:
    def __init__(self, number):
        self.number = number

    def reduce(self):
        return self.number

    def __str__(self):
        return str(self.number)

    def __repr__(self):
        return str(self.number)

class Expr:
    def __init__(self, op, exprs):
        self.op = op
        self.exprs = exprs
        self.value = None

    @property
    def is_memo(self):
        return self.value is not None

    def reduce(self):
        if self.is_memo:
            return self.value

        if self.op == '+':
            fn = lambda acc, e: acc + e.reduce()
        elif self.op == '-':
            fn = lambda acc, e: acc - e.reduce()
        elif self.op == '*':
            fn = lambda acc, e: acc * e.reduce()
        elif self.op == '/':
            fn = lambda acc, e: acc / e.reduce()
        self.value = reduce(fn, self.exprs[1:], self.exprs[0].reduce())
        return self.value

    def __str__(self):
        return '{} {}'.format(self.op, self.exprs)


@ParserFromGenerator
def string():
    yield Parsers.char('"')
    contents = yield (alpha | esc)[1:] > ''.join
    yield Parsers.char('"')
    yield contents

@ParserFromGenerator
def number():
    minus = yield Parsers.char('-').optional
    number = yield Parsers.any_of(lambda c: c.isdigit() or c =='.')[1:] > ''.join
    number = float(number)
    if minus is not None:
        number = -number
    yield number

whitespace = Parsers.whitespace()[0:]
open_p = Parsers.char('(') << whitespace
close_p = Parsers.char(')') << whitespace
string_p = string() << whitespace
number_p = (number() << whitespace) > NumberExpr

op_p = Parsers.any_of(lambda c: c == '+' or c == '-' or c == '*' or c == '/') << whitespace

@ParserFromGenerator
def expr():
    res = yield number_p.optional
    if res is not None:
        yield res
    else:
        yield open_p
        op = yield op_p
        expressions = yield expr()[1:]
        yield close_p
        yield Expr(op, expressions)

@ParserFromGenerator
def polish():
    op = yield op_p
    expressions = yield expr()[1:]
    yield Expr(op, expressions)

polish_p = polish()

src = Source(r'+ 6 (* 2 9)')
result = polish_p(src)
if result.is_successful:
    print result.value
    print result.value.is_memo
    print result.value.reduce()
    print result.value.is_memo
else:
    print result.error
