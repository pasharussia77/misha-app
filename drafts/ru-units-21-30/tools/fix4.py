s=open('content.py',encoding='utf8').read()
def R(a,b):
    global s
    assert a in s,a[:70]; s=s.replace(a,b)
R('("tima","Нет, на авто`бусе.","No, by bus.")','("tima","Нет, на авто`бусе.","No, I\'m taking the bus.")')
R('("mama","Ми`ша, вот краси`вая су`мка!","Misha, here\'s a beautiful bag!")','("mama","Ми`ша, како`й краси`вый велосипе`д!","Misha, what a beautiful bike!")')
open('content.py','w',encoding='utf8').write(s)
