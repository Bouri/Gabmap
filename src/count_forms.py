#!__PYTHON3__

"""
Usage count_forms clgroups_file cluster_number data_file

List the forms of an item, counting how many times each form occurs
within a given cluster and in the complete data set.

The output is a tab separated list of (1) the number of occurrences 
of the form inside the cluster, (2) total number of occurrences, (3)
the string representation of the form.

"""

import sys, re

def _unquote(s):
    s = s.strip()
    if len(s) < 2:
        return s
    if s[0] != '"' or s[-1] != '"':
        return s
    return re.sub(r'\\(.)', r'\1', s[1:-1]).strip()

if len(sys.argv) != 4:
    sys.exit("Usage %s clgroups_file cluster_number data_file" % sys.argv[0]);

fp = open("../data/Method", 'rt', encoding='iso-8859-1')
if (fp and not fp.read().startswith("lev")):
    fp.close()
    sys.exit(0)
fp.close()

clgroups = sys.argv[1]
targetcl = int(sys.argv[2])
datafile = sys.argv[3]

cluster = set()
fp = open(clgroups, 'rt', encoding='iso-8859-1')
for line in fp:
    a, b = line.split(None, 1)
    if int(a) == targetcl:
        cluster.add(_unquote(b))
fp.close()

variants = {}
variantsin = {}
fp = open(datafile, 'rb')
for line in fp:
    if line[:1] == b':':
        lbl = line[1:].strip().decode('iso-8859-1')
    elif line[:1] == b'-':
        v = line[1:].strip().decode('utf-8')
        if not v in variants:
            variants[v] = 0
            variantsin[v] = 0
        variants[v] += 1
        if lbl in cluster:
            variantsin[v] += 1

fp.close()
for v in variants:
    print('{}\t{}\t{}'.format(variantsin[v], variants[v], v))
