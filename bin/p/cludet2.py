#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

import os, re, sys, unicodedata

import u.path, u.html, u.config, u.distribute, u.setChar

#| globals

title = 'cluster determinants (difference based)'

#| functions


def _toStrHtml(s, em=False):
    if s == '__':
        if em:
            return '<em>(empty)</em>'
        else:
            return ''
    return u.html.escape(re.sub('_([0-9]+)_', _num2chr, s))

def _num2chr(m):
    return '{:c}'.format(int(m.group(1)))


def makepage(path):
    u.path.chdir(path)
    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    p = path.split('-', 1)[1]
    project = path.split('-')[1]

#    pnum =  path.split('-')[-2].split('_')[-1]

    sys.stdout.write(u.html.head(ltitle, tip=True, maptip=True))
    sys.stdout.write('''
    {}
    <div class="pgcludet">
    <h2>distance based cluster determinants (experimental)</h2>
    '''.format(crumbs))


    sys.stdout.write('<h3 id="s1">Step 1: select number of clusters</h3>\n')
    sys.stdout.write(u.html.img(p + '-clmap', usemap="map1", 
                                idx=1, pseudoforce=True) + '\n')

    fp = open('nclusters', 'rt')
    current = fp.read().split()
    fp.close()

    sys.stdout.write('''
    <p>
    <form action="{}bin/cludet2form" method="post" enctype="multipart/form-data">
    <input type="hidden" name="p" value="{}">
    <input type="hidden" name="action" value="number">
    Number of clusters:
    <select name="n">
    '''.format(u.config.appurl, project))
    n = int(current[0])
    for i in range(2, 13):
        if i == n:
            sys.stdout.write('<option selected="selected">{}</option>\n'.format(i))
        else:
            sys.stdout.write('<option>{}</option>\n'.format(i))
    sys.stdout.write('''
    </select>
    <input type="submit" value="Change number">
    </form>
    <p>
    ''')


    sys.stdout.write('''
    <h3 id="s2">Step 2: select cluster</h3>
    <form action="{}bin/cludet2form" method="post" enctype="multipart/form-data">
    <input type="hidden" name="p" value="{}">
    <input type="hidden" name="action" value="cluster">
    '''.format(u.config.appurl, project))

    try:
        fp = open('currentcl', 'rt')
        curclnum = int(fp.read().rstrip())
        fp.close()
    except:
        curclnum =  0

    sys.stdout.write('''
    Clusters in plot:
    '''.format(u.config.appurl, project))
    for i in range(1, n + 1):
        if i == curclnum:
            c = ' checked="checked"'
        else:
            c = ''
        sys.stdout.write('''
        <span class="s{0}">
        <input type="radio" name="c" value="{0}"{1}>
        </span>\n
        '''.format(i, c))

    sys.stdout.write('''
    <input type="submit" value="Select cluster">
    </form>
    <p>
    ''')

    if (os.access('score.txt', os.F_OK)):
        sys.stdout.write('''
        <h3 id="s3">step 3: select item</h3>
        <form action="{}bin/cludetform" method="post" enctype="multipart/form-data">
        <input type="hidden" name="p" value="{}">
        <input type="hidden" name="action" value="item">
        Items sorted by value:
        <select name="item">
        '''.format(u.config.appurl, project))

        try:
            fp = open('currentitem', 'rt')
            curitem = fp.read().rstrip()
            fp.close()
        except:
            curitem = ''

        fp = open('score.txt', 'rt')
        for line in fp:
            r, w, b, f = line.split()
            item = f[2:-5]
            if item == curitem:
                sel = ' selected="selected"'
            else:
                sel = ''
            sys.stdout.write('''
                <option value="{}"{}>{} ({} / {}) &nbsp; {} </option>\n
            '''.format(item, sel, r, w, b,  _toStrHtml(item)))

        sys.stdout.write('''
        </select>
        <input type="submit" value="Select item">
        <br>The format of the select list is 'ratio (within distance /
        between distance) item.
        <br>&rarr; <a href="cludet2list?p={}" target="_blank">download as list</a>
        </form>
        <p>
        '''.format(project))

#    sys.stdout.write('\n</div>\n')
    sys.stdout.write('</div>')
    sys.stdout.write(u.html.foot())


#| main
