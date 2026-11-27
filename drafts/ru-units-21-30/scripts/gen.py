import importlib.util,json,re,hashlib,subprocess,os,sys,datetime,requests,numpy as np
EL=os.environ['EL']
sp=importlib.util.spec_from_file_location('c','/home/claude/u2130/content.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
ROLE={'misha':('rSfuQoQ3FY8SVKeraMAp',0.35),'tima':('drOVtcvHhJKNEXv5h1l5',0.45),'mama':('PZhi1QpQl0Z9H9WfRfYS',0.5),'papa':('0BcDz9UPwL3MpsnTeUlO',0.5),'teacher':('FZGeNF7bE3syeQOynDKC',0.55)}
def plain(t): return t.replace('`','').strip()
def audio_text(t):
    t=plain(t)
    if t[-1] not in '.?!': t+='.'
    return t
def lines(u): return [(x[0],x[1],x[2]) for x in m.U[u]['story'] if x[0]!='q']
def gen(u,i,prev=None,seed_add=0):
    L=lines(u); role,ru,_=L[i-1]
    text=audio_text(ru); vid,stab=ROLE[role]
    if prev is None and i>1: prev=audio_text(L[i-2][1])
    seed=int(hashlib.sha1(f'{role}|{text}'.encode()).hexdigest()[:8],16)+seed_add
    body={'text':text,'model_id':'eleven_v4_turbo','language_code':'ru','voice_settings':{'stability':stab},'seed':seed}
    if prev: body['previous_text']=prev
    r=requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128',headers={'xi-api-key':EL,'Content-Type':'application/json'},json=body,timeout=120)
    if r.status_code!=200: print('ERR',r.status_code,r.text[:200].replace(EL,'***'));return None
    rid=r.headers.get('request-id'); raw=f'audio/raw_{u}_{i}.mp3'; open(raw,'wb').write(r.content)
    fin=f'audio/u{u}_{i:02d}.mp3'; af=[]
    if role=='tima':
        R=2**(3/12); af.append(f'asetrate=44100*{R},aresample=44100,atempo={1/R}')
    af.append('loudnorm=I=-19:TP=-2:LRA=11')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',raw,'-af',','.join(af),'-ar','44100','-ac','1','-b:a','128k',fin],check=True)
    return dict(unit=u,line=i,role=role,lang='ru',text=text,previous_text=prev,voice_id=vid,model='eleven_v4_turbo',stability=stab,seed=seed,request_id=rid,file=fin,date=datetime.date.today().isoformat(),processing='+3 semitones asetrate' if role=='tima' else '',trial='no-stress-marks')
def check(fin):
    raw=subprocess.run(['ffmpeg','-loglevel','error','-i',fin,'-f','s16le','-ac','1','-ar','16000','-'],capture_output=True).stdout
    x=np.frombuffer(raw,dtype=np.int16).astype(float); n=160
    fr=x[:len(x)//n*n].reshape(-1,n); db=20*np.log10(np.sqrt((fr**2).mean(1))+1e-9); db-=db.max()
    sp=db>-45; idx=np.where(sp)[0]; segs=[];s=idx[0];p=idx[0]
    for k in idx[1:]:
        if (k-p)*0.01>=0.12: segs.append((s,p));s=k
        p=k
    segs.append((s,p)); dur=len(x)/16000; last=segs[-1]; lastlen=(last[1]-last[0]+1)*0.01
    gap=(last[0]-segs[-2][1])*0.01 if len(segs)>1 else 9; tail=dur-(last[1]+1)*0.01
    fail=(lastlen<0.35 and gap>=0.2) or tail>0.25+0.12
    lufs=subprocess.run(['ffmpeg','-nostats','-i',fin,'-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
    I=re.findall(r'I:\s+(-?[\d.]+) LUFS',lufs)[-1]
    return dict(dur=round(dur,2),segments=len(segs),last_seg=round(lastlen,2),gap_before_last=round(gap,2),tail_after=round(tail,2),tail_fail=bool(fail),lufs=I)
if __name__=='__main__':
    out=[]
    for u,i in [(21,3),(27,3),(30,10)]:
        r=gen(u,i)
        if r: r['check']=check(r['file']); out.append(r); print(u,i,r['role'],r['text'],r['check'])
    json.dump(out,open('audio/test-log.json','w'),ensure_ascii=False,indent=1)

def gen_seed(u,i,n,prev=None):
    return gen(u,i,prev=prev,seed_add=n*104729)
