"""Generate deterministic NEMA v1.5 SFT and evaluation data (synthetic)."""
import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from codec import parse,render,encode,decode
OUT=ROOT/'training'
SYSTEM=('Follow NEMA v1.5 exactly. Domain headers are TAB+backslash+decimal ID (Table), TAB+?+ID (5W1H), TAB+>+ID (Graph); optional revision defaults to 1. Table is default: only the first body line prefixed '
        'by a backslash followed by one space is an explicit table header; otherwise '
        'the first body row is data with generated column1...columnN. '
        '5W1H uses ? and What Why How Who When Where; Graph uses > and A>X>B. '
        'ASCII spaces separate columns; leading N spaces continue column N-1; '
        'TAB is reserved for domain headers and dictionary controls. '
        'All NEMA output ends with two empty physical lines.')

atoms=['APIKey','HTTPStatus','AuthService','TokenStore','PermissionGrant']

def new_header(src, base):
    import re
    found=[]
    def change(m):
        k=(m.group(1),m.group(2))
        if k not in found: found.append(k)
        sign={'':'\\','?':'?','>':'>'}[m.group(1)]
        rev=m.group(3)
        return '\t'+sign+str(base+found.index(k))+((' '+rev) if rev!='1' else '')
    return re.sub(r'^\t([?>]?)([A-Za-z][A-Za-z0-9_.-]*) ([1-9][0-9]*)$',change,src,flags=re.M)

def example(i):
    kind=i%6
    version=1+i%3
    if kind==0:
        name=f'T{i:04d}'
        src=f'\t{name} {version}\nAgent{i:03d} Ready CheckSession\nCodex Ready RenewToken\n\n\n'
        task=f'Create a NEMA default Table with no explicit header and records Agent{i:03d} Ready CheckSession, Codex Ready RenewToken. Domain {name}, revision {version}.'
    elif kind==1:
        name=f'T{i:04d}'
        src=f'\t{name} {version}\n\\ Agent Status Note\nClaude Ready CheckSession\n   AccessGranted\nCodex Failed InvalidToken\n\n\n'
        task=f'Write domain {name} rev {version} as an explicitly headed NEMA table: columns Agent Status Note, Claude Ready CheckSession + AccessGranted vertical continuation in Note, Codex Failed InvalidToken.'
    elif kind==2:
        name=f'W{i:04d}'
        text={0:'ValidateAuthGateway PreventUnauthorizedUse Rust Claude Today AuthService .',1:'请检查接口是否安全 防止越权 使用测试套件 .',2:'APIの動作を確認する 不正アクセスを防ぐ テストを実行 .' }[i%3]
        src=f'\t?{name} {version}\n{text}\n\n\n'
        task=f'Generate a What-first NEMA 5W1H domain ?{name} revision {version} for the positional fields: {text}'
    elif kind==3:
        name=f'G{i:04d}'
        a='A'+str(i);b='B'+str(i);x='E'+str(i)
        op='>' if i%2 else '<'
        src=f'\t>{name} {version}\n{a} LoginAPI\n{b} TokenStore\n{a}{op}{x}{op}{b} Reads CheckSession\n   RetryOnce\n\n\n'
        task=f'Generate NEMA Graph >{name} rev {version}: nodes {a}=LoginAPI, {b}=TokenStore, edge {x} in expression {a}{op}{x}{op}{b}, Reads / CheckSession, add X2 continuation RetryOnce.'
    elif kind==4:
        name=f'D{i:04d}';atom=atoms[i%len(atoms)]
        src=f'\t$1\n{atom}\n\t?{name} {version}\nValidate^0BeforeAccess PreventLeak Rust .\n\n\n'
        task=f'Write an explicit NEMA dictionary with one opaque atom {atom} and one 5W1H domain ?{name} revision {version}; What=Validate^0BeforeAccess, Why=PreventLeak, How=Rust, remaining fields explicit empty.'
    else:
        name=f'J{i:04d}'
        src=f'\t{name} {version}\n\\ Name State Note\nAgent{i} Ready HTTPItIs\n   CheckStatus\n\n\n'
        task=f'Generate a headed NEMA table domain {name} rev {version}: Name State Note header, Agent{i} Ready HTTPItIs, then continue Note with CheckStatus.'
    src=new_header(src,i+1)
    task=task.replace(name,str(1))
    parse(src)
    return {'type':'native_generate','messages':[{'role':'system','content':SYSTEM},{'role':'user','content':task},{'role':'assistant','content':src}]}


def write_jsonl(path,items):
    path.write_text(''.join(json.dumps(item,ensure_ascii=False,separators=(',',':'))+'\n' for item in items),encoding='utf-8')

def main():
    train=[example(i) for i in range(300)]
    holdout=[example(i) for i in range(1000,1080)]
    write_jsonl(OUT/'nema_v1.5_train.jsonl',train)
    write_jsonl(OUT/'nema_v1.5_holdout.jsonl',holdout)
    compressed=[]
    for f in ['bench_en_60.nema','bench_zh_60.nema','bench_ja_60.nema','bench_table_300.nema','bench_graph_120_600.nema','bench_high_entropy_120.nema']:
        source=(ROOT/'examples'/f).read_text(encoding='utf-8')
        choice=encode(source)
        result=choice.text
        if choice.format=='nemat':assert decode(result)==source
        instruction=(f'Encode the following NEMA source with the v1.5 lossless transport codec. '
                     f'If compression does not reduce the total UTF-8 size, retain native NEMA. '
                     f'Provide the exact content only.\nSOURCE:\n{source}')
        compressed.append({'type':'transport_encode','format':choice.format,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':instruction},{'role':'assistant','content':result}]})
    write_jsonl(OUT/'nema_v1.5_transport_examples.jsonl',compressed)
    print('wrote',len(train),'native train;',len(holdout),'holdout;',len(compressed),'codec demonstrations')
if __name__=='__main__':main()
