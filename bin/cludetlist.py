#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/05/13"

#| imports

import cgitb; cgitb.enable(format="text")

import cgi, re, sys, os

import u.html, u.path
from u.login import username

def num2chr(m):
    return '{:c}'.format(int(m.group(1)))

def getval(field):
    return re.sub(r'\s+', ' ', form.getvalue(field, '')).strip()

#| main

u.html.loginCheck()

form = cgi.FieldStorage()

path = getval('p')

if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

u.path.chdir(username + '-' + path + '-cludet')

sys.stdout.write('''Content-type: text/plain; charset=utf-8
Cache-Control: no-cache
Pragma: no-cache

''')

if (getval('t') == 'fail'):
    filename = 'score-failed.txt'
else:
    filename = 'score.txt'

if os.access('clusterdet-method', os.F_OK):
    fp = open('clusterdet-method', 'r')
    det_method = fp.read().strip()
    fp.close()
else:
    det_method = "shibboleth"

if det_method == 'importance':
    score_name = 'Importance'
    wtn_name = 'Representativeness'
    btw_name = 'Distinctiveness'
else:
    score_name = 'Score'
    wtn_name = 'Within score'
    btw_name = 'Between score'

sys.stdout.write('{}\t{}\t{}\tItem\n'.format(score_name, wtn_name, btw_name))

fp = open(filename, 'rt')
for line in fp:
    a, b, c, d = line.rstrip().split("\t")
    sys.stdout.write('{}\t{}\t{}\t{}\n'.format(a, b, c, 
                                            re.sub('_([0-9]+)_', num2chr, d)))
fp.close()

