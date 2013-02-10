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
from p.clusters import methods, colors

#| globals

title = 'cluster determinants'

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

def _xmlescape(m):
    return '_{}_'.format(ord(m.group()))

def _iname(s):
    s = re.sub(r'[^-+a-zA-Z0-9]', _xmlescape, s)
    return s


def makepage(path):
    u.path.chdir(path)
    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    p = path.split('-', 1)[1]
    project = path.split('-')[1]

#    pnum =  path.split('-')[-2].split('_')[-1]

    sys.stdout.write(u.html.head(ltitle, tip=True, maptip=True, tipfile='tip.html'))
    sys.stdout.write('''<script  language="JavaScript">
function checkmanualclustering() {
    var e = document.cluster.mthd;
    var v = e.options[e.selectedIndex].value;
    mform = document.getElementById("manualcluster");
    mform.style.visibility = "hidden";
    mform.style.display = "none";
    if (v == "man") {
        mform.style.visibility = "visible";
        mform.style.display = "block";
        mform.style.border = "thin dotted gray";
        mform.style.margin = "5px 0px 5px 0px";
        document.cluster.n.value="2";
    }
}
function checkdeterminantoptions() {
    var e = document.determinant.detmethod;
    var v = e.options[e.selectedIndex].value;
    var shib = document.getElementById('shibopts')
    var imp = document.getElementById('impopts')

    shib.style.visibility = 'hidden';
    shib.style.display = 'none';
    imp.style.visibility = 'hidden';
    imp.style.display = 'none';

    if (v == "shibboleth") {
        shib.style.visibility = 'visible';
        shib.style.display = 'block';
    } else if (v == "importance") {
        imp.style.visibility = 'visible';
        imp.style.display = 'block';
    }
}
function moverows(list1, list2)
{
    var sel='';
    var seltext='';
    for (i = list1.options.length - 1; i >= 0; i--) {
        if (list1.options[i].selected == true) {
            sel=list1.options[i].value;
            seltext=list1.options[i].text;
            var newrow = new Option(seltext,sel);
            list2.options[list2.length]=newrow;
            list1.options[i]=null;
        }
    }
}
function submitclusterform()
{
    var form = document.cluster;
    var m = form.mthd.options[form.mthd.selectedIndex].value;
    var outlist = form.labelsout;
    var inlist = form.labelsin;

    if (m == "man") {
        form.lin.value = "";
        form.lout.value = "";
        for (i = inlist.options.length - 1; i >= 0; i--) {
            form.lin.value += inlist.options[i].value + "#";
        }
        for (i = outlist.options.length - 1; i >= 0; i--) {
            form.lout.value += outlist.options[i].value + "#";
        }
    }
    form.submit();
}
</script>
        ''')
    sys.stdout.write('''
    {}
    <div class="pgcludet">
    <h2>cluster determinants</h2>
    '''.format(crumbs))

    if os.access('OK', os.F_OK):
        sys.stdout.write('<h3 id="s1">Step 1: cluster</h3>\n')
        if os.access('cluster-params', os.F_OK):
            fp = open('cluster-params', 'rt')
            method, groups = fp.read().split()
            fp.close()
        elif os.access('../clusters/current.txt', os.F_OK):
            fp = open('../clusters/current.txt', 'rt')
            method, groups, col = fp.read().split()
            fp.close()
        else:
            method, groups = ('wa', 6)

        fp = open('../data/Method', 'rt')
        project_type = fp.read().strip()
        fp.close()

        sys.stdout.write('''<p>
        <form name="cluster" action="{}bin/cludetform" method="post" enctype="multipart/form-data">
        <input type="hidden" name="p" value="{}">
        <input type="hidden" name="action" value="cluster">
        <fieldset style="line-height:150%"><legend>change parameters</legend>
        Clustering method:
        <select name="mthd" onchange="checkmanualclustering()">
        '''.format(u.config.appurl, project))
        methods['man'] = "Manual"
        for i in sorted(methods):
            sys.stdout.write('<!--{}:{} -->\n'.format(i, methods[i]))
            if i == method:
                sys.stdout.write('<option selected="selected" value="{}">{}</option>\n'.format(i, methods[i]))
            else:
                sys.stdout.write('<option value="{}">{}</option>\n'.format(i, methods[i]))
        sys.stdout.write('''
        </select><br>
        Number of clusters:
        <select name="n">
        ''')
        n = int(groups)
        maxnum = min(13, int(open('../data/stats.txt', 'rt').read().split()[0]))
        for i in range(2, maxnum):
            if i == n:
                sys.stdout.write('<option selected="selected">{}</option>\n'.format(i))
            else:
                sys.stdout.write('<option>{}</option>\n'.format(i))

        try:
            fp = open('currentcl', 'rt')
            curclnum = int(fp.read().rstrip())
            fp.close()
        except:
            curclnum =  1

        labels_in = []
        labels_out = []
        if os.access('clgroups.txt', os.F_OK):
            fp = open ('clgroups.txt', 'r')
            for line in fp:
                (gr, label) = line.strip().split()
                if int(gr) == curclnum:
                    labels_in.append(label)
                else:
                    labels_out.append(label)
        else:
            fp = open ('../data/labels.txt', 'r')
            for line in fp:
                (gr, label) = line.strip().split()
                labels_out.append(label)

        sys.stdout.write('</select><br>')

        moptvisible = '"visibility:hidden;display:none"';
        if method == 'man':
            moptvisible = '"border:thin dotted gray;margin:5px 0px 5px 0px;visibility:visible;display:block"';
        sys.stdout.write('''
        <div id="manualcluster" style={}>
        <input type="hidden" name="lin" value="x">
        <input type="hidden" name="lout" value="y">
        <table border="0">
        <tr><th>Labels outside the cluster</th>
            <th></th>
            <th>Labels in the cluster</th>
        <tr>
            <td><select name="labelsout" style="width:25em" size="10" multiple>
        '''.format(moptvisible))
        for l in labels_out:
            sys.stdout.write('<option value="{}">{}</option>\n'.format(l, l))

        sys.stdout.write('''
            <td valign="middle">
                <input type="Button" value=">>" 
                    onClick="moverows(document.cluster.labelsout,document.cluster.labelsin)"><br>
                <input type="Button" value="<<"
                    onClick="moverows(document.cluster.labelsin,document.cluster.labelsout)"><br>
            </td>
            <td><select name="labelsin" style="width:25em" size="10" multiple>
        ''')
        for l in labels_in:
            sys.stdout.write('<option value="{}">{}</option>\n'.format(l, l))

        sys.stdout.write('''
            </select>
            </td>
        </tr>
        </table>
        </div>
        ''')
        sys.stdout.write('<input type="button" value="Cluster" onclick="submitclusterform()"></fieldset></form>')



        if os.access('clmap.png', os.F_OK):
            sys.stdout.write(u.html.img(p + '-clmap', usemap="map1",
                                        idx=1, pseudoforce=True) + '\n')


        sys.stdout.write('''
        <h3 id="s2">Step 2: select cluster and determinant options</h3>
        <form action="{}bin/cludetform" method="post" 
              name="determinant" enctype="multipart/form-data">
        <input type="hidden" name="p" value="{}">
        <input type="hidden" name="action" value="determinant">
        '''.format(u.config.appurl, project))


        sys.stdout.write('<fieldset style="line-height:150%">\n')
        sys.stdout.write('<legend>determinant options</legend>\n');
        sys.stdout.write('Cluster of interest: ')
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

        if project_type.startswith('lev'):
            det_methods =  {
                'shibboleth': 'Distance based',
                'importance': 'Categorical'
            }
        else:
            det_methods =  {
                'shibboleth': 'Distance based'
            }

        if os.access('clusterdet-method', os.F_OK):
            fp = open('clusterdet-method', 'r')
            det_method = fp.read().strip()
            fp.close()
        else:
            det_method = "shibboleth"

        sys.stdout.write('''<br>Determinant: 
                <select name="detmethod" onchange="checkdeterminantoptions()">
            ''')
        selected = ""
        for i in sorted(det_methods):
            if i == det_method:
                selected = ' selected'
            else:
                selected = ""
            sys.stdout.write('''<option{} value="{}">{}</option>
                             '''.format(selected, i, det_methods[i]))
        sys.stdout.write('</select>{}\n'.format(u.html.help('cludetmethod')))
        norm_method = 'zscore'
        na_val = 0.8
        opt_diff = True
        if det_method == 'shibboleth':
            optvisible = ' style="visibility:visible;display:block"'
            if (os.access('clusterdet-params', os.F_OK)):
                fp = open('clusterdet-params', 'r')
                line = fp.read().strip()
                fp.close()
                norm_method = re.search('--norm=(\S+)', line).group(1)
                na_val = re.search('--ignore-na=([0-9.-]+)', line).group(1)
                opt_diff = re.search('--diff', line)
        else:
            optvisible = ' style="visibility:hidden;display:none"'

        sys.stdout.write(' <div id="shibopts"{}>'.format(optvisible)) 

        if(opt_diff):
            ratiosel=''
        else: 
            ratiosel='checked'

        if norm_method == 'none':
            nselected = "selected"
            zselected = ""
        else:
            zselected = "selected"
            nselected = ""

