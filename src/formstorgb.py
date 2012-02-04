#!__PYTHON3__

"""
Usage formstorgb item_file forms_file output_file

Output an RGB file to be used sith maprgb, such that only the sites
where forms in forms_file is observed has color, varying according to
the use of the file.

"""

import sys, re


colors = [x.replace(' ', '\n') for x in '''1 1 0.9979133
1 1 0.951178
1 1 0.904911
1 1 0.8595787
0.9936441 0.9975165 0.8157186
0.9766634 0.9908928 0.7751566
0.9537174 0.9819685 0.7408325
0.9261637 0.971293 0.7157217
0.8940859 0.9588669 0.7015761
0.853902 0.9431143 0.6966288
0.8013755 0.9221774 0.698484
0.7328502 0.8944876 0.7048092
0.6514241 0.8618412 0.7140098
0.5645519 0.8282048 0.7249673
0.4797463 0.797567 0.7365706
0.4021244 0.7716024 0.7476638
0.3317804 0.7471322 0.7569964
0.268176 0.7203667 0.7633064
0.2111159 0.6878304 0.76541
0.1631302 0.6485423 0.7627474
0.1280489 0.6027108 0.7550558
0.1096479 0.5505687 0.7420829
0.1079946 0.4933524 0.7240725
0.1174074 0.4338541 0.7020381
0.1317104 0.3750003 0.6770591
0.1449949 0.3195292 0.6498102
0.1528481 0.2691288 0.6187012
0.1513770 0.2251213 0.5813547
0.1368118 0.1887735 0.5354694
0.1090943 0.1596755 0.481082
0.07245721 0.1354784 0.4209323
0.03137255 0.1137255 0.3579104'''.split('\n')]

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

itemfn = sys.argv[1]
formsfn = sys.argv[2]
outfn = sys.argv[3]

fp = open(itemfn, encoding='iso-8859-1')
item = fp.read().strip()
fp.close()

forms = set()
fp = open(formsfn, 'rt')
for line in fp:
    f = re.sub('_([0-9]+)_', _num2chr, line.strip()).strip()
    forms.add(f)
    sys.stdout.write('fomrms += _{}_\n'.format(f))
fp.close()

fp = open('../data/_/{}.data'.format(item), 'rb')
placen = {}
placeall = {}
for line in fp:
    if line[:1] == b':':
        place = line[1:].decode('iso-8859-1').strip()
        if not place in placen:
            placen[place] = 0
            placeall[place] = 0
        sys.stdout.write('place: {}'.format(place))
    elif line[:1] == b'-':
        if line[1:].strip().decode('utf-8') in forms:
            placen[place] += 1
        placeall[place] += 1
        sys.stdout.write('form: _{}_\n'.format(line[1:].strip().decode('utf-8')))
fp.close()

fmin = 0.0
fmax = 1.0

ncols = len(colors)

fp = open(outfn, 'wt', encoding='iso-8859-9')
fp.write('3\n')
for place in placen:
    i = int(float(placen[place] / placeall[place]) * ncols)
    if i == ncols:
        i = ncols - 1
    fp.write('{}\n{}\n'.format(place, colors[i]))
#    if placen[place] > 0:
#        fp.write('{}\n0.9\n0\n0\n'.format(place))

fp.close()
