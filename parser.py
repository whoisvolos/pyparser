import sys
import re

from pyparser.exceptions import ParseException
from pyparser import Parsers
from pyparser.Source import Source










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
print 4, parser4(src)

parser5 = opener * 2
print parser5(src)

parser6 = Parsers.string('(((')
print parser6(src)

parser7 = Parsers.string('(((') | Parsers.string('(()')
print parser7(src)

src = Source('jopa!')
parser8 = Parsers.string('jopa').result('JOPA')
print parser8(src   )

src = Source('abcd')
src = src.advance()
print src
print src.reminder
