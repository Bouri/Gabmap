#!__PYTHON3__

"""
Usage makelongtips tip_template data_file output_file

"""

import sys, re

def _num2chr(m):
    return '{:c}'.format(int(m.group(1)))

def _unquote(s):
    s = s.strip()
    if len(s) < 2:
        return s
    if s[0] != '"' or s[-1] != '"':
        return s
    return re.sub(r'\\(.)', r'\1', s[1:-1]).strip()

if len(sys.argv) != 4:
    sys.exit("Usage %s clgroups_file cluster_number data_file" % sys.argv[0]);

tipfile = sys.argv[1]
data = sys.argv[2]
outfn = sys.argv[3]

forms = {}
fp = open(data, 'rb')
for line in fp:
    if line[:1] == b':':
        place = line[1:].decode('iso-8859-1').strip()
        forms[place] = ''
    elif line[:1] == b'-':
        form = line[1:].strip().decode('utf-8')
        if forms[place]:
            forms[place] += ' / ' + form
        else:
            forms[place] += form
fp.close()

fp = open(tipfile, 'rt')
fpout =  open(outfn, 'w')
for line in fp:
    for place, formstr in forms.items():
        if not re.search('<div id=\S+ class="tip"', line):
            fpout.write(line)
            break
        elif (re.search('>' + place + '<', line)):
            fpout.write(line.replace('>' + place + '<',
                           '>' + place + ' (' + formstr + ')<'))

fp.close()
fpout.close()
