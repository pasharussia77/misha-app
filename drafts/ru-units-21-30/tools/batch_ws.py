import json,os,sys,hashlib,time,requests,subprocess,datetime,threading,importlib.util,re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,'/home/claude/u2130')
import gen
EL=gen.EL; LIMIT=39000; MARGIN=40
sp=importlib.util.spec_from_file_location('c','/home/claude/u2130/content.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
vid,stab=gen.ROLE['teacher']; TAG='[extremely slowly] '
def txt(t):
    t=t.replace('`','').replace('\u0301','').strip()
    return t if t[-1] in '.?!' else t+'.'
items=[]
for u,d in sorted(m.U.items()):
    for w in d['words']: items.append(dict(unit=u,kind='word',key=w[0],display=w[1].replace('`','\u0301'),text=txt(w[1])))
    for i,s in enumerate(d['sentences'],1): items.append(dict(unit=u,kind='sent',key=f'{u}_{i}',display=s[0].replace('`','\u0301'),text=txt(s[0])))
logf='audio/gen-log-ws.json'; log=json.load(open(logf)) if os.path.exists(logf) else []
done={(r['role'],r['kind'],r['key']) for r in log}; lock=threading.Lock()
used=requests.get('https://api.elevenlabs.io/v1/user/subscription',headers={'xi-api-key':EL}).json()['character_count']
prior=sum(len(r['sent_text']) for r in log)
state={'chars':0,'live':used,'base':27909+0.2*prior}
print('start used',used,'items',len(items),flush=True)
def one(it,role):
    k=(role,it['kind'],it['key'])
    if k in done: return
    text=it['text'] if role=='teacher' else TAG+it['text']
    with lock:
        projected=max(state['live'],state['base']+0.2*state['chars'])+0.2*len(text)
        if projected>LIMIT-MARGIN: return
        state['chars']+=len(text)
    seed=int(hashlib.sha1(f'{role}|{text}'.encode()).hexdigest()[:8],16)
    body={'text':text,'model_id':'eleven_v4_turbo','language_code':'ru','voice_settings':{'stability':stab},'seed':seed}
    for a in range(4):
        r=requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128',headers={'xi-api-key':EL,'Content-Type':'application/json'},json=body,timeout=120)
        if r.status_code==200: break
        time.sleep(3+a*4)
    else:
        print('ERR',r.status_code,r.text[:100].replace(EL,'***'),flush=True); return
    tag=hashlib.sha1(f'{role}|{it["display"]}'.encode()).hexdigest()[:12]
    raw=f'audio/ws/raw_{tag}.mp3'; fin=f'audio/ws/{tag}.mp3'; open(raw,'wb').write(r.content)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',raw,'-af','loudnorm=I=-19:TP=-2:LRA=11','-ar','44100','-ac','1','-b:a','128k',fin],check=True)
    rec=dict(it,role=role,sent_text=text,voice_id=vid,model='eleven_v4_turbo',stability=stab,seed=seed,request_id=r.headers.get('request-id'),file=fin,date=datetime.date.today().isoformat(),trial='no-stress-marks',check=gen.check(fin))
    with lock:
        log.append(rec); json.dump(log,open(logf,'w'),ensure_ascii=False)
    os.remove(raw)
def run(role,subset):
    with ThreadPoolExecutor(3) as ex: list(ex.map(lambda it:one(it,role),subset))
run('teacher',items); print('NORMAL DONE',len([r for r in log if r['role']=='teacher']),'chars so far',state['chars'],flush=True)
words=[i for i in items if i['kind']=='word']; sents=[i for i in items if i['kind']=='sent']
run('teacher_slow',words); run('teacher_slow',sents)
print('ALL DONE clips',len(log),'chars',state['chars'],'slow clips',len([r for r in log if r['role']=='teacher_slow']),flush=True)