#        sys.stdout.write('''<br>Normalization:
#        <select name="norm">
#        <option value="none" {}>none</option>
#        <option value="zscore" {}>z-score</option>
#        </select>
#        '''.format(nselected, zselected))
        sys.stdout.write('''<br>Missing values: 
        <input type="text" size=3 name="narate" value={}>{}
        '''.format(na_val,u.html.help('cludetmethod#MissingData')))

#        sys.stdout.write('''<br>Use ratio? 
#               <input type="checkbox" name="ratio" value="ratio" {}>
#               if checked overall scores is `between / within', otherwise
#               `between - within'.
#        '''.format(ratiosel))

        sys.stdout.write('</div>\n')


        if det_method == 'importance':
            optvisible = ' style="visibility:visible;display:block"'
        else: 
            optvisible = ' style="visibility:hidden;display:none"'

        sys.stdout.write('''
        <div id="impopts"{} class="accents">
        These characters are ignored, unless checked:
        <div class="ipa2">
        '''.format(optvisible))

        accents = {}
        if (os.access('accents.txt', os.F_OK)):
            fp = open('accents.txt', 'rt')
            for line in fp:
                accents[int(line)] = False
            fp.close()

            if (os.access('accentscurrent.txt', os.F_OK)):
                fp = open('accentscurrent.txt', 'rt')
                for line in fp:
                    accents[int(line)] = True
                fp.close
        else:
            optvisible = False

        if accents:
            for i in sorted(accents):
                if i == 32:
                    s = 'SPACE'
                else:
                    s = '&nbsp;&#{};&nbsp;'.format(i)
                if accents[i]:
                    v = ' checked="checked"'
                else:
                    v = ''
                nm = unicodedata.name('{:c}'.format(i), '')
                if nm:
                    a1 = '<abbr title="{}">'.format(u.html.escape(nm))
                    a2 = '</abbr>'
                else:
                    a1 = a2 = ''
                sys.stdout.write('''<span class="cdc">{}
                                   <input type="checkbox" name="chr{}"{}>&nbsp;{}{}
                                   </span>\n'''.format(a1, i, v, s, a2))
        sys.stdout.write('</div></div>''')



        sys.stdout.write('''<br>
        <input type="submit" value="Select"><br>
        </fieldset>
        </form>
        <p>
        ''')

    # step 3

        if (os.access('score.txt', os.F_OK)):
            sys.stdout.write('''
            <h3 id="s3">Step 3: select item</h3>
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

            if det_method == 'importance':
                score_name = 'Importance'
                wtn_name = 'Representativeness'
                btw_name = 'Distinctiveness'
            else:
                score_name = 'Score'
                wtn_name = 'Within difference'
                btw_name = 'Between difference'

            fp = open('score.txt', 'rt')
            for line in fp:
                r, w, b, f = line.split()
                item = f
                if item == curitem:
                    sel = ' selected="selected"'
                else:
                    sel = ''
                sys.stdout.write('''
                    <option value="{}"{}>{:.2f} ({:.2f} : {:.2f}) &nbsp; {} 
                    </option>\n
                '''.format(item, sel, 
                           float(r), float(w), float(b),  _toStrHtml(item)))

            sys.stdout.write('''
            </select>
            <input type="submit" value="Select item">
            <br>The format of the select list is '{} ({} : {}) item.
            <br>&rarr; 
            <a href="cludetlist?p={}&t=success" target="_blank">download as list
            </a><br>
            </form>
            <p>
            '''.format(score_name, wtn_name, btw_name, project))

        if (os.access('score-failed.txt', os.F_OK)):
            fp = open('score-failed.txt')
            linecount = 0
            for line in fp:
                linecount = linecount + 1
            if (linecount > 0):
                sys.stdout.write('''
                {} items are ignored due to missing data (&rarr; 
                <a href="cludetlist?p={}&t=fail" target="_blank">
                download as list</a>)
                '''.format(linecount, project))

        if (os.access('currentlist.txt', os.F_OK)):
            fp = open('currentitem', 'rt')
            curitem = fp.read().strip()
            fp.close()

            fp = open('score.txt')
            for line in fp:
                r, wtn, btw, item = line.strip().split()
                if item == curitem:
                    break
            fp.close()

            sys.stdout.write('''
            Current item: {}
            <table cellspacing="0" cellpadding="0" border="0">
            <tr><td>{}:&nbsp;  <td>{}
            <tr><td>&mdash; {}:&nbsp;  <td>{}
            <tr><td>&mdash; {}:&nbsp; <td>{}
            </table>
            '''.format(_toStrHtml(curitem), score_name, r, 
                                            wtn_name, wtn, 
                                            btw_name, btw))

            if (det_method == 'shibboleth' 
                and os.access('itemmap.png', os.F_OK)):
                sys.stdout.write('''<br>Difference map for <i>{}</i>
                    (note: darker link color means higher difference)<br>
                '''.format(curitem))
                sys.stdout.write(u.html.img(p + '-itemmap', usemap="map1", 
                                    idx=1, pseudoforce=True) + '\n')

        if project_type.startswith('lev'):
    # step 4
            if (os.access('currentitem', os.F_OK)):
                sys.stdout.write('''
                    <h3 id="s4">Step 4: show the distribution of relevant forms</h3>
                    <form action="{}bin/cludetform" method="post" 
                          enctype="multipart/form-data">
                    <input type="hidden" name="p" value="{}">
                    <input type="hidden" name="action" value="formdist">
                    <table><tr><th style="padding-right:2em">Patterns in the cluster
                               </th>
                               <th>Patterns not in the cluster
                               </th>
                           </tr>
                '''.format(u.config.appurl, project))

                formsin = {}
                formsout = {}

    #            if (os.access('selectedforms.txt', os.F_OK)):
    #                fp = open("currentlist.txt", "rt")
    #                for line in 

                fp = open("currentlist.txt", "rt")
                for line in fp:
                    cin, cout, form = line.strip().split('\t')
                    if int(cin) == 0:
                        formsout[form] = (cin, cout)
                    else:
                        formsin[form] = (cin, cout)
                fp.close()
                

                selectedforms = set()
                if (os.access('selectedforms.txt', os.F_OK)):
                    fp = open('selectedforms.txt', 'rt')
                    for line in fp:
                        selectedforms.add(_toStrHtml(line.strip()))

                select_len = len(formsin)
                if select_len > 10: select_len = 10
                sys.stdout.write('''
                        <tr valign="top"> <td>
                        <select name="formsin" multiple="multiple" size="{}" class="ipaw">
                '''.format(select_len))

                for form, (cin, cout) in sorted(formsin.items(), 
                                            key=lambda x: int(x[1][0])/int(x[1][1]), 
                                            reverse=True):
                    if (form in selectedforms): sel=' selected="selected"'
                    else: sel = ''
                    sys.stdout.write('''<!-- {} -->\n'''.format(form))
                    sys.stdout.write('''<option value="{}"{}>{} ({}:{})</option>\n
                    '''.format(_iname(form), sel, _toStrHtml(form, True), cin, cout))

                select_len = len(formsout)
                if select_len > 10: select_len = 10
                sys.stdout.write('''</select></td><td>\n
                       <select name="formsout" multiple="multiple" size="{}" class="ipa2">
                '''.format(select_len))
                for form, (cin, cout) in formsout.items():
                    if (form in selectedforms): sel=' selected="selected"'
                    else: sel = ''
                    sys.stdout.write('''<option value="{}"{}>{} ({}:{})</option>\n
                    '''.format(_iname(form), sel, _toStrHtml(form, True), cin, cout))
                sys.stdout.write('</select></td></tr></table>\n')
                sys.stdout.write('<input type="submit" value="Show distribution map">\n')
                sys.stdout.write('</form>')

                if (os.access('distmap.png', os.F_OK)):
                    sys.stdout.write(u.html.img(p + '-distmap', usemap="map1", 
                                        idx=1, pseudoforce=True) + '\n')

    elif os.access('QUEUED', os.F_OK):
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1]))


    sys.stdout.write('</div>\n')
    sys.stdout.write(u.html.foot())

#| main
