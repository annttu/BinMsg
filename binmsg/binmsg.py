# encoding: utf-8

from struct import Struct, unpack, pack
import logging


logger = logging.getLogger('BinMsg' )

class BinMsgException(Exception):
    pass

class SizeNotDefined(BinMsgException):
    pass

class CannotUnpack(BinMsgException):
    pass

class CannotPack(BinMsgException):
    pass

class BinStruct(object):
    def unpack(self, msg):
        return None

    def pack(self, msg):
        return None

class StringStruct(BinStruct):
    def __init__(self, length_format='!b'):
        self.size_struct = Struct(length_format)
        self._size = None

    @property
    def size(self):
        if self._size is not None:
            return self._size
        raise SizeNotDefined()

    @size.setter
    def size(self, value):
        self._size = value

    def unpack(self, msg):
        """
        Unpack string, little ugly but works
        """
        if len(msg) != self.size:
            raise CannotPack("Got message with wrong length!")
        return (''.join([unpack('!c', msg[i])[0] for i in range(self.size)]),)

    def pack(self, msg):
        """
        Pack string with length
        """
        return self.size_struct.pack(len(msg)) + \
                        ''.join([pack('!c', msg[i]) for i in range(len(msg))])



class Condition(object):
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
    def __init__(self, field, neagtion = False):
        self.field = field
        self.negation = negation

    def check(self, output):
        if self.field not in output:
            return self.negation
        return not self.negation

class ValueIs(Condition):
    def __init__(self, field, value, condition='=='):
        self.field = field
        self.value = value
        if type(value) == str and condition not in ['==', '!=']:
            raise ValueError("Invalid condition %s for type %s" % (condition), type(value))
        elif type(value) in [int, float] and condition not in ['==', '>', '<', '!=', '<=', '>=']:
            raise ValueError("Invalid condition %s" % condition)
        self.condition = condition

    def check(self, output):
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
        if type(msg) != dict:
            raise ValueError("Msg should be dict!")
        output = []
        for definition in self.definitions:
            if definition['name'] not in msg:
                raise CannotPack("value for key %s not found from message" % (
                                 definition['name']))
            struct = definition['struct']
            output.append(struct.pack(msg[definition['name']]))
        return ''.join(output)

    def unpack(self, msg):
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
                    struct.size = size
                except Exception as e:
                    logger.exception(e)
            if not size:
                raise CannotUnpack("Cannot get size of element %s" % definition['name'])
            m = msg[:size]
            msg = msg[size:]
            value = struct.unpack(m)
            if len(value) == 1:
                # unpack returns tuples
                value = value[0]
            output[definition['name']] = value
        return output

