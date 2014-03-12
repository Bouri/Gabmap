#!/usr/bin/env python3
"""
--documentation--
"""
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

u.path.chdir(username + '-' + path + '-align')

sys.stdout.write('''Content-type: text/plain; charset=utf-8
Cache-Control: no-cache
Pragma: no-cache

''')


fp = open("alignments.txt", 'rt')
sys.stdout.write('{}\n'.format(fp.read()))
fp.close()

