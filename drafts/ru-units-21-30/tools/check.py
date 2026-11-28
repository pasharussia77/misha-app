import importlib.util,json,re,unicodedata
sp=importlib.util.spec_from_file_location('c','content.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
known=set(json.load(open('/tmp/known.json',encoding='utf8')))
def st(x): return x.replace('`','').replace('\u0301','').lower()
def toks(x): return [st(t) for t in re.findall(r"[а-яА-ЯёЁ`]+",x)]
cum=set(known)
for u in sorted(m.U):
    d=m.U[u]
    for w in d['words']:
        for t in toks(w[1]): cum.add(t)
    bad={}
    def chk(label,txt):
        for t in toks(txt):
            if t not in cum: bad.setdefault(t,[]).append(label)
    for i,s in enumerate(d['sentences']): chk('sent%d'%(i+1),s[0])
    for i,s in enumerate(d['story']):
        if s[0]=='q':
            for o in s[2]: chk('storyQopt',o)
        else: chk('story%d'%(i+1),s[1])
    for c in d['chat']: chk('chat',c[1])
    for q in d['qa']: chk('qa',q[0]); chk('qa',q[3])
    print(u,d['title'],'UNKNOWN:',{k:sorted(set(v)) for k,v in bad.items()} or 'none')
