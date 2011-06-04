#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

#import locale
import os, re, sys

import u.path, u.html, u.config

#| globals

title = 'items'

#| functions

def _num2chr(m):
    return '{:c}'.format(int(m.group(1)))


def _unquote(s):
    s = s.strip()
    if len(s) < 2:
        return s
    if s[0] != '"' or s[-1] != '"':
        return s
    return re.sub(r'\\(.)', r'\1', s[1:-1]).strip()

def _num2chr(m):
    return '{:c}'.format(int(m.group(1)))

def _iso2utf(s):
    if not s:
        return ''
    return re.sub('&#([0-9]+);', _num2chr, s)


def makepage(path):

    u.path.chdir(path[:-9])
    os.chdir('data')

    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    p = path.split('-', 1)[1]
    pnum =  path.split('-')[-2].split('_')[-1]

    sys.stdout.write(u.html.head(ltitle))
    sys.stdout.write('''
    {}
    <div class="pgitems">
    <h2>{}</h2>
    '''.format(crumbs, title))

    if os.access('OK', os.F_OK):

        sys.stdout.write('''
        <div class="info">
        This is a list of all items &mdash; the column labels &mdash; in your data set.<br>
        The number (if any) says how many values are missing for each item.
        <br>&nbsp;<br>
        Click on a number to get a map of missing values.
        </div>
        <table class="items" cellspacing="0" cellpadding="0" border="0">
        ''')

        lines = []
        fp = open('NAs.txt', 'rt', encoding='utf-8')
        n = -1
        for line in fp:
            n += 1
            a = line.split('\t')
            lines.append((a[1].strip(), int(a[0]), n))
        fp.close()
        lines.sort()
        
        for item, i, n in lines:
            if i == 0:
                i = ''
            else:
                i = '<a href="namap?{}-{}" target="_blank">{}</a>'.format(pnum, n, i)                
            sys.stdout.write('<tr><td align="right">{}<td>{}\n'.format(i, u.html.escape(item.strip())))
        sys.stdout.write('</table>\n')


    elif os.access('QUEUED', os.F_OK):
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1].replace('numitems', 'data')))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())



#| main