import json,re
A='\u0301'
D=json.load(open('allunits.json',encoding='utf8'))
def plain(t): return re.sub(r'[\u0301`]','',t)
def marked(unit,phrase):
    lines=[x['ru'] for x in D[str(unit)]['story']]+[x['ru'] for x in D[str(unit)]['chat']]
    for ln in lines:
        p=plain(ln).lower(); i=p.find(phrase.lower().rstrip('.!?'))
        if i<0: continue
        # map plain index -> marked index
        pi=0;mi=0;start=end=None
        tgt_s=i;tgt_e=i+len(phrase.rstrip('.!?'))
        out='';k=0
        res=[];pos=0
        for ch in ln:
            if ch in (A,'`'):
                if tgt_s<=pos<=tgt_e and pos>tgt_s: res.append(A)
                continue
            if tgt_s<=pos<tgt_e: res.append(ch)
            pos+=1
        s=''.join(res)
        tail=phrase[len(phrase.rstrip('.!?')):]
        return (s[:1].upper()+s[1:])+tail
    return phrase
C=[(21,"Не волнуйся!","Don't worry!","Tima is worried, so Mom says it. Everyday phrase for a friend.","Sentence in unit 21"),
(29,"Извините!","Excuse me! / Sorry! (polite, to a teacher or an adult)","Tima says it to the teacher. We only taught the informal «Извини!».","Sentence in unit 29"),
(22,"У меня вопрос.","I have a question.","Useful in class and in life.","Sentence in unit 22"),
(17,"Что болит?","What hurts?","Mom asks it in the sick unit; only «Где болит?» is taught.","Sentence in unit 17"),
(15,"Тебе не холодно?","Aren't you cold?","A caring question, comes with «Мне холодно».","Sentence in unit 15"),
(7,"Хочешь яблоко?","Do you want an apple?","The way to offer something. Pattern «Хочешь …?»","Sentence in unit 7"),
(9,"Какого цвета моя бабушка?","What color is my grandma?","The way to ask a color. Pattern «Какого цвета …?»","Sentence in unit 9"),
(9,"Мой любимый цвет — зелёный.","My favorite color is green.","Common way to say a favorite color.","Sentence in unit 9"),
(10,"Я люблю рисовать.","I like drawing.","«люблю» + a verb: the key pattern for hobbies.","Sentence in unit 10"),
(12,"Я живу здесь, в Америке.","I live here, in America.","Personal phrase every learner needs.","Sentence in unit 12"),
(12,"Я говорю по-русски.","I speak Russian.","Personal phrase every learner needs.","Sentence in unit 12"),
(13,"Что делает папа?","What is Dad doing?","Third-person question; only «Что ты делаешь?» is taught.","Sentence in unit 13"),
(18,"Я здесь!","I'm here!","Said when someone is looking for you.","Sentence in unit 18"),
(21,"Я не умею петь.","I can't sing.","Pattern «Я не умею …» (I can't).","Sentence in unit 21"),
(27,"Хочу на море!","I want to go to the sea!","Pattern «Хочу на/в …» (I want to go to).","Sentence in unit 27")]
items=[dict(i=i,unit=u,ru=marked(u,ru),en=en,why=why,form=form) for i,(u,ru,en,why,form) in enumerate(C)]
for x in items: print(x['unit'],x['ru'],'|',x['en'])
tpl=open('phrases.tpl.html',encoding='utf8').read()
open('/mnt/user-data/outputs/phrase-bank-review.html','w',encoding='utf8').write(tpl.replace('__ITEMS__',json.dumps(items,ensure_ascii=False)))
