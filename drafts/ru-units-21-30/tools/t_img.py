from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':390,'height':800}); pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(1500)
    pg.evaluate("S.unlockAll=true")
    f="""()=>[...document.querySelectorAll('img')].filter(i=>i.complete&&i.naturalWidth===0&&!/fonts/.test(i.src)).map(i=>({outer:i.outerHTML.slice(0,160),vis:!!(i.offsetWidth||i.offsetHeight),parent:i.parentElement.className+' | '+i.parentElement.outerHTML.slice(0,120)}))"""
    print('HOME:',pg.evaluate(f))
    for u,l,n in [(1,0,0),(21,0,0)]:
        pg.evaluate("([u,l,n])=>{setUnit(u);const q=buildLesson(l,n);runQueue(q,{level:l,n,unit:u})}",[u,l,n])
        for k in range(14):
            pg.evaluate("()=>{try{next()}catch(e){}}"); r=pg.evaluate(f)
            if r: print('unit',u,'step',k,r[:2]); break
    b.close()
