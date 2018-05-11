import sys
import re

from pyparser.exceptions import ParseException
from pyparser import Parsers
from pyparser.Source import Source
from pyparser.Parser import ParserFromGenerator


esc = Parsers.char('\\') >> (
    Parsers.char('\"').result(r'\"') |
    Parsers.char('\\').result(r'\\') |
    Parsers.char('\'').result(r'\'')
)
alpha = Parsers.any_of(lambda c: c != '\'' and c != '"')

parser = (alpha | esc)[1:] > ''.join

src = Source(r'abc\"')
print src.string
print parser(src)