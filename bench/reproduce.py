"""Offline benchmark: NEMA v1.1 SPACE-X versus TAB-X, vertical variants,
position-only YAML and reversible .nemat. No official provider tokenizers.
Run: python bench/reproduce.py
"""
import sys, json, csv, random, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from codec import native,nemat
import sentencepiece as spm

BASE=ROOT/'bench';DATA=ROOT/'examples';DATA.mkdir(exist_ok=True)
SP={k:spm.SentencePieceProcessor(model_file=str(BASE/f'neutral_{k}.model')) for k in ('bpe','unigram')}

def finish(lines):return '\n'.join(lines)+'\n\n\n'

def split_cols(values,mark=' '):return mark.join(values)

EN=[('BuildLoginFlow','PreventDataLeak','ValidateAPI','Codex','Today','AuthService'),
('ReviewHTTPStatus','ExplainUnexpectedFailure','AuditLogs','Claude','Tomorrow','Gateway'),
('FixTokenCache','AvoidExpiredSessions','AddTests','Argo','Today','Redis'),
('DocumentReleasePlan','ImproveSharedContext','ReviewChanges','Codex','Friday','Repository'),
('AnalyzeGraphEdges','PreventInvalidDirections','VerifyTopology','Claude','Today','IDE'),
('PrepareAgentHandoff','ReduceTokenWaste','ReviewDependencies','Argo','Tomorrow','Project')]
ZH=[('处理登录流程','防止数据泄露','验证访问令牌','智能体甲','今天','认证服务'),
('检查接口响应','说明异常原因','审阅运行日志','智能体乙','明天','网关'),
('修复令牌缓存','避免会话过期','补充测试用例','调度程序','今天','数据库'),
('整理发布计划','改善协作流程','审核代码变更','智能体甲','周五','代码仓库'),
('分析图形关系','防止方向错误','检查节点连接','智能体乙','今天','编辑器'),
('准备任务交接','减少重复内容','确认任务依赖','调度程序','明天','工作区')]
JA=[('ログイン処理を確認する','情報漏洩を防ぐ','認証トークンを検証する','担当エージェント','今日','認証サービス'),
('応答内容を確認する','異常の原因を説明する','実行ログを調べる','監査エージェント','明日','ゲートウェイ'),
('キャッシュを修正する','期限切れを防ぐ','テストを追加する','実行エージェント','今日','データベース'),
('リリース計画を作る','連携を改善する','変更内容を審査する','担当エージェント','金曜日','リポジトリ'),
('接続関係を分析する','方向の誤りを防ぐ','依存関係を検証する','監査エージェント','今日','エディタ'),
('作業引継ぎを準備する','重複情報を減らす','タスク間の関係を調べる','実行エージェント','明日','作業領域')]

def english_chunks(s):
    # Parsed intent is identical for compact and vertical, without coercing proper nouns.
    return native.lexical_words(s)

def cjk_chunks(s):
    if len(s)<=4:return [s]
    pivot=len(s)//2
    return [s[:pivot],s[pivot:]]

def domain_rows(values,vertical,lang):
    if not vertical:return [split_cols(values)]
    blocks=[(english_chunks(v) if lang=='en' else cjk_chunks(v)) for v in values]
    maxlen=max(map(len,blocks));out=[]
    for i in range(maxlen):
        seg=[p[i] if len(p)>i else '' for p in blocks]
        while seg and not seg[-1]:seg.pop()
        out.append(' '.join(seg))
    return out

def make_language(lang,items,vertical=False,delimiter=' '):
    out=[];canonical=[]
    for i in range(60):
        vals=list(items[i%len(items)]); name=f'Task{i+1:03d}'
        out.append(f'\t{name} 1')
        rows=domain_rows(vals,vertical,lang)
        out.extend(rows if delimiter==' ' else [r.replace(' ','\t') for r in rows])
    return finish(out)

def yaml_semantic(file):
    domains=native.view(file)
    result=[]
    for d in domains:
        if d['mode']=='5w1h':row=[d['id'],d['revision']]+[d['fields'][x] for x in native.FIELD_NAMES]
        elif d['mode']=='table':row=[d['id'],d['revision'],d['columns'],list(d['records'])]
        else:row=[d['id'],d['revision'],d['nodes'],d['edges']]
        result.append('- '+json.dumps(row,ensure_ascii=False,separators=(',',':')))
    return '\n'.join(result)+'\n'

def graph():
    lines=['\t>Gnetwork1 1']
    for i in range(40):lines.append(f'N{i:02d} Node{i:02d} 接收并处理任务')
    for j in range(160):
        a=j%40;b=(j*7+3)%40
        if j%4==0: a,b=b,a; expr=f'N{a:02d}<E{j:03d}<N{b:02d}'
        else:expr=f'N{a:02d}>E{j:03d}>N{b:02d}'
        lines.append(f'{expr} Notify 传递任务状态')
        if j%7==0:lines.append('  等待下一轮确认')
    return finish(lines)

