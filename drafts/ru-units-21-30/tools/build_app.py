import json,re,hashlib,shutil,os,importlib.util,glob,sys,unicodedata
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0,'/home/claude/u2130'); sys.path.insert(0,'/home/claude/u2130/pics')
REPO='/home/claude/misha-app'; W='/home/claude/u2130'; A='\u0301'
f=lambda s:s.replace('`',A)
sp=importlib.util.spec_from_file_location('c',W+'/content.py'); C=importlib.util.module_from_spec(sp); sp.loader.exec_module(C)
import picdata, scenes
over_none={'atvyet','sabirat','osyenyu','vyesnoy'}
draw={i for i in scenes.D}                     # 89 + staryy below
draw.add('staryy')
# ---------- 1. pictures -> transparent webp ----------
def to_webp(src,dst):
    im=Image.open(src).convert('RGB'); a=np.array(im).astype(int)
    white=(a.min(2)>=238); lab,n=ndimage.label(white)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bg=np.isin(lab,list(border))
    alpha=(~bg).astype(float); alpha=ndimage.gaussian_filter(alpha,0.7); alpha=np.clip(alpha*1.15,0,1)
    rgba=np.dstack([a.astype(np.uint8),(alpha*255).astype(np.uint8)]); img=Image.fromarray(rgba,'RGBA')
    bb=img.getchannel('A').point(lambda v:255 if v>20 else 0).getbbox() or (0,0,*img.size)
    m=int(0.03*1024); bb=(max(0,bb[0]-m),max(0,bb[1]-m),min(1024,bb[2]+m),min(1024,bb[3]+m)); img=img.crop(bb)
    s=max(img.size); sq=Image.new('RGBA',(s,s),(0,0,0,0)); sq.paste(img,((s-img.size[0])//2,(s-img.size[1])//2)); sq=sq.resize((320,320),Image.LANCZOS)
    tmp=dst+'.tmp'; sq.save(tmp,'WEBP',quality=84,alpha_quality=90,method=6); h=hashlib.sha1(open(tmp,'rb').read()).hexdigest()[:12]
    out=f'{REPO}/img/{h}.webp'; os.replace(tmp,out); return h
PIC={}
for i in sorted(draw):
    PIC[i]=to_webp(f'{W}/pics/raw/{i}.png',f'{W}/pics/tmp_{i}')
print('pictures',len(PIC),'avg KB',round(sum(os.path.getsize(f'{REPO}/img/{h}.webp') for h in PIC.values())/len(PIC)/1024,1))
IMG=lambda h:f"<img class='wp' src='img/{h}.webp' alt=''>"
ICON={21:'gitara',22:'vapros',23:'magazin',24:'avtobus',25:'khobbi',26:'vchyera',27:'poyezd',28:'krasivyy',29:'klass',30:'zima'}
# ---------- 2. adopted phrases ----------
ph=json.load(open(W+'/audio/phrases.json',encoding='utf8'))
NEWU={21,22,29}
for x in ph:
    if x['unit'] in NEWU: C.U[x['unit']]['sentences'].append((x['ru'].replace(A,'`'),x['en'],1))
OLD=[x for x in ph if x['unit'] not in NEWU]
# ---------- 3. word ids unique ----------
existing=set(re.findall(r'id:"([a-z0-9_]+)"',open(REPO+'/index.html',encoding='utf8').read()))
ren={}
def wid(i,u):
    return i if i not in existing else f'{i}_{u}'
# ---------- 4. unit objects ----------
CL={21:('#B5499B','#8C3778'),22:('#2F7FD0','#2160A3'),23:('#D98B1F','#A8680F'),24:('#3FA66A','#2D7C4E'),25:('#D6475B','#A8344A'),26:('#6A5ACD','#4F42A0'),27:('#1FA3B8','#167C8C'),28:('#E0662D','#B04C1E'),29:('#7A9E2A','#5C781E'),30:('#4A6FA5','#34507B')}
def toks(s): return [t.strip('.,!?»«—-') for t in s.split()]
def stripacc(s): return unicodedata.normalize('NFC',''.join(c for c in unicodedata.normalize('NFD',s) if c not in '\u0301')).lower()
UN={}
for u,d in sorted(C.U.items()):
    idm={w[0]:wid(w[0],u) for w in d['words']}
    words=[dict(id=idm[w[0]],ru=f(w[1]),en=w[2],tr=w[3],pic=(IMG(PIC[w[0]]) if w[0] in PIC else '')) for w in d['words']]
    groups=[[idm[i] for i in g] for g in d['groups']]
    sents=[dict(ru=f(s[0]),en=s[1],set=s[2],src='C') for s in d['sentences']]
    sent_tokens=[(t,stripacc(t)) for s in sents for t in toks(s['ru'])]
    blank=[]
    for w in d['words']:
        if ' ' in w[1] or w[1].startswith('не'): continue
        k=stripacc(f(w[1]))
        for t,ts in sent_tokens:
            if ts==k and t not in blank: blank.append(t); break
    story=[]
    for x in d['story']:
        story.append(dict(who=x[0],ru=f(x[1]),en=x[2]) if x[0]!='q' else dict(q=x[1],options=[f(o) for o in x[2]],answer=x[3]))
    UN[u]=dict(title=d['title'],cls=f'u{u}',icon=IMG(PIC[ICON[u]]),storyTitle=d['storyTitle'],doneLine=f(d['doneLine']),words=words,groups=groups,sentences=sents,blankable=blank,story=story,
        chat=[[c[0],f(c[1]),c[2]] for c in d['chat']],tips=[f(t) for t in d['tips']],qa=[dict(q=f(q[0]),hint=q[1],pic=q[2],a=f(q[3])) for q in d['qa']])
unit_js='Object.assign(UNITS, '+json.dumps(UN,ensure_ascii=False,indent=1)+');\n'
old_js='/* Useful story phrases now taught as sentences (Galina, Nov 2026) */\n[\n'+',\n'.join(f'  [{x["unit"]}, {json.dumps(dict(ru=x["ru"],en=x["en"],set=1,src="C"),ensure_ascii=False)}]' for x in OLD)+'\n].forEach(([u, s]) => UNITS[u].sentences.push(s));\n'
# ---------- 5. gloss ----------
need=json.load(open(W+'/gloss_need.json',encoding='utf8'))
MAN={'гитаре':'«на гитаре» = (play) the guitar','волнуйся':'«не волнуйся» = don’t worry','извините':'excuse me / sorry (polite)','потому':'«потому что» = because','магазине':'«в магазине» = in the store',
'музее':'«в музее» = in the museum','улице':'«на улице» = outside, on the street','библиотеке':'«в библиотеке» = in the library','стадион':'«на стадион» = (go) to the stadium','автобусе':'«на автобусе» = by bus',
'школу':'«в школу» = (go) to school','библиотеку':'«в библиотеку» = (go) to the library','поезде':'«на поезде» = by train','машине':'«на машине» = by car','он':'he','здравствуй':'hello (to a friend or a child)',
'уроке':'«на уроке» = in class','перемене':'«на перемене» = at recess','классе':'«в классе» = in the classroom','рождения':'«день рождения» = birthday','мае':'«в мае» = in May','июле':'«в июле» = in July',
'январе':'«в январе» = in January','декабре':'«в декабре» = in December','может':'«может быть» = can be','быть':'«может быть» = can be'}
G={}
for k,v in need.items():
    G[k]=MAN.get(k) or v
    assert G[k],k
gloss_js='Object.assign(GLOSS, '+json.dumps(G,ensure_ascii=False)+');\n'
# ---------- 6. css ----------
css=''
for u,(c,dk) in CL.items():
    css+=f'.unitcard.u{u}{{background:{c};box-shadow:0 6px 0 {dk}}}\n.popcard.u{u}{{background:{c};box-shadow:0 6px 0 {dk}}}\n.popcard.u{u}::before{{background:{c}}}\n.popcard.u{u} button{{color:{dk}}}\n.path.p{u}{{--uc:{c};--ucd:{dk};--ucl:{c}55;--ucld:{c}88;--ucf:{c}3D}}\n'
# ---------- 7. patch index.html ----------
p=REPO+'/index.html'; s=open(p,encoding='utf8').read()
def once(a,b,after=False):
    global s
    assert s.count(a)==1,(a[:50],s.count(a)); s=s.replace(a,(a+b) if after else (b+a))
once('let UNIT_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20];',unit_js+'\n')
s=s.replace('let UNIT_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20];','let UNIT_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30];\n'+old_js)
i=s.index('let GLOSS = {'); j=s.index('\n};',i)+3; s=s[:j]+'\n'+gloss_js+s[j:]
once('let WHO = {misha:"Ми́ша", mama:"Ма́ма", papa:"Па́па", tima:"Ти́ма"};','let WHO = {misha:"Ми́ша", mama:"Ма́ма", papa:"Па́па", tima:"Ти́ма", teacher:"Учи́тель"};'); s=s.replace('let WHO = {misha:"Ми́ша", mama:"Ма́ма", papa:"Па́па", tima:"Ти́ма"};\nlet WHO = ','let WHO = ') if False else s
s=s.replace('  tima: () => "🦔"\n};','  tima: () => "🦔",\n  teacher: () => "🧑‍🏫"\n};',1); assert 'teacher: () =>' in s
a='.path.p20{--uc:#4E7F2C;--ucd:#385D1F;--ucl:#4E7F2C55;--ucld:#4E7F2C88;--ucf:#4E7F2C3D}\n'
assert a in s; s=s.replace(a,a+css)
open(p,'w',encoding='utf8').write(s)
json.dump(dict(PIC=PIC,idm={u:{w[0]:wid(w[0],u) for w in d['words']} for u,d in C.U.items()}),open(W+'/build_maps.json','w'))
# ---------- 8. audio ----------
vk=lambda t: re.sub(r'\s+',' ',re.sub(r'[«»“”"\'()¿¡.,:;…]','',unicodedata.normalize('NFC',t).lower())).strip()
idx=json.load(open(REPO+'/voices/ru/index.json')); clips=idx['clips']; used_ids={i for d in clips.values() for i in d.values()}
def add(role,display,src):
    i=hashlib.sha1(f'{role}|{display}'.encode()).hexdigest()[:12]; assert i not in used_ids or clips.get(role,{}).get(vk(display))==i,(role,display,i)
    shutil.copy(src,f'{REPO}/voices/ru/{i}.mp3'); clips.setdefault(role,{})[vk(display)]=i; used_ids.add(i); return i
n=0
log=json.load(open(W+'/audio/gen-log-new.json',encoding='utf8')); cur={}
for r in log:
    if not r.get('superseded'): cur[(r['unit'],r['line'])]=r
for u,d in sorted(C.U.items()):
    L=[x for x in d['story'] if x[0]!='q']
    for i,x in enumerate(L,1):
        r=cur[(u,i)]; assert r['role']==x[0],(u,i); add(r['role'],f(x[1]),f'{W}/{r["file"]}'); n+=1
ws=json.load(open(W+'/audio/gen-log-ws.json',encoding='utf8'))
for r in ws: add(r['role'],r['display'],f'{W}/{r["file"]}'); n+=1
for r in json.load(open(W+'/audio/gen-log-phrases.json',encoding='utf8')): add(r['role'],r['display'],f'{W}/{r["file"]}'); n+=1
tot=sum(os.path.getsize(x) for x in glob.glob(REPO+'/voices/ru/*.mp3'))
idx['mb']=int(tot/1e6)+1; json.dump(idx,open(REPO+'/voices/ru/index.json','w'),ensure_ascii=False)
print('audio clips added',n,'| total MB',idx['mb'],'| roles',{r:len(v) for r,v in clips.items()})
