from playwright.sync_api import sync_playwright
import json,re,importlib.util
A='\u0301'
def plain(t): return re.sub(r'[\u0301`]','',t).strip().lower()
def norm(t): return re.sub(r'[^\w\s]','',plain(t)).strip()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/misha-app/index.html'); pg.wait_for_timeout(1500)
    D=pg.evaluate("""()=>{const o={};for(const k of Object.keys(UNITS)){const u=UNITS[k];o[k]={title:u.title,words:u.words.map(w=>w.ru),sents:u.sentences.map(s=>s.ru),story:u.story.filter(x=>!x.q).map(x=>({who:x.who,ru:x.ru,en:x.en})),chat:(u.chat||[]).map(x=>({ru:x.ru||x[1],en:x.en||x[2]})),tips:u.tips||[]}}return o}""")
    b.close()
sp=importlib.util.spec_from_file_location('c','content.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
for u,d in m.U.items():
    D[str(u)]=dict(title=d['title'],words=[w[1] for w in d['words']],sents=[s[0] for s in d['sentences']],
      story=[dict(who=x[0],ru=x[1],en=x[2]) for x in d['story'] if x[0]!='q'],chat=[dict(ru=c[1],en=c[2]) for c in d['chat']],tips=d['tips'])
json.dump(D,open('allunits.json','w'),ensure_ascii=False)
bank_s={norm(s) for d in D.values() for s in d['sents']}; bank_w={norm(w) for d in D.values() for w in d['words']}
n=0
for u in sorted(D,key=int):
    d=D[u]; out=[]
    for i,x in enumerate(d['story'],1):
        t=norm(x['ru'])
        if t in bank_s or t in bank_w: continue
        out.append(f"{u}.{i} {x['ru'].replace(A,'').replace('`','')} | {x['en']}")
    for i,x in enumerate(d['chat'],1):
        t=norm(x['ru'])
        if t in bank_s or t in bank_w: continue
        out.append(f"{u}.c{i} {x['ru'].replace(A,'').replace('`','')} | {x['en']}")
    n+=len(out); print('##',u,d['title']); print('\n'.join(out))
print('TOTAL not in bank',n)