def table(n=200):
    lines=['\tTb01 1','\tAgent Status Note']
    for i in range(n):
        lines.append(f'Agent{i:03d} '+('Ready' if i%3 else 'Done')+' '+('已完成校验' if i%4 else '等待结果确认'))
        if i%12==0:lines.append('  需要再次复核')
    return finish(lines)

def random_data():
    r=random.Random(20261106);chars='ABCDEFGHabcdefgh0123456789'
    lines=[]
    for i in range(60):
        lines.append(f'\tRand{i:03d} 1')
        lines.append(' '.join(''.join(r.choice(chars) for _ in range(18)) for _ in range(6)))
    return finish(lines)

SCENARIOS={}
for lang,items in [('en',EN),('zh',ZH),('ja',JA)]:
    compact=make_language(lang,items)
    vertical=make_language(lang,items,True)
    # Confirm the exact *semantic view* is unchanged between compact and vertical.
    a=native.view(compact,{'en':'en','zh':'zh','ja':'ja'}[lang]);b=native.view(vertical,lang)
    assert a==b,(lang,next(((x,y) for x,y in zip(a,b) if x!=y),None))
    SCENARIOS[f'{lang}_60_compact']=compact
    SCENARIOS[f'{lang}_60_vertical']=vertical
    SCENARIOS[f'{lang}_60_tab_control']=make_language(lang,items,False,'\t')
SCENARIOS['graph_40n_160e']=graph()
SCENARIOS['table_200rows']=table()
SCENARIOS['entropy_60domains']=random_data()
SCENARIOS['english_one_domain']=finish(['\tT1 1','BuildLoginFlow'])
SCENARIOS['english_http_example']=finish(['\tT1 1','What','HTTPItIs'])

BASELINE={}
for name,raw in SCENARIOS.items():
    (DATA/f'{name}.nema').write_text(raw,encoding='utf-8',newline='\n')
    if '_tab_control' in name:
        # TAB-X comparison substitutes separators only; this intentionally isn't a canonical v1.1 input.
        BASELINE[name]={'source':'tab-x control','text':raw}
        continue
    BASELINE[name]={'source':'canonical','text':yaml_semantic(raw)}
    (DATA/f'{name}.positional.yaml').write_text(BASELINE[name]['text'],encoding='utf-8',newline='\n')

results=[]
for name,src in SCENARIOS.items():
    if '_tab_control' in name:continue
    lang=name[:2] if name[:2] in ('en','zh','ja') else None
    case={'scenario':name,'domains':len(native.parse(src)),'bytes':{'nema':len(src.encode()),'yaml':len(BASELINE[name]['text'].encode())},'tokenizers':{},'mode':{}}
    tab=SCENARIOS.get(f'{lang}_60_tab_control') if name.endswith('compact') else None
    for model_name,model in SP.items():
        scorer=lambda s,m=model:len(m.encode(s))
        before=scorer(src);yaml=scorer(BASELINE[name]['text'])
        opt=nemat.optimize(src,scorer)
        if opt.mode!='native':assert nemat.decode(opt.text)==src
        case['tokenizers'][model_name]={'native':before,'yaml':yaml,'optimized':opt.score,'mode':opt.mode,
             'vs_yaml_pct':round(100*(yaml-before)/yaml,2),
             'wire_vs_yaml_pct':round(100*(yaml-opt.score)/yaml,2),
             'wire_vs_native_pct':round(100*(before-opt.score)/before,2)}
        if tab is not None:
            case['tokenizers'][model_name]['tab_x']=scorer(tab)
            case['tokenizers'][model_name]['space_vs_tab_pct']=round(100*(scorer(tab)-before)/scorer(tab),2)
        if model_name=='bpe':
            (DATA/f'{name}.nemat').write_text(opt.text,encoding='utf-8',newline='\n')
    results.append(case)

(BASE/'results.json').write_text(json.dumps({'model_names':list(SP),'method':'byte-preserving SentencePiece; fixed local reference models','scenarios':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (BASE/'results.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f);w.writerow(['scenario','nema_bytes','yaml_bytes','bpe_nema','bpe_yaml','bpe_nemat','bpe_space_vs_tab_pct','bpe_vs_yaml_pct','bpe_nemat_vs_yaml_pct','unigram_nema','unigram_yaml','unigram_nemat','unigram_vs_yaml_pct'])
    for c in results:
        b=c['tokenizers']['bpe'];u=c['tokenizers']['unigram']
        w.writerow([c['scenario'],c['bytes']['nema'],c['bytes']['yaml'],b['native'],b['yaml'],b['optimized'],b.get('space_vs_tab_pct',''),b['vs_yaml_pct'],b['wire_vs_yaml_pct'],u['native'],u['yaml'],u['optimized'],u['vs_yaml_pct']])
print(json.dumps([{'scenario':r['scenario'],'bpe':r['tokenizers']['bpe'],'unigram':r['tokenizers']['unigram']} for r in results],ensure_ascii=False,indent=2))
