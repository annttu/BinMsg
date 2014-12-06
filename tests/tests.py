#!/usr/bin/env python
# encoding: utf-8


import binmsg
import unittest
import struct
import logging


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.basicConfig()

"""
TODO: test conditions
"""

class TestBasic(unittest.TestCase):
    def setUp(self):
        defs = [
            {'name': 'type', 'struct': binmsg.uchar()},
            {'name': 'name', 'struct': binmsg.string()},
            {'name': 'age', 'struct': binmsg.uint()},
        ]
        self.binmsg = binmsg.BinMsg(definitions=defs)

    def test_unpack(self):
        msg = struct.pack('!bIccccI', 1, 4, b'T', b'e', b's', b't', 20)
        msg = struct.pack('!I', len(msg)) + msg
        out = self.binmsg.unpack(msg)
        self.assertEqual(out['type'], 1, "Type should be 1")
        self.assertEqual(out['name'], 'Test', "Name should be 'Test'")
        self.assertEqual(out['age'], 20, "Age should be 20")

    def test_pack(self):
        msg = {'type': 1, 'name': 'Test', 'age': 20}
        out = self.binmsg.pack(msg)
        x = struct.unpack('!IbIccccI', out)
        (_len, _type, name_length, name, age) = (x[0], x[1], x[2], b''.join(x[3:7]), x[7])
        self.assertEqual(_type, 1, "Type should be 1")
        self.assertEqual(name_length, 4, "name length should be 4")
        self.assertEqual(name, b'Test', "Name should be 'Test'")
        self.assertEqual(age, 20, "Age should be 20")

    def test_both(self):
        msg = {'type': 1, 'name': 'Test', 'age': 20}
        x = self.binmsg.pack(msg)
        out = self.binmsg.unpack(x)
        self.assertEqual(out['type'], 1, "Type should be 1")
        self.assertEqual(out['name'], 'Test', "Name should be 'Test'")
        self.assertEqual(out['age'], 20, "Age should be 20")

    def test_length(self):
        defs = [{'name': 'age', 'struct': binmsg.uint()}]
        b = binmsg.BinMsg(definitions=defs)
        x = struct.pack("!II", 1, 25)
        try:
            out = self.binmsg.unpack(x)
            self.fail("Too short message shouldn't get parsed")
        except binmsg.CannotUnpack:
            pass
        x = struct.pack("!II", 5, 25)
        try:
            out = self.binmsg.unpack(x)
            self.fail("Too long message shouldn't get parsed")
        except binmsg.CannotUnpack:
            pass


