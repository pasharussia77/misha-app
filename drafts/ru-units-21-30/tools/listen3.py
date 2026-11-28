import json,base64,importlib.util,re
sp=importlib.util.spec_from_file_location('c','/home/claude/u2130/content.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
log=json.load(open('audio/gen-log-new.json'))
names={'misha':'Миша','tima':'Тима','mama':'Мама','papa':'Папа','teacher':'Учитель'}
by={(r['unit'],r['line']):r for r in log}
U=[]
for u in range(21,31):
    L=[x for x in m.U[u]['story'] if x[0]!='q']; lines=[]
    for i,x in enumerate(L,1):
        r=by[(u,i)]
        lines.append(dict(n=i,who=names[x[0]],ru=x[1].replace('`','\u0301'),en=x[2],sent=r['text'],a='data:audio/mpeg;base64,'+base64.b64encode(open(r['file'],'rb').read()).decode()))
    U.append(dict(u=u,t=m.U[u]['title'],st=m.U[u]['storyTitle'],lines=lines))

ph=json.load(open('audio/gen-log-phrases.json'))
b64=lambda f:'data:audio/mpeg;base64,'+base64.b64encode(open(f,'rb').read()).decode()
lines=[]
for k in sorted({r['i'] for r in ph}):
    nm=[r for r in ph if r['i']==k and r['role']=='teacher'][0]; sl=[r for r in ph if r['i']==k and r['role']=='teacher_slow'][0]
    lines.append(dict(n=k+1,who='Учитель',ru=nm['display'],en=nm['en'],sent=nm['text'],a=b64(nm['file']),b=b64(sl['file'])))
U.append(dict(u=99,t='Adopted phrases',st='teacher audio, normal and slow',lines=lines))
tpl=open('listen3.tpl.html',encoding='utf8').read()
html=tpl.replace('__U__',json.dumps(U,ensure_ascii=False).replace('<','\\u003c'))
open('/mnt/user-data/outputs/units-21-30-listening.html','w',encoding='utf8').write(html);print(len(html)//1024,'KB')
