#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/07/14"

#| imports

import cgitb; cgitb.enable(format="text")

import os, pickle, re ,math, sys

import u.setChar as setChar

from p.cludetparms import SlowBeta2 as B2
from p.cludetparms import Sep, Limit

#| globals

if sys.argv[1] == '-d':
    sys.argv.pop(1)
    dump = True
else:
    dump = False

clufile = 'clgroups.txt'
target = int(sys.argv[1])
datafile = sys.argv[2]

minvar = 2

#| functions

def _esc(m):
    return '_{}_'.format(ord(m.group()))

def _escape(s):
    if not s:
        return '__'
    return re.sub(r'[^-+a-zA-Z0-9]', _esc, s)

def _unquote(s):
    s = s.strip()
    if len(s) < 2:
        return s
    if s[0] != '"' or s[-1] != '"':
        return s
    return re.sub(r'\\(.)', r'\1', s[1:-1]).strip()


#| main

partition = set()
fp = open(clufile, 'rt', encoding='iso-8859-1')
for line in fp:
    a, b = line.split(None, 1)
    if int(a) == target:
        partition.add(_unquote(b))
fp.close()

fp = open('dst.pickle', 'rb')
labels, idx, dst = pickle.load(fp)
fp.close()

nPlaces = len(labels)
nPlacesIn = len(partition)

RelSize = nPlacesIn / nPlaces

variants = {}
allvars = [0] * nPlaces
subst = {}

fp = open(datafile, 'rb')
encoding = 'iso-8859-1'
ignore = re.compile('[^ a-zA-Z0-9]+')
for line in fp:
    if line.startswith(b'%utf8'):
        encoding = 'utf-8'
        ign = setChar.Vowel.union(setChar.Consonant).union(setChar.Semivowel)
        first = ''
        if os.access('accentscurrent.txt', os.F_OK):
            fp1 = open('accentscurrent.txt', 'rt')
            for line in fp1:
                c = '{:c}'.format(int(line))
                if c == '-':
                    first = '-'
                elif c == '[' or c == ']' or c == '\\':
                    ign.add('\\' + c)
                else:
                    ign.add(c)
            fp1.close()
        ignore = re.compile('[^' + first + ''.join(ign) + ']+')
    elif line[:1] == b':':
        lbl = line.decode('iso-8859-1')[1:].strip()
    elif line[:1] == b'-':
        var1 = line.decode(encoding)[1:].strip()
        variant = ignore.sub('', var1).strip()
        if not variant in variants:
            variants[variant] = {}
            subst[variant] = set()
        subst[variant].add(_escape(var1))
        if not lbl in variants[variant]:
            variants[variant][lbl] = 1
        else:
            variants[variant][lbl] += 1
        allvars[idx[lbl]] += 1
fp.close()

n = 0
for i in range(nPlaces):
    if allvars[i] > 0 and labels[i] in partition:
        n += 1
if n < 3:
    sys.stdout.write('\n0.00 0.00 0.00 0.00 0.00 0:0\n')
    sys.exit()


items = []

rejected = []

for variant in variants:
    n = sum(variants[variant].values())
    if n < minvar:
        continue
    p = [False] * nPlaces
    for i in range(nPlaces):
        if allvars[i] > 0:
            lbl = labels[i]
            if lbl in variants[variant]:
                p[i] = [variants[variant][labels[i]], allvars[i]]
            else:
                p[i] = [0, allvars[i]]
    for i in range(nPlaces):
        if allvars[i] == 0:
            sum1 = 0
            sum2 = 0
            for j in range(nPlaces):
                if allvars[j]:
                    lbl = labels[j]
                    if lbl in variants[variant]:
                        n1 = variants[variant][lbl]
                    else:
                        n1 = 0
                    n2 = allvars[j]
                    d = math.pow(dst[i][j], Sep)
                    sum1 += n1 / d
                    sum2 += n2 / d
            p[i] = [sum1, sum2]

    TP = FP = FN = TN = 0.0
    for i in range(nPlaces):
        lbl = labels[i]
        if lbl in partition:
            tp = p[i][0] / p[i][1]
            TP += tp
            FN += 1 - tp
        else:
            fp = p[i][0] / p[i][1]
            FP += fp
            TN += 1 - fp
    if not TP:
        rejected.append(variant)
        continue

    prec = TP / (TP + FP)
    reca = TP / (TP + FN)
    f = (1 + B2) * prec * reca / (B2 * prec + reca)
    dist = (prec - RelSize) / (1 - RelSize)
    if dist > 0:
        imp = (dist + reca) / 2.0
    else:
        imp = 0.0
    items.append((f, prec, reca, imp, dist, variant, p))

items.sort(reverse=True)

ppp = []
for i in range(nPlaces):
    ppp.append([0, 0])
Fscore = 0
Prec = 0
Reca = 0

nnn = 0
nnnp = 0
for f, p, r, imp, dist, v, pp in items:
    for i in range(nPlaces):
        pp[i][0] += ppp[i][0]
    TP = FP = FN = TN = 0.0
    for i in range(nPlaces):
        lbl = labels[i]
        if lbl in partition:
            tp = pp[i][0] / pp[i][1]
            TP += tp
            FN += 1 - tp
        else:
            fp = pp[i][0] / pp[i][1]
            FP += fp
            TN += 1 - fp
    if not TP:
        rejected.append(v)
        continue
    prec = TP / (TP + FP)
    reca = TP / (TP + FN)
    ff = (1 + B2) * prec * reca / (B2 * prec + reca)

    if ff < Fscore * Limit:
        rejected.append(v)
    else:
        Fscore = ff
        Prec = prec
        Reca = reca
        for i in range(nPlaces):
            ppp[i][0] = pp[i][0]
            ppp[i][1] = pp[i][1]
        n = sum(variants[v].values())
        np = sum([variants[v][lbl] for lbl in variants[v] if lbl in partition])
        nnn += n
        nnnp += np
        sys.stdout.write('{:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {}:{} [ {} ]\n'.format(
            f, p, r, imp, dist, _escape(v), np, n, ' | '.join(sorted(subst[v]))))

rejected.sort()
for r in rejected:
    i = o = 0
    for lbl in range(nPlaces):
        if allvars[lbl] > 0:
            if labels[lbl] in variants[r]:
                n = variants[r][labels[lbl]]
            else:
                n = 0
            if labels[lbl] in partition:
                i += n
            else:
                o += n
    sys.stdout.write('[{}  {}:{}]\n'.format(_escape(r), i, i + o))

Dist = (Prec - RelSize) / (1 - RelSize)
if Dist > 0:
    Imp = (Dist + Reca) / 2.0
else:
    Imp = 0.0
sys.stdout.write('\n{:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {}:{}\n'.format(Fscore, Prec, Reca, Imp, Dist, nnnp, nnn))

if dump:
    fp1 = open('dump1.rgb', 'wt', encoding='iso-8859-1')
    fp2 = open('dump2.rgb', 'wt', encoding='iso-8859-1')
    fp1.write('3\n')
    fp2.write('3\n')
    for i in range(nPlaces):
        fp1.write(labels[i] + '\n')
        fp2.write(labels[i] + '\n')
        f = ppp[i][0] / ppp[i][1]
        if allvars[i] > 0:
            fp1.write('{0}\n{0}\n{0}\n'.format(1 - f))
        else:
            fp1.write('1\n.5\n.5\n')
        fp2.write('{0}\n{0}\n{0}\n'.format(1 - f))
    fp2.close()
    fp1.close()