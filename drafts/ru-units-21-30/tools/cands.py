import json,re
D=json.load(open('allunits.json',encoding='utf8'))
def norm(t): return re.sub(r'\s+',' ',re.sub(r'[^\w\s]','',re.sub(r'[\u0301`]','',t).lower())).strip()
bank=[(u,norm(s)) for u,d in D.items() for s in d['sents']+d['words']]
# (unit, plain phrase, english, kind)
C=[(1,"Как тебя зовут?","What's your name?"),(1,"Меня зовут Тима.","My name is Tima."),(1,"Здравствуйте!","Hello! (polite)"),
(3,"Нет, спасибо.","No, thank you."),(3,"Да, хочу.","Yes, I do."),(3,"Вкусно!","Yummy!"),
(6,"Вот твой телефон!","Here's your phone!"),
(7,"Доброе утро!","Good morning!"),(7,"Как дела?","How are you?"),(7,"Пока!","Bye!"),(7,"Спокойной ночи!","Good night!"),(7,"Хочешь яблоко?","Do you want an apple?"),
(8,"Сколько тебе лет?","How old are you?"),(8,"Мне пять лет.","I'm five."),(8,"А тебе?","And you?"),
(9,"Какого цвета моя бабушка?","What color is my grandma?"),(9,"Мой любимый цвет — зелёный.","My favorite color is green."),
(10,"Я люблю рисовать.","I like drawing."),(10,"Я тоже!","Me too!"),(10,"Я очень люблю торт!","I really love cake!"),
(11,"У меня есть ручка.","I have a pen."),(11,"А у тебя есть тетрадь?","Do you have a notebook?"),(11,"Вот тетрадь.","Here's a notebook."),
(12,"Я живу здесь, в Америке.","I live here, in America."),(12,"Я говорю по-русски.","I speak Russian."),(12,"Немного.","A little."),
(13,"Что ты делаешь?","What are you doing?"),(13,"Я сплю.","I'm sleeping."),(13,"Что делает папа?","What is Dad doing?"),
(14,"Какой сегодня день?","What day is it today?"),(14,"Извини!","Sorry!"),
(15,"Какая сегодня погода?","What's the weather like today?"),(15,"Мне жарко.","I'm hot."),(15,"Тебе не холодно?","Aren't you cold?"),
(16,"Надень шапку!","Put on your hat!"),(16,"Где моя шапка?","Where's my hat?"),
(17,"Что болит?","What hurts?"),(17,"У меня болит живот.","My tummy hurts."),(17,"Я устал.","I'm tired."),(17,"Где болит?","Where does it hurt?"),(17,"Извини, мама.","Sorry, Mom."),
(18,"Я здесь!","I'm here!"),(18,"Где ты?","Where are you?"),
(19,"Что на завтрак?","What's for breakfast?"),(19,"Я ем кашу.","I'm eating porridge."),(19,"А я?","What about me?"),(19,"Я тоже хочу кашу.","I want porridge too."),
(20,"Ты умеешь кататься на коньках?","Can you skate?"),(20,"Я умею играть в шахматы.","I can play chess."),
(21,"Не волнуйся!","Don't worry!"),(21,"Спасибо, Миша.","Thank you, Misha."),(21,"Я не умею петь.","I can't sing."),
(22,"У меня вопрос.","I have a question."),(22,"Вот твоя сумка.","Here's your bag."),
(23,"А ты где?","And where are you?"),
(24,"Ты идёшь пешком?","Are you walking?"),(24,"Я тоже иду на стадион!","I'm going to the stadium too!"),
(25,"У тебя есть хобби?","Do you have a hobby?"),
(26,"Где ты был вчера?","Where were you yesterday?"),
(27,"Хочу на море!","I want to go to the sea!"),(27,"Ты едешь?","Are you coming?"),
(29,"Здравствуйте!","Hello! (polite)"),(29,"Извините!","Excuse me / Sorry! (polite)"),(29,"Сейчас перемена!","It's recess now!")]
have=[];miss=[]
for u,ru,en in C:
    n=norm(ru); hit=[x for x,t in bank if n==t or (len(n.split())>=2 and n in t)]
    (have if hit else miss).append((u,ru,en,hit[:2]))
print('ALREADY TAUGHT (drop):');[print(' ',a,b,'<-unit',d) for a,b,c,d in have]
print('MISSING (candidates):',len(miss));[print(' ',a,b,'|',c) for a,b,c,d in miss]
json.dump([dict(unit=a,ru=b,en=c) for a,b,c,d in miss],open('cands.json','w'),ensure_ascii=False)
