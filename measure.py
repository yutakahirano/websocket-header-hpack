#!/usr/bin/python

import base64
import random
import sys
from compressor.http2 import Processor


class Frame:
    def __init__(self, opcode, fin, rsv1, rsv2, rsv3, length):
        self.opcode = opcode
        self.fin = fin
        self.rsv1 = rsv1
        self.rsv2 = rsv2
        self.rsv3 = rsv3
        self.length = length

    CONTINUATION = 0
    TEXT = 1
    BINARY = 2
    CLOSE = 8

    def headers1(self):
        o = {}
        o[':opcode'] = str(self.opcode)
        o[':fin'] = '1' if self.fin else '0'
        rsv = ''
        rsv += ('1' if self.rsv1 else '0')
        rsv += (',1' if self.rsv2 else ',0')
        rsv += (',1' if self.rsv3 else ',0')
        if rsv != '0,0,0':
            o[':rsv'] = rsv
        o[':length'] = str(self.length)
        return o

    def headers2(self):
        o = {}
        if self.opcode != 0:
            o[':opcode'] = str(self.opcode)
        if self.fin:
            o[':fin'] = '1'
        if self.rsv1:
            o[':rsv1'] = '1'
        if self.rsv2:
            o[':rsv2'] = '1'
        if self.rsv3:
            o[':rsv3'] = '1'
        o[':length'] = str(self.length)
        return o

    def headers3(self):
        o = {}
        if self.opcode != 0:
            o[':opcode'] = str(self.opcode)
        if self.fin:
            o[':fin'] = '1'
        if self.rsv1 or self.rsv2 or self.rsv3:
            rsv = 0
            if self.rsv1:
                rsv += 4
            if self.rsv2:
                rsv += 2
            if self.rsv3:
                rsv += 1
            o[':rsv'] = str(rsv)
        o[':length'] = str(self.length)
        return o

    def headers4(self):
        o = {}
        if self.opcode != 0:
            o[':opcode'] = str(self.opcode)
        if self.fin:
            o[':fin'] = '1'
        if self.rsv1:
            o[':rsv1'] = '1'
        if self.rsv2:
            o[':rsv2'] = '1'
        if self.rsv3:
            o[':rsv3'] = '1'
        o[':length'] = '{0:x}'.format(self.length)
        return o

    def headers5(self):
        o = {}
        if self.opcode != 0:
            o[':opcode'] = str(self.opcode)
        if self.fin:
            o[':fin'] = '1'
        if self.rsv1:
            o[':rsv1'] = '1'
        if self.rsv2:
            o[':rsv2'] = '1'
        if self.rsv3:
            o[':rsv3'] = '1'
        return o


def measure_for_frames(description, frames):
    print('{0}: len(frames) = {1}'.format(description, len(frames)))
    p1 = Processor({}, True, {})
    p2 = Processor({}, True, {})
    p3 = Processor({}, True, {})
    p4 = Processor({}, True, {})
    p5 = Processor({}, True, {})
    bytes1 = b''.join([p1.compress(f.headers1(), '') for f in frames])
    bytes2 = b''.join([p2.compress(f.headers2(), '') for f in frames])
    bytes3 = b''.join([p3.compress(f.headers3(), '') for f in frames])
    bytes4 = b''.join([p4.compress(f.headers4(), '') for f in frames])
    bytes5 = b''.join([p5.compress(f.headers5(), '') for f in frames])
    print('1: As specified in SPDY4 spec draft')
    print('  len(bytes) = {0}, average = {1}'.format(
        len(bytes1), len(bytes1) * 1.0 / len(frames)))
    print('2: Omit headers when its value is zero')
    print('  len(bytes) = {0}, average = {1}'.format(
        len(bytes2), len(bytes2) * 1.0 / len(frames)))
    print('3: 2 + assemble rsv headers')
    print('  len(bytes) = {0}, average = {1}'.format(
        len(bytes3), len(bytes3) * 1.0 / len(frames)))
    print('4: 2 + hexadecimal length representation')
    print('  len(bytes) = {0}, average = {1}'.format(
        len(bytes4), len(bytes4) * 1.0 / len(frames)))
    print('5: 2 + omit :length header')
    print('  len(bytes) = {0}, average = {1}'.format(
        len(bytes5), len(bytes5) * 1.0 / len(frames)))

