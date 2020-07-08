import re
import calendar

def journals(key):
    lib = {
      'arXiv e-prints': 'ArXiv',
      r'\apj': 'Astrophysical Journal',
      '\mnras': 'Monthly Notices of the Royal Astronomical Society',
      r'\aap': 'Astronomy and Astrophysics',
      r'\prd': 'Physical Review D',
    }
    if key in lib:
        return lib[key]
    else:
        return key

mon_num = {v.lower(): "%02d"%k for k, v in enumerate(calendar.month_abbr) if k>0}
def rm_spaces(string):
    base = string
    test = base.replace('\t', ' ')
    test = test.replace('  ', ' ')
    while test!=base:
        base = test
        test = base.replace('  ', ' ')
    return base
def get_info(data_line):
    data_use = data_line.split(' = ')
    keys = [d.split(',')[-1] for d in data_use][:-1]
    values = [','.join(d.split(',')[:-1]) for d in data_use]
    values = [rm_spaces(v) for v in values]
    out = {k: '' for k in ('author', 'title', 'journal', 'volume', 'page', 'month', 'year')}
    out['ref'] = values[0].replace('.', '')
    for k, v in zip(keys, values[1:]):
        #out[k.replace(' ', '')] = v
        out[k.replace(' ', '')] = v.replace('{', '').replace('}', '').replace('"', '')

    if 'howpublished' in out and out['journal']=='':
        out['journal'] = out['howpublished']
    return out
def abb_author(authors):
    if len(authors.split(' and '))>2:
        return '%s et al'%authors.split(' and ')[0].split(',')[0]
    else:
        return authors
def vol_page(pd):
    if pd['volume']==pd['page']=='':
        return ''
    elif pd['volume']=='':
        return ' %s,'%pd['page']
    elif pd['page']=='':
        return ' %s,'%pd['volume']
    else:
        return ' %s:%s,'%(pd['volume'], pd['page'])
def gen_file(pd):
    print(pd)
    date = '%s-%s-01'%(pd['year'], mon_num[pd['month'].lower()])
    filename = '%s-%s.md'%(date, pd['ref'])
    content = '\n'.join([
        '---',
        'title: "%s"'%pd['title'],
        'collection: publications',
        'permalink: /publication/%s'%filename[:-3],
        #'excerpt: "This paper is about the number 1. The number 2 is left for future work."',
        'date: %s'%date,
        'venue: "%s"'%journals(pd['journal']),
        'paperurl: "%s"'%pd['adsurl'],
        #'citation: "Your Name, You. (2009). &quot;Paper Title Number 1.&quot; <i>Journal 1</i>. 1(1)."',
        'citation: "%s. &quot;%s.&quot; <i>%s</i>,%s %s %s"'%(pd['author'], pd['title'], journals(pd['journal']),
                         vol_page(pd), pd['month'].capitalize(), pd['year']),
        '---',
        '',
        '[*ArXiv*](https://arxiv.org/abs/%s), [*ADS*](%s)'%(pd['eprint'], pd['adsurl']),
        #'This paper is about the number 1. The number 2 is left for future work.',
        #'[Download paper here](http://academicpages.github.io/files/paper1.pdf)',
        #'',
        #'Recommended citation: Your Name, You. (2009). "Paper Title Number 1." <i>Journal 1</i>. 1(1).',
        'Recommended citation: "%s (%s). &quot;%s.&quot; <i>%s</i>,%s %s %s"'%(abb_author(pd['author']),
                         pd['year'], pd['title'], journals(pd['journal']),
                         vol_page(pd), pd['month'].capitalize(), pd['year']),
        ])
    print '\n****%s\n_____\n%s\n'%(filename, content)
    return filename, content

if __name__=='__main__':
    import sys
    inbib =  sys.argv[1]
    data = ''.join(open(inbib, 'r').readlines())
    print data.split('\n@ARTICLE')[0]
    data = data.replace('\n', '')
    data_red = data.replace('  ', ' ')
    while data!=data_red:
        data = data_red
        data_red = data.replace('  ', ' ')
    
    data = data.split('@ARTICLE{')
    data = [d for dat in data for d in dat.split('@MISC{') if d!='']
    
    for dat in data:
        #print gen_file(get_info(dat))
        name, content = gen_file(get_info(dat))
        print name
        f = open('_publications/%s'%name, 'w')
        print >>f, content
        f.close()
