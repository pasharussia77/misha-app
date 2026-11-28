from playwright.sync_api import sync_playwright
import json,sys
UN=[int(x) for x in sys.argv[1:]] or list(range(1,31))
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':800}); pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append('PAGEERR '+str(e)[:160]))
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(2000)
    pg.evaluate("S.unlockAll=true; localStorage.setItem('x','1')")
    # voice coverage
    cov=pg.evaluate("""async()=>{await vpLoad('ru'); const miss=[]; 
      for(const u of UNIT_IDS.filter(x=>x>=21)){const U=UNITS[u];
        for(const w of U.words){ if(!vpFind(w.ru,false,'teacher')) miss.push(['word',u,w.ru]); if(!vpFind(w.ru,true,'teacher')) miss.push(['word-slow',u,w.ru]); }
        for(const s of U.sentences){ if(!vpFind(s.ru,false,'teacher')) miss.push(['sent',u,s.ru]); if(!vpFind(s.ru,true,'teacher')) miss.push(['sent-slow',u,s.ru]); }
        for(const st of U.story){ if(st.q) continue; const id=vpFind(st.ru,false,st.who); const idt=VP.ru.maps[st.who]&&VP.ru.maps[st.who].get(VKEY(st.ru)); if(!idt) miss.push(['story-role',u,st.who,st.ru]); }
      }
      for(const u of [7,9,10,12,13,15,17,18]){ for(const s of UNITS[u].sentences.filter(x=>x.src==='C'&&x.set===1)){ if(!vpFind(s.ru,false,'teacher')) miss.push(['adopt',u,s.ru]); if(!vpFind(s.ru,true,'teacher')) miss.push(['adopt-slow',u,s.ru]); } }
      return miss}""")
    print('missing audio:',len(cov),cov[:8])
    # picture files
    imgs=pg.evaluate("""async()=>{const bad=[];for(const u of UNIT_IDS.filter(x=>x>=21)){const U=UNITS[u]; for(const w of U.words){const m=/src='([^']+)'/.exec(w.pic||''); if(!m) continue; const r=await fetch(m[1]); if(!r.ok) bad.push(m[1]);} const m=/src='([^']+)'/.exec(U.icon); const r=await fetch(m[1]); if(!r.ok) bad.push(m[1]);} return bad}""")
    print('missing pictures:',imgs)
    tot=0; broken=[]
    for u in UN:
        for level,lessons in enumerate([3,3,2,1,1]):
            for n in range(lessons):
                try:
                    cnt=pg.evaluate("""([u,level,n])=>{setUnit(u); const q=buildLesson(level,n); runQueue(q,{level,n,unit:u}); return q.length}""",[u,level,n])
                    for k in range(cnt+1):
                        pg.evaluate("()=>{try{next()}catch(e){window.__e=String(e)}}")
                        bi=pg.evaluate("()=>[...document.querySelectorAll('img')].filter(i=>i.complete&&i.naturalWidth===0&&!/fonts/.test(i.src)).map(i=>i.src.slice(-30))")
                        if bi: broken+=bi
                    tot+=1
                except Exception as e: errs.append(f'u{u} L{level}.{n}: {str(e)[:120]}')
            pg.evaluate("()=>{try{home()}catch(e){}}")
    print('lessons built/run:',tot,'| broken images:',sorted(set(broken))[:5],'| errors:',len(errs)); [print(' ',e) for e in errs[:8]]
    b.close()