class TestTypes(unittest.TestCase):
    def test_unsignedinteger(self):
        defs = [{'name': 'integer', 'struct': binmsg.UnsignedInteger()},]
        b = binmsg.BinMsg(definitions=defs)
        msg = {'integer': 12345}
        out = b.pack(msg)
        s = struct.Struct('!I')
        self.assertEqual(struct.pack('!II', s.size,12345), out,
                                               "Wrong value for packed integer")
        out = b.unpack(out)
        self.assertEqual(out['integer'], 12345,
                                             "Wrong value for unpacked integer")

        msg = {'integer': -12345}
        try:
            out = b.pack(msg)
        except binmsg.CannotPack as e:
            pass
        except Exception as e:
            self.fail("Wrong exception (%s) thrown for neagtive value." % e)
        else:
            self.fail("Negative value should raise CannotPack error")

    def test_integer(self):
        defs = [{'name': 'integer', 'struct': binmsg.Integer()},]
        b = binmsg.BinMsg(definitions=defs)
        msg = {'integer': 12345}
        out = b.pack(msg)
        s = struct.Struct('!I')
        self.assertEqual(struct.pack('!II', s.size, 12345), out,
                                               "Wrong value for packed integer")
        out = b.unpack(out)
        self.assertEqual(out['integer'], 12345,
                                             "Wrong value for unpacked integer")
        # Test negative value
        msg = {'integer': -12345}
        out = b.pack(msg)
        s = struct.Struct("!I")
        self.assertEqual(struct.pack('!Ii', s.size, -12345), out,
                                      "Wrong value for packed neagtive integer")
        out = b.unpack(out)
        self.assertEqual(out['integer'], -12345,
                                    "Wrong value for unpacked negative integer")

    def test_uchar(self):
        defs = [{'name': 'char', 'struct': binmsg.UnsignedChar()},]
        b = binmsg.BinMsg(definitions=defs)
        msg = {'char': 129}
        out = b.pack(msg)
        self.assertEqual(struct.pack('!IB', 1, 129), out,
                                         "Wrong value for packed unsigned char")
        out = b.unpack(out)
        self.assertEqual(out['char'], 129, "Wrong value for unsigned char")
        msg = {'char': -1}
        try:
            out = b.pack(msg)
        except binmsg.CannotPack as e:
            pass
        except Exception as e:
            self.fail("Wrong exception (%s) thrown for neagtive value." % e)
        else:
            self.fail("Negative value should raise CannotPack error")

    def test_char(self):
        defs = [{'name': 'char', 'struct': binmsg.char()},]
        b = binmsg.BinMsg(definitions=defs)
        msg = {'char': b'z'}
        out = b.pack(msg)
        self.assertEqual(struct.pack('!Ic', 1, b'z'), out,
                                                  "Wrong value for packed char")
        out = b.unpack(out)
        self.assertEqual(out['char'], 'z', "Wrong value for char")

    def test_string(self):
        defs = [{'name': 'string', 'struct': binmsg.string()},]
        b = binmsg.BinMsg(definitions=defs)
        out = b.pack({'string': 'test abc 123 ?*= abc abc test test test'})
        out = b.unpack(out)
        self.assertEqual(out['string'], 'test abc 123 ?*= abc abc test test test', "Wrong value for string %s" % out['string'])
        out = b.pack({'string': 'unicode chars ä í ☃'})
        out = b.unpack(out)
        self.assertEqual(out['string'], 'unicode chars ä í ☃', "Wrong value for string %s" % (out['string'],))
        out = b.pack({'string': '☃☃☃☃☃☃'})
        out = b.unpack(out)
        self.assertEqual(out['string'], '☃☃☃☃☃☃', "Wrong value for string %s" % (out['string'],))

    def test_biginteger(self):
        defs = [{'name': 'number', 'struct': binmsg.BigInteger()},]
        b = binmsg.BinMsg(definitions=defs)
        msg = {'number': 123456789}
        out = b.pack(msg)
        s = struct.Struct('!q')
        self.assertEqual(struct.pack('!Iq', s.size, 123456789), out,
                                                "Wrong value for packed number")
        out = b.unpack(out)
        self.assertEqual(out['number'], 123456789, "Wrong value for number")

    def test_unsignedbiginteger(self):
        defs = [{'name': 'number', 'struct': binmsg.UnsignedBigInteger()},]
        b = binmsg.BinMsg(definitions=defs)
        msg = {'number': 123456789}
        out = b.pack(msg)
        s = struct.Struct('!q')
        self.assertEqual(struct.pack('!Iq', s.size, 123456789), out,
                                                "Wrong value for packed number")
        out = b.unpack(out)
        self.assertEqual(out['number'], 123456789, "Wrong value for number")

    def test_float(self):
        defs = [{'name': 'number', 'struct': binmsg.Float()},]
        b = binmsg.BinMsg(definitions=defs)
        msg = {'number': 1234.12}
        out = b.pack(msg)
        self.assertTrue(struct.unpack('!If', out)[1] > 1234.11999 and \
                        struct.unpack('!If', out)[1] < 1234.12001,
                                                "Wrong value for packed number")
        out = b.unpack(out)
        self.assertTrue(out['number'] > 1234.1199 and out['number'] < 1234.1201,
                                                       "Wrong value for number")

    def test_double(self):
        defs = [{'name': 'number', 'struct': binmsg.Double()},]
        b = binmsg.BinMsg(definitions=defs)
        msg = {'number': 1234.12}
        out = b.pack(msg)
        self.assertTrue(struct.unpack('!Id', out)[1] > 1234.11999999 and \
                        struct.unpack('!Id', out)[1] < 1234.120001,
                                                "Wrong value for packed number")
        out = b.unpack(out)
        self.assertEqual(out['number'], 1234.12, "Wrong value for number")

    def test_invalid_type(self):
        defs = [{'name': 'number', 'struct': binmsg.uchar()},]
        b = binmsg.BinMsg(definitions=defs)
        msg = {'number': 'x'}
        try:
            b.pack(msg)
        except binmsg.CannotPack as e:
            pass
        except Exception as e:
            self.fail("Wrong exception (%s) thrown for invalid type." % e)
        else:
            self.fail("Invalid type should raise CannotPack error")


class TestConditions(unittest.TestCase):
    def test_contains(self):
        defs = [{'name': 'type', 'struct': binmsg.uchar()},
                {'name': 'number', 'struct': binmsg.Double(), 'condition': binmsg.Contains('nonexist')},
                {'name': 'string', 'struct': binmsg.String(), 'condition': binmsg.Contains('type')},
                ]
        b = binmsg.BinMsg(definitions=defs)
        msg = {'type': 3, 'string': 'asdf'}
        b.pack(msg)
        msg = {'type': 3, 'number': 3.4, 'string': 'asdf'}
        try:
            b.pack(msg)
            self.fail("Contains should filter field with false condition")
        except binmsg.CannotPack:
            pass

    def test_valueis(self):
        defs = [{'name': 'type', 'struct': binmsg.uchar()},
                {'name': 'number', 'struct': binmsg.Double(), 'condition': binmsg.ValueIs('type', 3)},
                {'name': 'string', 'struct': binmsg.String(), 'condition': binmsg.ValueIs('type', 2)},
                ]
        b = binmsg.BinMsg(definitions=defs)
        msg = {'type': 2, 'string': 'asdf'}
        b.pack(msg)
        msg = {'type': 3, 'number': 3.4}
        b.pack(msg)
        msg = {'type': 3, 'number': 3.4, 'string': 'asdf'}
        try:
            b.pack(msg)
            self.fail("Contains should filter field with ValueIs condition which expands to False")
        except binmsg.CannotPack:
            pass

if __name__ == '__main__':
    unittest.main()
