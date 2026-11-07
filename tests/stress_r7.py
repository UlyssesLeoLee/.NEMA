import random,sys
from pathlib import Path
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from codec import native,nemat
r=random.Random(28911)
S=['Word','A','API','HTTP','ItIs','-','\u65e5\u672c\u8a9e','\u6c49\u5b57','^','$9','\\\\','\\ ','\\t','\\=Hello','Token^2','Why:','abc123','\\\\^','A>B','0','42','']
def cell():return r.choice(S)
for i in range(1800):
 mode=r.choice(['5w1h','table','graph']);rows=[f'\t'+('>G' if mode=='graph' else 'T')+str(i)+' 1']
 if mode=='5w1h':
  for j in range(r.randint(1,6)):
   a=[cell() for _ in range(r.randint(1,6))]
   rows.append(' '.join(a))
 elif mode=='table':
  n=r.randint(1,5);rows.append('\t'+' '.join('C'+str(x) for x in range(n)))
  for j in range(r.randint(1,6)):
   rows.append(' '.join(['R'+str(j)]+[cell() for _ in range(n-1)]))
   if r.random()<.45 and n>1:rows.append(' '*(r.randint(1,n-1)) + cell())
 else:
  rows.extend([' A LoginAPI Authentication',' B TokenStore SessionStorage'])
  rows.append('A>X>B Reads '+cell())
  if r.random()<.45:rows.append('  '+cell())
 src='\n'.join(rows)+'\n\n\n'
 try:native.parse(src)
 except ValueError:continue
 for opts in ([],['Word'], ['API','HTTP'],['^'],['\\\\']):
  try:
   en=nemat.encode(src,opts,True);back=nemat.decode(en)
   if src!=back:raise AssertionError(('mismatch',src,back,en))
  except Exception as e:
   print('FAIL CASE',i,mode,repr(src),opts,repr(e));raise
print('property codec ok')
