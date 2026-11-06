"""Deterministic synthetic benchmarks and explicit examples for NEMA v1.4.
These are synthetically repetitive, NOT production traffic.
"""
import pathlib,random,string,json
BASE=pathlib.Path(__file__).resolve().parents[1]
EX=BASE/'examples';EX.mkdir(exist_ok=True)

def write(name,rows):
    (EX/name).write_text('\n'.join(rows)+'\n\n\n',encoding='utf-8')

write('00_default_table_no_header.nema',[
 '\tT1 1',
 'Claude Ready CheckSession',
 '   HTTPItIs',
 'Codex Failed InvalidToken',
 'Gemini Ready RenewToken',
])
write('01_explicit_table_header.nema',[
 '\tT2 1',
 '\\ Agent Status Note',
 'Claude Ready CheckSession',
 '   AccessGranted.',
 'Codex Failed HTTP/2',
 '   TokenExpired.',
])
write('02_5w1h_what_first.nema',[
 '\t?Task1 1',
 'WriteProjectSpecification EnsureQuality Rust Codex Today IDE1.0 .',
 '\t?Task2 1',
 'HTTPItIs AQuestion NaturalLanguage',
 ' TestAPIKey',
])
write('03_graph_complex.nema',[
 '\t>G1 1',
 'A LoginAPI Authentication',
 'B TokenStore Redis',
 'C AuditService Events',
 'D BackgroundWorker Queue',
 'A>X>B Reads ValidateSession',
 '   WhenTokenIsValid',
 'A>Y>B Writes RefreshTTL',
 'B<Z<C Notifies TokenExpired',
 'C>V>D Dispatches AuditJob',
 'A=U=C Shares SecurityPolicy',
 'A>P>A Retry AtMost3Times',
 'D>W>A Reports CompletionStatus'
])
write('04_inline_shared_dictionary.nema',[
 '\t$3', 'APIKey','HTTPStatus','PasswordHash',
 '\t?M1 1', 'Validate^0BeforeAccess PreventLeak Rust .',
 '\tT1 1', '\\ Agent Action Target',
 'Claude Validate ^0',
 'Codex Check ^1',
 '\t>G1 1', 'A LoginAPI','B TokenStore','A>X>B Reads Validate^0BeforeAccess',
])
write('05_mixed_languages.nema',[
 '\t?CN1 1','请检查APIKey是否有效 确保安全',
 '\t?JA1 1','APIKeyを確認してください セキュリティ確認',
 '\t?EN1 1','Validate^0BeforeAccess PreventUnauthorizedUse',
])
# 05 intentionally references a dictionary; put it at start to make fixture fully parseable.
p=EX/'05_mixed_languages.nema'
s=p.read_text(encoding='utf-8');p.write_text('\t$1\nAPIKey\n'+s,encoding='utf-8')
write('06_escaping_and_rle.nema',[
 '\tTescape 1','\\ Symbol Value',
 'Caret \\^',
 'Backslash \\\\',
 'Dot \\.',
 'Repeated AAAAAAAAAAAAAAAA',
 'PasswordRef SecretManagerRef'  # never store raw secrets
])
write('07_table_header_without_records.nema',['\tTempty 1','\\ Name State'])
write('08_table_expanding_columns.nema',['\tTgrow 1','Alpha One','Beta Two Three','  ContinuedSecondColumn'])

for lang in ('en','zh','ja'):
 rows=[]
 for i in range(1,61):
  rows.append(f'\t?Task{i:03d} 1')
  if lang=='en': rows.append('Validate^0BeforeAccess PreventUnauthorizedUse UseAuthGateway Claude Today SecurityService .')
  if lang=='zh': rows.append('验证APIKey有效性 防止越权访问 使用认证网关 Claude 今天 安全服务 .')
  if lang=='ja': rows.append('APIKeyの有効性を検証する 不正アクセスを防止する 認証ゲートウェイを利用 Claude 今日 セキュリティサービス .')
 if lang=='en': rows=['\t$1','APIKey']+rows
 write(f'bench_{lang}_60.nema',rows)

rows=['\tTbig 1','\\ Agent Status Note Module']
for i in range(300):
 rows.append(f'Agent{i:03d} Ready CheckSession AuthGateway')
write('bench_table_300.nema',rows)
rows=['\t>Gbig 1']
for i in range(120): rows.append(f'N{i:03d} ServiceNode{i:03d} Architecture')
for i in range(600):
 a=i%120;b=(i*7+13)%120
 rows.append(f'N{a:03d}>E{i:03d}>N{b:03d} Calls CheckSession')
write('bench_graph_120_600.nema',rows)
rand=random.Random(20261106)
rows=['\tTentropy 1','\\ ID Nonce Payload']
for i in range(120):
 payload=''.join(rand.choice(string.ascii_letters+string.digits) for _ in range(20))
 rows.append(f'R{i:03d} {payload} {payload[::-1]}')
write('bench_high_entropy_120.nema',rows)

# human-render sample projections generated through the runtime, not handwritten.
import sys
sys.path.insert(0,str(BASE))
from codec.core import render
for f in EX.glob('0*.nema'):
 (f.with_suffix('.render.json')).write_text(json.dumps(render(f.read_text(encoding='utf-8')),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('created',len(list(EX.glob('*.nema'))),'latest .nema examples')
