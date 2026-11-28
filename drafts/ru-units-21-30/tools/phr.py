import json,os,sys,hashlib,requests,subprocess,datetime
sys.path.insert(0,'/home/claude/u2130')
import gen
P=[(7,"Хо́чешь я́блоко?","Do you want an apple?"),(9,"Мой люби́мый цвет — зелёный.","My favorite color is green."),(10,"Я люблю́ рисова́ть.","I like drawing."),
(12,"Я живу́ здесь, в Аме́рике.","I live here, in America."),(12,"Я говорю́ по-ру́сски.","I speak Russian."),(13,"Что де́лает па́па?","What is Dad doing?"),
(15,"Тебе не хо́лодно?","Aren't you cold?"),(17,"Что боли́т?","What hurts?"),(18,"Я здесь!","I'm here!"),
(21,"Не волну́йся!","Don't worry!"),(21,"Я не уме́ю петь.","I can't sing."),(22,"У меня вопро́с.","I have a question."),(29,"Извини́те!","Excuse me! / Sorry! (polite)")]
json.dump([dict(unit=u,ru=r,en=e) for u,r,e in P],open('audio/phrases.json','w'),ensure_ascii=False,indent=1)
vid,stab=gen.ROLE['teacher']
out=[];os.makedirs('audio/phr',exist_ok=True)
def one(role,text,tag):
    seed=int(hashlib.sha1(f'{role}|{text}'.encode()).hexdigest()[:8],16)
    body={'text':text,'model_id':'eleven_v4_turbo','language_code':'ru','voice_settings':{'stability':stab},'seed':seed}
    r=requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128',headers={'xi-api-key':gen.EL,'Content-Type':'application/json'},json=body,timeout=120)
    if r.status_code!=200: print('ERR',r.status_code,r.text[:120].replace(gen.EL,'***'));return None
    raw=f'audio/phr/raw_{tag}.mp3'; open(raw,'wb').write(r.content); fin=f'audio/phr/{tag}.mp3'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',raw,'-af','loudnorm=I=-19:TP=-2:LRA=11','-ar','44100','-ac','1','-b:a','128k',fin],check=True)
    return dict(role=role,text=text,voice_id=vid,model='eleven_v4_turbo',stability=stab,seed=seed,request_id=r.headers.get('request-id'),file=fin,date=datetime.date.today().isoformat(),trial='no-stress-marks',check=gen.check(fin))
chars=0
for i,(u,ru,en) in enumerate(P):
    t=gen.audio_text(ru)
    for role,txt in (('teacher',t),('teacher_slow','[extremely slowly] '+t)):
        r=one(role,txt,f'{i:02d}_{role}'); 
        if r: r['unit']=u;r['i']=i;r['display']=ru;r['en']=en;out.append(r);chars+=len(txt)
    n=[x for x in out if x['i']==i]
    if len(n)==2: print(i,ru,'normal',n[0]['check']['dur'],'slow',n[1]['check']['dur'],'ratio',round(n[1]['check']['dur']/n[0]['check']['dur'],2),'tail',n[0]['check']['tail_fail'],n[1]['check']['tail_fail'],flush=True)
json.dump(out,open('audio/gen-log-phrases.json','w'),ensure_ascii=False,indent=1)
print('chars sent',chars,'balance',requests.get('https://api.elevenlabs.io/v1/user/subscription',headers={'xi-api-key':gen.EL}).json()['character_count'])
