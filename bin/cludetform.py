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

def setClParams():
    method = getval('mthd')
    groups = int(getval('n'))

    assert groups >= 2 and groups <= 12
    fp = open('{}/templates/Makefile-cludet'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    fp = open('cluster-params', 'wt')
    fp.write('{} {}\n'.format(method, groups))
    fp.close()
    for f in 'score.txt score-failed.txt currentitem currentcl distmap.eps distmap.png currentlist.txt'.split():
            if os.access(f, os.F_OK):
                os.remove(f);

    if method == 'man':
        cin = getval('lin').rstrip('#').split('#')
        cout = getval('lout').rstrip('#').split('#')
        assert (len(cin) > 0 and len(cout) > 0)
        i = 0
        j = 0
        fp = open('cluster.txt', 'w')
        if len(cin) > 1:
            fp.write('1 0.1\n')
            fp.write('L {}\n'.format(cin[0]))
            fp.write('L {}\n'.format(cin[1]))
            dd = 0.1
            delta = 0.01
            for i in range(2,len(cin)):
                fp.write('{} {}\n'.format(i, dd + i*delta))
                fp.write('L {}\n'.format(cin[i]))
                fp.write('C {}\n'.format(i-1))
        if len(cout) > 1:
            fp.write('{} 0.1\n'.format(i+1))
            fp.write('L {}\n'.format(cout[0]))
            fp.write('L {}\n'.format(cout[1]))
            for j in range(2,len(cout)):
                fp.write('{} {}\n'.format(i+j, dd + j*delta))
                fp.write('L {}\n'.format(cout[j]))
                fp.write('C {}\n'.format(i+j-1))
        else:
            fp.write('{} 0.9\n'.format(i+1))
            fp.write('L {}\n'.format(cout[0]))
            fp.write('C {}\n'.format(i))
        if len(cin) == 1:
            fp.write('{} 0.9\n'.format(j+1))
            fp.write('L {}\n'.format(cin[0]))
            fp.write('C {}\n'.format(j))
        else:
            fp.write('{} 0.9\n'.format(j+i))
            fp.write('C {}\n'.format(i))
            fp.write('C {}\n'.format(i+j))
        fp.close()

    try:
        with open('../data/stats.txt', 'r') as fp:
            nPlaces = int(fp.read().strip().split()[0])
    except:
        nPlaces = 2
    u.queue.enqueue(path + '/cludet', 
                    make.format({'appdir': u.config.appdir, 
                                 'python3': u.config.python3, 
                                 'target': 's1',
                                 'nGroups': min(6, nPlaces)}))
    u.queue.run()
    time.sleep(2)

def setClDetParams():

    if getval('detmethod') == 'importance':
        cludet_method = "importance"
    else:
        cludet_method = "shibboleth"

    fp = open('clusterdet-method', 'w')
    fp.write('{}\n'.format(cludet_method))
    fp.close()

    try:
        na_rate = float(getval('narate'))
    except: 
        na_rate = 0


    diff = '--diff '
    if getval('ratio') == 'ratio':
        diff = ""

    norm = 'zscore'
    if getval('norm') == 'none':
        norm = 'none'

    fp = open('clusterdet-params', 'w')
    if cludet_method == 'shibboleth':
        fp.write('--norm={} --ignore-na={} {}\n'.format(norm, na_rate, diff))
    else:
        fp.write('\n') # TODO
    fp.close()
    c = getval('c')
    if not c:
        return
    c = int(c)
    fp = open('cluster-params', 'rt')
    clmethod, groups = fp.read().split()
    fp.close()
    assert c >= 1 and c <= int(groups)

    fp = open('currentcl', 'wt')
    fp.write('{}\n'.format(c))
    fp.close()

    if os.access('accents.txt', os.F_OK):
        fpin = open('accents.txt', 'rt')
        fpout = open('accentscurrent.txt', 'wt')
        for line in fpin:
            if getval('chr{}'.format(line.strip())):
                fpout.write(line)
        fpout.close()
        fpin.close()

    for f in 'score.txt score-failed.txt currentitem currentlist.txt distmap.eps distmap.png'.split():
            if os.access(f, os.F_OK):
                os.remove(f);
    fp = open('{}/templates/Makefile-cludet'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    u.queue.enqueue(path + '/cludet', 
                    make.format({'appdir': u.config.appdir, 
                                 'python3': u.config.python3, 
                                 'target': 's2'}))
    u.queue.run()
    while(os.access('QUEUED', os.F_OK)):
        time.sleep(2)


def setItem():
    i = getval('item')
    if not i:
        return
    for f in 'currentlist.txt selectedforms.txt distmap.eps distmap.png currentlist.txt'.split():
            if os.access(f, os.F_OK):
                os.remove(f);
    fp = open('currentitem', 'wt')
    fp.write('{}\n'.format(i))
    fp.close()
    fp = open('{}/templates/Makefile-cludet'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    u.queue.enqueue(path + '/cludet', 
                    make.format({'appdir': u.config.appdir, 
                                 'python3': u.config.python3, 
                                 'target': 's3'}))
    u.queue.run()
    while(os.access('QUEUED', os.F_OK)):
        time.sleep(2)

def setForms():
    fin = getval('formsin')
    fout = getval('formsout')
    fp = open('/tmp/cludet.dbg', "w")
    fp.write('{}\n'.format(fin))
    fp.write('{}\n'.format(fout))
    fp.close()

    if not (fin or fout):
        return

    fp = open('selectedforms.txt', 'wt')
    if (fin):
        fp.write('{}\n'.format(fin))
    if (fout):
        fp.write('{}\n'.format(fout))
    fp.close()
    fp = open('{}/templates/Makefile-cludet'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    u.queue.enqueue(path + '/cludet', 
                    make.format({'appdir': u.config.appdir, 
                                 'python3': u.config.python3, 
                                 'target': 's4'}))
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

u.path.chdir(username + '-' + path + '-cludet')

a = getval('action')

if not os.access('QUEUED', os.F_OK):
    if a == 'cluster':
        setClParams()
        target = '#s1'
    elif a == 'determinant':
        setClDetParams()
        target = '#s2'
    elif a == 'item':
        setItem()
        target = '#s3'
    elif a == 'formdist':
        setForms()
        target = '#s4'

sys.stdout.write('Location: goto?p={}-cludet{}\n\n'.format(path, target))
