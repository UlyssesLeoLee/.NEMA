from pathlib import Path
from codec import native,nemat
a=Path('examples/complete_v12.nema').read_text(encoding='utf-8')
assert len(native.view(a))==3
b=nemat.optimize(a).text
assert b==a or nemat.decode(b)==a
print('.NEMA v1.2 interpreter roundtrip PASS')

x=Path('examples/graph_x3_extensions.nema').read_text(encoding='utf-8')
v=native.view(x)[0]
assert v['nodes'][0]['extensions']['X3']=='APIKey'
assert v['edges'][0]['extensions']['X3']=='HTTP401 RetryOnTimeout'
assert nemat.decode(nemat.encode(x,['HTTP401']))==x
print('R7 Graph X3 semantic and transport checks PASS')
