import json,os,sys,hashlib,time,numpy as np,subprocess
sys.path.insert(0,'/home/claude/u2130')
import gen
from scipy.signal import butter,sosfilt
NEUTRAL_PREV='Хорошо.'
done_file='audio/gen-log-new.json'
log=json.load(open(done_file)) if os.path.exists(done_file) else []
have={(r['unit'],r['line']) for r in log}
for r in json.load(open('audio/test-log.json')):
    if (r['unit'],r['line']) not in have: log.append(r); have.add((r['unit'],r['line']))
def td_ratio(raw):
    x=subprocess.run(['ffmpeg','-loglevel','error','-i',raw,'-f','s16le','-ac','1','-ar','44100','-'],capture_output=True).stdout
    x=np.frombuffer(x,dtype=np.int16).astype(float)
    hi=sosfilt(butter(4,2500,'hp',fs=44100,output='sos'),x); lo=sosfilt(butter(4,500,'lp',fs=44100,output='sos'),x)
    n=int(0.005*44100); H=np.array([ (hi[i:i+n]**2).mean() for i in range(0,min(len(hi),44100)-n,n)])
    if H.max()<=0: return None
    # first speech frame: skip leading silence
    act=np.where(np.array([ (x[i:i+n]**2).mean() for i in range(0,min(len(x),44100)-n,n)])>1e3)[0]
    if len(act)==0: return None
    start=act[0]; win=H[start:start+40]; b=start+int(np.argmax(win>0.25*win.max()))
    a=max(0,b-8); lo_pre=(lo[a*n:b*n]**2).mean(); lo_peak=max((lo[i:i+n*8]**2).mean() for i in range(0,len(lo)-n*8,n*8))
    return float(lo_pre/lo_peak)
def save():
    json.dump(log,open(done_file,'w'),ensure_ascii=False,indent=1)
chars=0
for u in range(21,31):
    L=gen.lines(u)
    for i in range(1,len(L)+1):
        if (u,i) in have: continue
        role,ru,_=L[i-1]; first=gen.audio_text(ru)[0] in 'ТтДд'
        prev=NEUTRAL_PREV if i==1 else None
        best=None
        for n in range(4 if (first and role=='misha') else 1):
            r=gen.gen(u,i,prev=prev) if n==0 else gen.gen_seed(u,i,n,prev) if hasattr(gen,'gen_seed') else None
            if r is None: break
            chars+=len(r['text']); r['check']=gen.check(r['file'])
            if first and role=='misha':
                r['td']=td_ratio(f'audio/raw_{u}_{i}.mp3'); r['take']=n
            ok=not r['check']['tail_fail'] and (r.get('td') is None or r['td']<0.1)
            best=r
            if ok: break
        if best: log.append(best); have.add((u,i)); save(); print(u,i,best['role'],best['check']['tail_fail'],best.get('td'),flush=True)
print('DONE chars',chars,flush=True)
