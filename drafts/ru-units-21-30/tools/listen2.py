import json,base64,importlib.util
sp=importlib.util.spec_from_file_location('c','/home/claude/u2130/content.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
log=json.load(open('audio/gen-log-new.json'))
names={'misha':'Миша','tima':'Тима','mama':'Мама','papa':'Папа','teacher':'Учитель'}
by={}
for r in log: by[(r['unit'],r['line'])]=r
U=[]
for u in range(21,31):
    L=[x for x in m.U[u]['story'] if x[0]!='q']; lines=[]
    for i,x in enumerate(L,1):
        r=by[(u,i)]
        lines.append(dict(n=i,who=names[x[0]],ru=x[1].replace('`','\u0301'),en=x[2],a='data:audio/mpeg;base64,'+base64.b64encode(open(r['file'],'rb').read()).decode()))
    U.append(dict(u=u,t=m.U[u]['title'],st=m.U[u]['storyTitle'],lines=lines))
html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Mishaling: Russian units 21–30, listening</title>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><style>
:root{--bg:#fbf6ee;--card:#fff;--ink:#2b1d10;--mute:#7a6650;--line:#e6d9c5;--acc:#8a4f1d;--on:#f3e3cc;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1d1610;--card:#2a2018;--ink:#f1e6d6;--mute:#b3a08a;--line:#43362a;--acc:#e0a468;--on:#3b2b1c}}
html{scroll-padding-top:calc(env(safe-area-inset-top,0px) + 120px)}*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;max-width:720px;margin:auto}
header{padding:12px 14px 0}h1{font-size:18px;margin:0}p.s{margin:2px 0 8px;color:var(--mute);font-size:13px}
.bar{position:sticky;top:env(safe-area-inset-top,0px);background:var(--bg);z-index:5;padding:6px 12px 8px;border-bottom:1px solid var(--line)}
nav{display:flex;gap:6px;overflow-x:auto;padding-bottom:6px}nav button{flex:0 0 auto;padding:6px 11px;font-size:15px}
button{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:12px;padding:9px 13px;font:inherit}
button.p,nav button[aria-pressed=true]{background:var(--acc);color:var(--bg);border-color:var(--acc)}
.ctl{display:flex;gap:6px;flex-wrap:wrap}
main{padding:10px 14px 60px}h2{font-size:17px;margin:4px 0 8px}
.l{display:flex;gap:10px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px;margin:8px 0}.l.on{background:var(--on);outline:2px solid var(--acc)}
.l .n{color:var(--mute);width:24px;flex:0 0 24px}.l b{font-size:18px}.l small{display:block;color:var(--mute)}.l .w{font-size:12px;color:var(--mute)}
.l button{margin-left:auto;align-self:center;flex:0 0 auto}
</style></head><body><header><h1>Russian units 21–30: listening</h1><p class="s">Trial: sent with no stress marks. Tell me the unit and line number of anything that sounds wrong (for example “unit 24, line 3”).</p></header>
<div class="bar"><nav id="nav"></nav><div class="ctl"><button class="p" id="pu">Play unit</button><button id="all">Play all</button><button id="rs">Restart unit</button><button id="st">Stop</button></div></div>
<main id="main"></main>
<script>
const U=__U__;let cu=0,ci=-1,mode='',a=new Audio();
const nav=document.getElementById('nav'),main=document.getElementById('main');
U.forEach((x,i)=>{const b=document.createElement('button');b.textContent=x.u;b.dataset.i=i;nav.appendChild(b)});
function render(){[...nav.children].forEach((b,i)=>b.setAttribute('aria-pressed',i==cu));const x=U[cu];
main.innerHTML=`<h2>Unit ${x.u}: ${x.t}. ${x.st}</h2>`+x.lines.map((l,i)=>`<div class="l" id="l${i}"><span class="n">${l.n}</span><div><span class="w">${l.who}</span><br><b>${l.ru}</b><small>${l.en}</small></div><button data-i="${i}">Play</button></div>`).join('')}
function mark(){document.querySelectorAll('.l').forEach((e,i)=>e.classList.toggle('on',i==ci))}
function play(u,i){cu=u;if(document.getElementById('l0')==null||main.dataset.u!=u){render();main.dataset.u=u}ci=i;mark();a.pause();a.src=U[u].lines[i].a;a.play();const e=document.getElementById('l'+i);if(e)e.scrollIntoView({block:'center',behavior:'smooth'})}
nav.onclick=e=>{const b=e.target.closest('button');if(!b)return;mode='';a.pause();cu=+b.dataset.i;ci=-1;render();main.dataset.u=cu;window.scrollTo(0,0)};
main.onclick=e=>{const b=e.target.closest('button[data-i]');if(b){mode='';play(cu,+b.dataset.i)}};
document.getElementById('pu').onclick=()=>{mode='unit';play(cu,Math.max(ci,0))};
document.getElementById('rs').onclick=()=>{mode='unit';play(cu,0)};
document.getElementById('all').onclick=()=>{mode='all';play(cu,0)};
document.getElementById('st').onclick=()=>{mode='';a.pause()};
a.onended=()=>{if(!mode)return;const n=U[cu].lines.length;if(ci<n-1)setTimeout(()=>play(cu,ci+1),450);else if(mode=='all'&&cu<U.length-1)setTimeout(()=>play(cu+1,0),900);else mode=''};
render();main.dataset.u=0;
</script></body></html>'''
html=html.replace('__U__',json.dumps(U,ensure_ascii=False))
open('/mnt/user-data/outputs/units-21-30-listening.html','w',encoding='utf8').write(html);print(len(html)//1024,'KB')
