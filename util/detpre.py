#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This is detpre.py
    Copyright (C) 2011 Peter Kleiweg

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2011/06/20"


#| imports

import cgitb; cgitb.enable(format="text")

import os

import u.setChar

#| globals

defaults = '''
02B0  MODIFIER LETTER SMALL H
02B1  MODIFIER LETTER SMALL H WITH HOOK
02B2  MODIFIER LETTER SMALL J
02B3  MODIFIER LETTER SMALL R
02B4  MODIFIER LETTER SMALL TURNED R
02B5  MODIFIER LETTER SMALL TURNED R WITH HOOK
02B6  MODIFIER LETTER SMALL CAPITAL INVERTED R
02B7  MODIFIER LETTER SMALL W
02B8  MODIFIER LETTER SMALL Y
02C0  MODIFIER LETTER GLOTTAL STOP
02C1  MODIFIER LETTER REVERSED GLOTTAL STOP
02E0  MODIFIER LETTER SMALL GAMMA
02E1  MODIFIER LETTER SMALL L
02E2  MODIFIER LETTER SMALL S
02E3  MODIFIER LETTER SMALL X
02E4  MODIFIER LETTER SMALL REVERSED GLOTTAL STOP
0363  COMBINING LATIN SMALL LETTER A
0364  COMBINING LATIN SMALL LETTER E
0365  COMBINING LATIN SMALL LETTER I
0366  COMBINING LATIN SMALL LETTER O
0367  COMBINING LATIN SMALL LETTER U
0368  COMBINING LATIN SMALL LETTER C
0369  COMBINING LATIN SMALL LETTER D
036A  COMBINING LATIN SMALL LETTER H
036B  COMBINING LATIN SMALL LETTER M
036C  COMBINING LATIN SMALL LETTER R
036D  COMBINING LATIN SMALL LETTER T
036E  COMBINING LATIN SMALL LETTER V
036F  COMBINING LATIN SMALL LETTER X
207F  SUPERSCRIPT LATIN SMALL LETTER N
'''.strip().split('\n')


#| functions

#| main

if os.access('../data/UTF', os.F_OK):

    charset = set()

    if not os.access('accents.txt' ,os.F_OK):
        fpin = open('../data/charcount.txt', 'rt')
        fpout = open('accents.txt', 'wt')
        for line in fpin:
            i = int(line.split()[0])
            c = u.setChar.ci(i)
            if c != 'V' and c != 'S' and c != 'C':
                fpout.write('{}\n'.format(i))
        fpout.close()
        fpin.close()

    accents = {}
    fp = open('accents.txt', 'rt')
    for line in fp:
        accents[int(line)] = False
    fp.close()

    if not os.access('accentscurrent.txt' ,os.F_OK):
        fp = open('accentscurrent.txt', 'wt')
        for j in defaults:
            i = int(j.split()[0], 16)
            if i in accents:
                fp.write('{}\n'.format(i))
        fp.close()

    fp = open('accentscurrent.txt', 'rt')
    for line in fp:
        charset.add(int(line))
    fp.close()
    fp = open('../data/charcount.txt', 'rt')
    for line in fp:
        i = int(line.split()[0])
        k = u.setChar.ci(i)
        if k == 'V' or k == 'S' or k == 'C':
            charset.add(i)
    fp.close()

    fp = open('currentchars-u.txt', 'wt', encoding='utf-8')
    for i in sorted(charset):
        fp.write('{:c}\n'.format(i))
    fp.close()
    
else:

    fp = open('currentchars-1.txt', 'wt', encoding='iso-8859-1')
    for i in ' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
        fp.write(i + '\n')
    fp.close()
