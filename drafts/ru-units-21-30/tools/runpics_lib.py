import re,os,sys,json,shutil
sys.path.insert(0,'.'); sys.path.insert(0,'/home/claude/u2130')
from g2 import gen
from scenes import D
from concurrent.futures import ThreadPoolExecutor
BASE=("Flat vector children's sticker illustration, solid colours, clean dark-brown outlines, soft simple shading, in exactly the same style as the style reference image. "
      "{TXT}Plain white background, centred, nothing cut off, subject fills most of the frame. ")
NOTXT="No text, no letters, no numbers, no words. "; NUM="Numbers and simple math symbols are allowed, but no words or letters. "
DESC={'apple':'the STYLE reference (colours, outlines, shading)','misha':"Misha, the chipmunk: keep him exactly the same (face, round black glasses, brown and cream fur, striped tail) with bright red cartoon gloves on both paws",
 'tima':"Tima, the boy hedgehog: keep him exactly the same",'mom':"Mom: keep her exactly the same",'grandma':"Grandma: keep her exactly the same",
 'you':"the gesture of pointing straight at the viewer, to copy","phone":"the exact smartphone to reuse","bag":"the exact handbag to reuse","horse":"the exact horse to reuse",
 'school':"the exact school building to reuse",'toread':"the STYLE reference (colours, outlines, shading)",'zima':"the exact tree and composition to keep"}
def prompt(i,scene,refs):
    scene=re.sub(r'(in|from) the (first|second|third) reference image','in the matching reference image',scene)
    desc=' '.join(f'Reference image {k+1} is {DESC[r]}.' for k,r in enumerate(refs))
    txt=NUM if i in ('matyematika','vchyera') else NOTXT
    return BASE.replace('{TXT}',txt)+desc+' '+scene
