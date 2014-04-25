#!/usr/bin/env python
# encoding: utf-8


import binmsg
import unittest
import struct
import logging


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.basicConfig()

class TestBasic(unittest.TestCase):
    def setUp(self):
        defs = [
            {'name': 'type', 'struct': binmsg.Struct('!b')},
            {'name': 'name', 'struct': binmsg.StringStruct()},
            {'name': 'age', 'struct': binmsg.Struct('!I')},
        ]
        self.binmsg = binmsg.BinMsg(definitions=defs)

    def test_unpack(self):
        msg = struct.pack('!bbccccI', 1, 4, 'T', 'e', 's', 't', 20)
        out = self.binmsg.unpack(msg)
        self.assertEquals(out['type'], 1, "Type should be 1")
        self.assertEquals(out['name'], 'Test', "Name should be 'Test'")
        self.assertEquals(out['age'], 20, "Age should be 20")

    def test_pack(self):
        msg = {'type': 1, 'name': 'Test', 'age': 20}
        out = self.binmsg.pack(msg)
        x = struct.unpack('!bbccccI', out)
        (_type, name_length, name, age) = (x[0], x[1], ''.join(x[2:6]), x[6])
        self.assertEquals(_type, 1, "Type should be 1")
        self.assertEquals(name_length, 4, "name length should be 4")
        self.assertEquals(name, 'Test', "Name should be 'Test'")
        self.assertEquals(age, 20, "Age should be 20")
 
    def test_both(self):
        msg = {'type': 1, 'name': 'Test', 'age': 20}
        out = self.binmsg.unpack(self.binmsg.pack(msg))
        self.assertEquals(out['type'], 1, "Type should be 1")
        self.assertEquals(out['name'], 'Test', "Name should be 'Test'")
        self.assertEquals(out['age'], 20, "Age should be 20")

if __name__ == '__main__':
    unittest.main()