import sys
import re

from pyparser.exceptions import ParseException
from pyparser.Result import Result
from pyparser import Parsers
from pyparser.Source import Source
from pyparser.Parser import ParserFromGenerator


esc = Parsers.char('\\') >> (Parsers.char('\"') | Parsers.char('\\') | Parsers.char('\''))
alpha = Parsers.any_of(lambda c: c != '\'' and c != '"' and c != '\\')

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
number_p = number() << whitespace
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
        yield (op, expressions)

@ParserFromGenerator
def polish():
    op = yield op_p
    expressions = yield expr()[1:]
    yield (op, expressions)

polish_p = polish()

src = Source(r'+ 6 (* 2 9)')
print polish_p(src)
