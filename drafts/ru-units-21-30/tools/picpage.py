import json,re,base64,importlib.util,sys
sys.path.insert(0,'/home/claude/u2130')
import picdata
sp=importlib.util.spec_from_file_location('c','/home/claude/u2130/content.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
old=json.load(open('oldwords.json',encoding='utf8'))
img={x['en']:re.search(r"img/(\w+)\.webp",x['pic']).group(1) for x in old if 'img/' in x['pic']}
A='\u0301';U=[]
for u,d in m.U.items():
    ws=[]
    for w in d['words']:
        mode,idea,conf,ex=picdata.P[w[0]]
        exl=[dict(label=g,src='data:image/webp;base64,'+base64.b64encode(open(f'/home/claude/misha-app/img/{img[g]}.webp','rb').read()).decode()) for g in ex if g in img]
        ws.append(dict(id=w[0],ru=w[1].replace('`',A),plain=w[1].replace('`',''),en=w[2],emoji=w[4],mode=mode,idea=idea,conf=conf,ex=exl,unit=u))
    U.append(dict(u=u,t=d['title'],words=ws))
open('/mnt/user-data/outputs/pictures-21-30.html','w',encoding='utf8').write(open('pics.tpl.html',encoding='utf8').read().replace('__U__',json.dumps(U,ensure_ascii=False)))
print(len(open('/mnt/user-data/outputs/pictures-21-30.html',encoding='utf8').read())//1024,'KB')
