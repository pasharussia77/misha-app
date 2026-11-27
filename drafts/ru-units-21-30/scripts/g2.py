import os,json,base64,requests,time,random
K=os.environ['OAI']; H={'Authorization':'Bearer '+K}
def gen(name,prompt,refs=(),out=None):
    out=out or f'raw/{name}.png'; data={'model':'gpt-image-2','prompt':prompt,'size':'1024x1024','quality':'low'}
    for a in range(6):
        t=time.time()
        try:
            if refs:
                files=[('image[]',(os.path.basename(r),open(r,'rb'),'image/png')) for r in refs]
                r=requests.post('https://api.openai.com/v1/images/edits',headers=H,data={**data,'n':'1'},files=files,timeout=300)
            else:
                r=requests.post('https://api.openai.com/v1/images/generations',headers={**H,'Content-Type':'application/json'},json={**data,'n':1},timeout=300)
        except Exception as e: print(name,'net',str(e)[:80]); time.sleep(5); continue
        j=r.json()
        if r.status_code==429 or r.status_code>=500: time.sleep(10*(a+1)+random.random()*5); continue
        if r.status_code!=200: print(name,'ERROR',r.status_code,str(j)[:200].replace(K,'***')); return None
        open(out,'wb').write(base64.b64decode(j['data'][0]['b64_json']))
        u=j.get('usage',{}); it=u.get('input_tokens_details',{}); cost=it.get('text_tokens',0)*5e-6+it.get('image_tokens',0)*8e-6+u.get('output_tokens',0)*30e-6
        open('cost.log','a').write(json.dumps({'name':name,'cost':cost})+'\n'); print(name,f'{time.time()-t:.0f}s ${cost:.4f}',flush=True); return cost
    return None
