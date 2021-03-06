=======
BinMsg
=======

.. image:: https://drone.io/github.com/annttu/BinMsg/status.png

BinMsg is simple library to make a binary message protocol easily.

Currently library supports python >= 2.7

Usage
------

Example::

    >>> import binmsg
    >>> defs = [
            {'name': 'type', 'struct': binmsg.uchar()},
            {'name': 'name', 'struct': binmsg.string()},
            {'name': 'age', 'struct': binmsg.uint()},
        ]
    >>> b = binmsg.BinMsg(definitions=defs)
    >>> msg = {'type': 1, 'name': 'Test', 'age': 20}
    >>> out = b.pack(msg)
    >>> out
    '\x01\x00\x00\x00\x04Test\x00\x00\x00\x14'
    >>> b.unpack(out)
    {'age': 20, 'type': 1, 'name': 'Test'}


Author
------

* Antti 'Annttu' Jaakkola

License
-------

The MIT License (MIT)

Copyright (c) 2014 Antti Jaakkola

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