frames = [
    Frame(Frame.TEXT, False, False, False, False, 1423),
    Frame(Frame.CONTINUATION, False, False, False, False, 123),
    Frame(Frame.CONTINUATION, False, False, False, False, 4123),
    Frame(Frame.CONTINUATION, False, False, False, False, 99),
    Frame(Frame.CONTINUATION, True, False, False, False, 0),
    Frame(Frame.TEXT, False, False, False, False, 133),
    Frame(Frame.CONTINUATION, False, False, False, False, 1),
    Frame(Frame.CONTINUATION, False, False, False, False, 1623),
    Frame(Frame.CONTINUATION, True, False, False, False, 588),
    Frame(Frame.TEXT, False, False, False, False, 9145),
    Frame(Frame.CONTINUATION, False, False, False, False, 76),
    Frame(Frame.CONTINUATION, False, False, False, False, 5128),
    Frame(Frame.CONTINUATION, False, False, False, False, 5689),
    Frame(Frame.CONTINUATION, False, False, False, False, 733),
    Frame(Frame.CONTINUATION, True, False, False, False, 42),
    Frame(Frame.TEXT, True, False, False, False, 929),
    Frame(Frame.TEXT, True, False, False, False, 1534),
    Frame(Frame.TEXT, True, False, False, False, 81),
    Frame(Frame.TEXT, False, False, False, False, 145),
    Frame(Frame.CONTINUATION, False, False, False, False, 1476),
    Frame(Frame.CONTINUATION, False, False, False, False, 814),
    Frame(Frame.CONTINUATION, False, False, False, False, 27),
    Frame(Frame.CONTINUATION, True, False, False, False, 439),
    Frame(Frame.BINARY, False, False, False, False, 15),
    Frame(Frame.CONTINUATION, False, False, False, False, 1376),
    Frame(Frame.CONTINUATION, False, False, False, False, 714),
    Frame(Frame.CONTINUATION, False, False, False, False, 17),
    Frame(Frame.CONTINUATION, True, False, False, False, 339),
    Frame(Frame.TEXT, False, False, False, False, 115),
    Frame(Frame.CONTINUATION, False, False, False, False, 11376),
    Frame(Frame.CONTINUATION, False, False, False, False, 7114),
    Frame(Frame.CONTINUATION, False, False, False, False, 117),
    Frame(Frame.CONTINUATION, True, False, False, False, 3139),
    Frame(Frame.TEXT, False, False, False, False, 1424),
    Frame(Frame.CONTINUATION, False, False, False, False, 124),
    Frame(Frame.CONTINUATION, False, False, False, False, 4124),
    Frame(Frame.CONTINUATION, False, False, False, False, 90),
    Frame(Frame.CONTINUATION, True, False, False, False, 1),
    Frame(Frame.TEXT, False, False, False, False, 134),
    Frame(Frame.CONTINUATION, False, False, False, False, 2),
    Frame(Frame.CONTINUATION, False, False, False, False, 1624),
    Frame(Frame.CONTINUATION, True, False, False, False, 589),
    Frame(Frame.TEXT, False, False, False, False, 9146),
    Frame(Frame.CONTINUATION, False, False, False, False, 77),
    Frame(Frame.CONTINUATION, False, False, False, False, 5129),
    Frame(Frame.CONTINUATION, False, False, False, False, 5680),
    Frame(Frame.CONTINUATION, False, False, False, False, 734),
    Frame(Frame.CONTINUATION, True, False, False, False, 43),
    Frame(Frame.BINARY, True, False, False, False, 920),
    Frame(Frame.BINARY, True, False, False, False, 1535),
    Frame(Frame.TEXT, True, False, False, False, 82),
    Frame(Frame.TEXT, False, False, False, False, 146),
    Frame(Frame.CONTINUATION, False, False, False, False, 1477),
    Frame(Frame.CONTINUATION, False, False, False, False, 815),
    Frame(Frame.CONTINUATION, False, False, False, False, 28),
    Frame(Frame.CONTINUATION, True, False, False, False, 430),
    Frame(Frame.BINARY, False, False, False, False, 16),
    Frame(Frame.CONTINUATION, False, False, False, False, 1377),
    Frame(Frame.CONTINUATION, False, False, False, False, 715),
    Frame(Frame.CONTINUATION, False, False, False, False, 18),
    Frame(Frame.CONTINUATION, True, False, False, False, 330),
    Frame(Frame.TEXT, False, False, False, False, 116),
    Frame(Frame.CONTINUATION, False, False, False, False, 11377),
    Frame(Frame.CONTINUATION, False, False, False, False, 7115),
    Frame(Frame.CONTINUATION, False, False, False, False, 118),
    Frame(Frame.CONTINUATION, True, False, False, False, 3130),
    Frame(Frame.TEXT, False, False, False, False, 1433),
    Frame(Frame.CONTINUATION, False, False, False, False, 133),
    Frame(Frame.CONTINUATION, False, False, False, False, 4133),
    Frame(Frame.CONTINUATION, False, False, False, False, 109),
    Frame(Frame.CONTINUATION, True, False, False, False, 10),
    Frame(Frame.TEXT, False, False, False, False, 143),
    Frame(Frame.CONTINUATION, False, False, False, False, 11),
    Frame(Frame.CONTINUATION, False, False, False, False, 1633),
    Frame(Frame.CONTINUATION, True, False, False, False, 598),
    Frame(Frame.TEXT, False, False, False, False, 9155),
    Frame(Frame.CONTINUATION, False, False, False, False, 86),
    Frame(Frame.CONTINUATION, False, False, False, False, 5138),
    Frame(Frame.CONTINUATION, False, False, False, False, 5699),
    Frame(Frame.CONTINUATION, False, False, False, False, 743),
    Frame(Frame.CONTINUATION, True, False, False, False, 52),
    Frame(Frame.TEXT, True, False, False, False, 939),
    Frame(Frame.TEXT, True, False, False, False, 1544),
    Frame(Frame.TEXT, True, False, False, False, 91),
    Frame(Frame.TEXT, False, False, False, False, 155),
    Frame(Frame.CONTINUATION, False, False, False, False, 1486),
    Frame(Frame.CONTINUATION, False, False, False, False, 824),
    Frame(Frame.CONTINUATION, False, False, False, False, 37),
    Frame(Frame.CONTINUATION, True, False, False, False, 449),
    Frame(Frame.BINARY, False, False, False, False, 25),
    Frame(Frame.CONTINUATION, False, False, False, False, 1386),
    Frame(Frame.CONTINUATION, False, False, False, False, 724),
    Frame(Frame.CONTINUATION, False, False, False, False, 27),
    Frame(Frame.CONTINUATION, True, False, False, False, 349),
    Frame(Frame.TEXT, False, False, False, False, 125),
    Frame(Frame.CONTINUATION, False, False, False, False, 11386),
    Frame(Frame.CONTINUATION, False, False, False, False, 7124),
    Frame(Frame.CONTINUATION, False, False, False, False, 127),
    Frame(Frame.CONTINUATION, True, False, False, False, 3149),
    Frame(Frame.TEXT, False, False, False, False, 1434),
    Frame(Frame.CONTINUATION, False, False, False, False, 134),
    Frame(Frame.CONTINUATION, False, False, False, False, 4134),
    Frame(Frame.CONTINUATION, False, False, False, False, 100),
    Frame(Frame.CONTINUATION, True, False, False, False, 11),
    Frame(Frame.TEXT, False, False, False, False, 144),
    Frame(Frame.CONTINUATION, False, False, False, False, 12),
    Frame(Frame.CONTINUATION, False, False, False, False, 1634),
    Frame(Frame.CONTINUATION, True, False, False, False, 599),
    Frame(Frame.TEXT, False, False, False, False, 9156),
    Frame(Frame.CONTINUATION, False, False, False, False, 87),
    Frame(Frame.CONTINUATION, False, False, False, False, 5139),
    Frame(Frame.CONTINUATION, False, False, False, False, 5690),
    Frame(Frame.CONTINUATION, False, False, False, False, 744),
    Frame(Frame.CONTINUATION, True, False, False, False, 53),
    Frame(Frame.BINARY, True, False, False, False, 930),
    Frame(Frame.BINARY, True, False, False, False, 1545),
    Frame(Frame.TEXT, True, False, False, False, 92),
    Frame(Frame.TEXT, False, False, False, False, 156),
    Frame(Frame.CONTINUATION, False, False, False, False, 1487),
    Frame(Frame.CONTINUATION, False, False, False, False, 825),
    Frame(Frame.CONTINUATION, False, False, False, False, 38),
    Frame(Frame.CONTINUATION, True, False, False, False, 440),
    Frame(Frame.BINARY, False, False, False, False, 26),
    Frame(Frame.CONTINUATION, False, False, False, False, 1387),
    Frame(Frame.CONTINUATION, False, False, False, False, 725),
    Frame(Frame.CONTINUATION, False, False, False, False, 28),
    Frame(Frame.CONTINUATION, True, False, False, False, 340),
    Frame(Frame.TEXT, False, False, False, False, 126),
    Frame(Frame.CONTINUATION, False, False, False, False, 11387),
    Frame(Frame.CONTINUATION, False, False, False, False, 7125),
    Frame(Frame.CONTINUATION, False, False, False, False, 128),
    Frame(Frame.CONTINUATION, True, False, False, False, 3140),
    Frame(Frame.CONTINUATION, False, False, False, False, 829),
    Frame(Frame.CONTINUATION, False, False, False, False, 41),
    Frame(Frame.CONTINUATION, True, False, False, False, 2601),
    Frame(Frame.BINARY, False, False, False, False, 18),
    Frame(Frame.CONTINUATION, False, False, False, False, 1298),
    Frame(Frame.CONTINUATION, False, False, False, False, 416),
    Frame(Frame.CONTINUATION, False, False, False, False, 21),
    Frame(Frame.CONTINUATION, True, False, False, False, 315),
    Frame(Frame.TEXT, False, False, False, False, 3892),
    Frame(Frame.CONTINUATION, False, False, False, False, 12345),
    Frame(Frame.CONTINUATION, False, False, False, False, 7201),
    Frame(Frame.CONTINUATION, False, False, False, False, 164),
    Frame(Frame.CONTINUATION, True, False, False, False, 3201),
    Frame(Frame.TEXT, False, False, False, False, 1507),
    Frame(Frame.CONTINUATION, False, False, False, False, 248),
    Frame(Frame.CONTINUATION, False, False, False, False, 3982),
    Frame(Frame.CONTINUATION, False, False, False, False, 400),
    Frame(Frame.CONTINUATION, True, False, False, False, 6),
    Frame(Frame.TEXT, False, False, False, False, 2344),
    Frame(Frame.CONTINUATION, False, False, False, False, 32),
    Frame(Frame.CONTINUATION, False, False, False, False, 218),
    Frame(Frame.CONTINUATION, True, False, False, False, 428),
    Frame(Frame.TEXT, False, False, False, False, 1392),
    Frame(Frame.CONTINUATION, False, False, False, False, 147),
    Frame(Frame.CONTINUATION, False, False, False, False, 6822),
    Frame(Frame.CONTINUATION, False, False, False, False, 910),
    Frame(Frame.CONTINUATION, False, False, False, False, 2677),
    Frame(Frame.CONTINUATION, True, False, False, False, 47),
    Frame(Frame.BINARY, True, False, False, False, 158),
    Frame(Frame.BINARY, True, False, False, False, 2346),
    Frame(Frame.TEXT, True, False, False, False, 183),
    Frame(Frame.TEXT, False, False, False, False, 228),
    Frame(Frame.CONTINUATION, False, False, False, False, 286),
    Frame(Frame.CONTINUATION, False, False, False, False, 421),
    Frame(Frame.CONTINUATION, False, False, False, False, 1426),
    Frame(Frame.CONTINUATION, True, False, False, False, 3201),
    Frame(Frame.BINARY, False, False, False, False, 4096),
    Frame(Frame.CONTINUATION, False, False, False, False, 821),
    Frame(Frame.CONTINUATION, False, False, False, False, 92),
    Frame(Frame.CONTINUATION, False, False, False, False, 683),
    Frame(Frame.CONTINUATION, True, False, False, False, 518),
    Frame(Frame.TEXT, False, False, False, False, 42),
    Frame(Frame.CONTINUATION, False, False, False, False, 32000),
    Frame(Frame.CONTINUATION, False, False, False, False, 157),
    Frame(Frame.CONTINUATION, False, False, False, False, 9209),
    Frame(Frame.CONTINUATION, True, False, False, False, 1),
]

random.seed(0)

measure_for_frames('no extension', frames)
print('')
measure_for_frames('with compress(1)', [
    Frame(f.opcode,
          f.fin,
          random.random() < 0.5 and f.opcode != Frame.CONTINUATION,
          f.rsv2,
          f.rsv3,
          f.length) for f in frames])
print('')
measure_for_frames('with compress(2)', [
    Frame(f.opcode,
          f.fin,
          f.opcode != Frame.CONTINUATION,
          f.rsv2,
          f.rsv3,
          f.length) for f in frames])
print('')
measure_for_frames('rsv bits are turned randomly on', [
    Frame(f.opcode,
          f.fin,
          random.random() < 0.2,
          random.random() < 0.2,
          random.random() < 0.2,
          f.length) for f in frames])
print('')
