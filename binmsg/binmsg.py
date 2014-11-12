# encoding: utf-8

from struct import Struct as SStruct, unpack, pack
import logging
import sys


logger = logging.getLogger('BinMsg')

python3 = False
if sys.version_info>(3,0,0):
    python3 = True
    # There isn't long on python3 anymore
    long = int

class BinMsgException(Exception):
    pass

class SizeNotDefined(BinMsgException):
    pass

class CannotUnpack(BinMsgException):
    pass

class CannotPack(BinMsgException):
    pass

class BinStruct(object):
    _format = '!c'
    _type = None
    _min = None
    _max = None

    def __init__(self):
        self.struct = SStruct(self._format)
        self._custom_size = None

    @property
    def size(self):
        return self.struct.size

    @property
    def custom_size(self):
        return self._custom_size

    @custom_size.setter
    def custom_size(self, value):
        self._custom_size = value

    def unpack(self, string):
        return self.struct.unpack(string)

    def pack(self, string):
        return self.struct.pack(string)

class Struct(BinStruct):
    def __init__(self, format):
        self._format = format
        self.struct = SStruct(self._format)

    @property
    def size(self):
        return self.struct.size

    def unpack(self, string):
        return self.struct.unpack(string)

    def pack(self, string):
        return self.struct.pack(string)

class UnsignedChar(BinStruct):
    """
    Unsigned char is number with value from 0 to 256
    """
    _format = '!B'
    _type = int
    _min = 0
    _max = 256

UChar = UnsignedChar
uchar = UnsignedChar

class Char(BinStruct):
    """
    Char is one ascii character with numeric value from -127 to 128
    """
    _format = '!c'
    _type = str
    _min = '\0'
    _max = '\256'

char = Char

class Integer(BinStruct):
    """
    Integer is number with value from -2147483647 to 2147483648
    """
    _format = '!i'
    _type = int
    _min = -2147483647
    _max = 2147483648

integer = Integer

class UnsignedInteger(BinStruct):
    """
    Unsigned Integer is number with value from 0 to 4294967296
    """
    _format = '!I'
    _type = int
    _min = 0
    _max = 4294967296

UInteger = UnsignedInteger
uinteger = UnsignedInteger
uint = UnsignedInteger

class BigInteger(BinStruct):
    """
    BigInteger is number with value from  -9223372036854775807 to 9223372036854775808
    """
    _format = '!q'
    _type = long
    _min = -9223372036854775807
    _max = 9223372036854775808

bigint = BigInteger
biginteger = BigInteger

class UnsignedBigInteger(BinStruct):
    """
    Unsigned big integer is number from 0 to 18446744073709551616
    """
    _format = '!Q'
    _type = long
    _min = 0
    _max = 18446744073709551616

UBigInteger = UnsignedBigInteger
ubigint = UnsignedBigInteger
ubiginteger = UnsignedBigInteger

class Float(BinStruct):
    _format = '!f'
    _type = float
    _min = 1.175494351* (10 ** (-38))
    _max = 3.402823466 * (10 ** 38)

class Double(BinStruct):
    _format = '!d'
    _type = float
    _min = 2.2250738585072014 * 10 ** (-308)
    _max = 1.7976931348623158 * 10 ** 308

double = Double

# TODO:
# - Unlimited integer

class String(BinStruct):
    """
    String contains 0 or more characters. Sting size is dynamically allocated.
    """
    _type = str

    def __init__(self, length_format='!I'):
        self.length_format = length_format
        self.size_struct = SStruct(length_format)

    @property
    def size(self):
        raise SizeNotDefined()

    def unpack(self, msg):
        """
        Unpack string, little ugly but works
        """
        if len(msg) != self.custom_size:
            raise CannotPack("Got message with wrong length!")
        return ''.join([chr(unpack('!B', msg[i])[0]) for i in range(self.custom_size)])

    def pack(self, msg):
        """
        Pack string with length
        """
        if not python3:
            if type(msg) == unicode:
                msg = msg.encode("utf-8")
        st = self.size_struct.pack(len(msg))
        st += b''.join([pack('!B', ord(msg[i])) for i in range(len(msg))])
        return st



