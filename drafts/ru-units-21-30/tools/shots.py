from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':390,'height':800}); pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(1800)
    pg.evaluate("S.unlockAll=true"); pg.evaluate("()=>{try{home()}catch(e){}}"); pg.wait_for_timeout(500)
    pg.evaluate("()=>{const b=document.querySelector('[data-unit=\"21\"][data-level=\"0\"]'); if(b) b.scrollIntoView({block:'center'})}"); pg.wait_for_timeout(600); pg.screenshot(path='shots/1_path.png')
    def lesson(u,l,n,steps,name):
        pg.evaluate("([u,l,n])=>{setUnit(u);const q=buildLesson(l,n);runQueue(q,{level:l,n,unit:u})}",[u,l,n]); pg.wait_for_timeout(400)
        for _ in range(steps): pg.evaluate("()=>{try{next()}catch(e){}}"); pg.wait_for_timeout(120)
        pg.wait_for_timeout(500); pg.screenshot(path=f'shots/{name}.png')
    lesson(21,0,0,0,'2_intro'); lesson(29,3,0,9,'3_story'); lesson(28,0,0,0,'4_word28')
    b.close()
ims=[Image.open(f'shots/{n}.png') for n in ['1_path','2_intro','3_story','4_word28']]
W=sum(i.width for i in ims); s=Image.new('RGB',(W,ims[0].height),'white'); x=0
for i in ims: s.paste(i,(x,0)); x+=i.width
s=s.resize((W//2,ims[0].height//2)); s.save('shots/sheet.png'); print(s.size)
