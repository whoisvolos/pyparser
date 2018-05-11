import sys
import re

from pyparser.exceptions import ParseException
from pyparser import Parsers
from pyparser.Source import Source
from pyparser.Parser import ParserFromGenerator


esc = Parsers.char('\\') >> (Parsers.char('\"') | Parsers.char('\\') | Parsers.char('\''))
alpha = Parsers.any_of(lambda c: c != '\'' and c != '"' and c != '\\')

@ParserFromGenerator
def str_parser():
    yield Parsers.char('"')
    contents = yield (alpha | esc)[1:] > ''.join
    yield Parsers.char('"')
    yield contents

src = Source(r'"abc\""')
print str_parser
print str_parser()
print str_parser()(src)