class Condition(object):
    """
    Condition for value

    Condition can be combined with other Conditions using "|" as or and "&"
    as and.

    Eg.

    Contains(field="foo") & ValueIs(field="foo", value=4, condition="!=")

    """
    def check(self, output):
        return True

    def __or__(self, other):
        c = self.check
        def f(*args, **kwargs):
            return c(*args, **kwargs) or other.check(*args, **kwargs)
        self.check = f
        return self

    def __and__(self, other):
        c = self.check
        def f(*args, **kwargs):
            return c(*args, **kwargs) and other.check(*args, **kwargs)
        self.check = f
        return self


class Contains(Condition):
    """
    Value existence check.
    """
    def __init__(self, field, neagtion = False):
        """
        Initialize Checker class

        field: name of field to check
        negation: negate check output
        """
        self.field = field
        self.negation = negation

    def check(self, output):
        """
        Do check to output

        Returns True if check passes, otherwise False.
        """
        if self.field not in output:
            return self.negation
        return not self.negation

class ValueIs(Condition):
    """
    Checks field value compared to given value with condition.
    """
    def __init__(self, field, value, condition='=='):
        """
        field: name of field to check
        value: value to compare value. 
        condition: condition between field value and given value.
        """
        self.field = field
        self.value = value
        if type(value) in [str] and condition not in ['==', '!=']:
            raise ValueError("Invalid condition %s for type %s" % (
                                                        condition), type(value))
        elif type(value) in [int, float] and \
                condition not in ['==', '>', '<', '!=', '<=', '>=']:
            raise ValueError("Invalid condition %s" % condition)
        self.condition = condition

    def check(self, output):
        """
        Do check to output

        Returns True if check passes, otherwise False.
        """
        if self.field not in output:
            return False
        value = output[self.field]
        if condition == '==':
            return value == self.value
        elif condition == '!=':
            return value != self.value
        elif condition == '>=':
            return value >= self.value
        elif condition == '<=':
            return value <= self.value
        elif condition == '>':
            return value > self.value
        elif condition == '<':
            return value < self.value
        return False

string = String

"""
'name': string,
'type': Struct,
'condition': Condition1 & Condition2
"""

class BinMsg(object):
    def __init__(self, definitions):
        self.definitions = []
        for v in definitions:
            if 'name' not in v:
                raise ValueError("Name is mandatory argument!")
            if 'struct' not in v:
                raise ValueError("Struct is mandatory argument!")
            self.definitions.append(v)

    def pack(self, msg):
        """
        Pack given message (dict) to binary message using predefined fields.
        If pack fails, CannotPack is raised.
        Returns binary string.
        """
        if type(msg) != dict:
            raise ValueError("Msg should be dict!")
        output = []
        for definition in self.definitions:
            if definition['name'] not in msg:
                raise CannotPack("value for key %s not found from message" % (
                                 definition['name']))
            struct = definition['struct']
            value = msg[definition['name']]
            if struct._type is not None:
                fail = False
                try:
                    value = struct._type(value)
                except ValueError:
                    fail = True
                if fail:
                    raise CannotPack(
                         "Value %s for field %s is invalid type %s" % (
                                     value, definition['name'], type(value)))
            if struct._min is not None:
                if value < struct._min:
                    raise CannotPack(
                         "Value %s for field %s is too small, minimum is %s" % (
                                     value, definition['name'], struct._min))
            if struct._max is not None:
                if value > struct._max:
                    raise CannotPack(
                         "Value %s for field %s is too big, maximum is %s" % (
                                     value, definition['name'], struct._max))
            output.append(struct.pack(value))
        return b''.join(output)

    def unpack(self, msg):
        """
        Unpack given message to message dictionary using predefined fields.
        If unpack fails, CannotUnpack is raised.
        Returns message dictionary.
        """
        output = {}
        for definition in self.definitions:
            if definition['name'] in output:
                continue
            if 'condition' in output:
                if not condition.check(output):
                    continue
            struct = definition['struct']
            try:
                size = struct.size
            except SizeNotDefined:
                try:
                    size_msg = msg[:struct.size_struct.size]
                    msg = msg[struct.size_struct.size:]
                    size = struct.size_struct.unpack(size_msg)[0]
                    struct.custom_size = size
                except Exception as e:
                    logger.exception(e)
            if not size:
                raise CannotUnpack("Cannot get size of element %s" %
                                                            definition['name'])
            m = msg[:size]
            msg = msg[size:]
            value = struct.unpack(m)
            if len(value) == 1:
                # unpack returns tuples
                value = value[0]
            output[definition['name']] = value
        return output

