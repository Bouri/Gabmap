#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/05/13"

#| imports

import cgitb; cgitb.enable(format="html")

import os, re, sys, time

import u.html, u.config, u.path, u.queue, u.myCgi, u.hebci
from u.login import username
from p.cludetparms import *

#| globals

target = ''

#| functions

def _unquote(s):
    s = s.strip()
    if len(s) < 2:
        return s
    if s[0] != '"' or s[-1] != '"':
        return s
    return re.sub(r'\\(.)', r'\1', s[1:-1]).strip()

def _num2chr(m):
    return '{:c}'.format(int(m.group(1)))

def getval(field):
    return u.myCgi.data.get(field, b'').decode(codepage).strip()

def setNumber():
    n = int(getval('n'))
    assert n >= 2 and n <= 12
    fp = open('{}/templates/Makefile-cludet2'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    fp = open('nclusters', 'wt')
    fp.write('{}\n'.format(n))
    fp.close()
    for f in 'score.txt currentcl'.split():
            if os.access(f, os.F_OK):
                os.remove(f);
    u.queue.enqueue(path + '/cludet2', 
                    make.format({'appdir': u.config.appdir, 
                                 'python3': u.config.python3, 
                                 'target': 's1'}))
    u.queue.run()
    time.sleep(2)

def setCluster():
    c = getval('c')
    if not c:
        return
    c = int(c)
    fp = open('nclusters', 'rt')
    n = int(fp.read().split()[0])
    fp.close()
    assert c >= 1 and c <= n
    fp = open('currentcl', 'wt')
    fp.write('{}\n'.format(c))
    fp.close()
    for f in 'score.txt'.split():
            if os.access(f, os.F_OK):
                os.remove(f);
    fp = open('{}/templates/Makefile-cludet2'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    u.queue.enqueue(path + '/cludet2', 
                    make.format({'appdir': u.config.appdir, 
                                 'python3': u.config.python3, 
                                 'target': 's2'}))
    u.queue.run()
    while(os.access('QUEUED', os.F_OK)):
        time.sleep(2)


#| main

u.html.loginCheck()

codepage = 'us-ascii'
path = getval('p')

if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

u.path.chdir(username + '-' + path + '-cludet2')

a = getval('action')

if not os.access('QUEUED', os.F_OK):

    if a == 'number':
        setNumber()
        target = '#s1'
    elif a == 'cluster':
        setCluster()
        target = '#s2'

fp = open('/tmp/cludet2.dbg', "w")
fp.write('setting the value to: {}'.format(getval('n')))
fp.write('Location: goto?p={}-cludet2{}\n\n'.format(path, target))
fp.close()
sys.stdout.write('Location: goto?p={}-cludet2{}\n\n'.format(path, target))
