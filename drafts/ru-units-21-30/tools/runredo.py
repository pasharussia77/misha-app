import os,sys,shutil; sys.path.insert(0,'.'); sys.path.insert(0,'/home/claude/u2130')
from g2 import gen
import runpics_lib as R
from scenes2 import S
from concurrent.futures import ThreadPoolExecutor
R.DESC.update({'muzyey':'the exact museum building to reuse'})
NB=" Flat sticker drawing, NOT inside a book or a frame."
def rp(r): return f'raw/{r}.png' if r=='muzyey' else f'refs/{r}.png'
def job(i):
    scene,refs=S[i]; refs=refs+['apple']
    if os.path.exists(f'raw/{i}.png'): os.replace(f'raw/{i}.png',f'raw/old3_{i}.png')
    txt=R.NUM if i=='myesyats' else R.NOTXT
    desc=' '.join(f'Reference image {k+1} is {R.DESC[r]}.' for k,r in enumerate(refs))
    p=R.BASE.replace('{TXT}',txt)+desc+' '+scene+NB
    return gen(i,p,[rp(r) for r in refs]) or 0
import sys
only=sys.argv[1:] or list(S)
with ThreadPoolExecutor(3) as ex: c=list(ex.map(job,only))
print('DONE',len(S),'total $',round(sum(c),3),flush=True)
