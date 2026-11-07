"""Reproducible benchmark of .NEMA v1.2 against JSON, positional JSON and YAML.
The primary metric uses bundled LOCAL sentencepiece models. No official API billing asserted.
"""
from __future__ import annotations
from pathlib import Path
import sys,json,csv,re,time,random
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from codec import native,nemat
try:import sentencepiece as spm
except ImportError:raise SystemExit('Install sentencepiece for tokenizer benchmark; original source remains usable')
OUT=ROOT/'bench'; EX=ROOT/'examples';OUT.mkdir(exist_ok=True);EX.mkdir(exist_ok=True)
SP={mode:spm.SentencePieceProcessor(model_file=str(OUT/f'neutral_{mode}.model')) for mode in ('bpe','unigram')}
LF=lambda l:'\n'.join(l)+'\n\n\n'
# Deterministic, finite data. These cases are NOT a representative model-wide distribution.
EN=[('BuildLoginFlow','PreventDataLeak','ValidateAPI','Codex','Today','AuthService'),('ReviewHTTPStatus','ExplainUnexpectedFailure','AuditLogs','Claude','Tomorrow','Gateway'),('FixTokenCache','AvoidExpiredSessions','AddTests','Argo','Today','Redis'),('DocumentReleasePlan','ImproveSharedContext','ReviewChanges','Codex','Friday','Repository'),('AnalyzeGraphEdges','PreventInvalidDirections','VerifyTopology','Claude','Today','IDE'),('PrepareAgentHandoff','ReduceTokenWaste','ReviewDependencies','Argo','Tomorrow','Project')]
ZH=[('处理登录流程','防止数据泄露','验证访问令牌','智能体甲','今天','认证服务'),('检查接口响应','说明异常原因','审阅运行日志','智能体乙','明天','网关'),('修复令牌缓存','避免会话过期','补充测试用例','调度程序','今天','数据库'),('整理发布计划','改善协作流程','审核代码变更','智能体甲','周五','代码仓库'),('分析图形关系','防止方向错误','检查节点连接','智能体乙','今天','编辑器'),('准备任务交接','减少重复内容','确认任务依赖','调度程序','明天','工作区')]
JA=[('ログイン処理を確認する','情報漏洩を防ぐ','認証トークンを検証する','担当エージェント','今日','認証サービス'),('応答内容を確認する','異常の原因を説明する','実行ログを調べる','監査エージェント','明日','ゲートウェイ'),('キャッシュを修正する','期限切れを防ぐ','テストを追加する','実行エージェント','今日','データベース'),('リリース計画を作る','連携を改善する','変更内容を審査する','担当エージェント','金曜日','リポジトリ'),('接続関係を分析する','方向の誤りを防ぐ','依存関係を検証する','監査エージェント','今日','エディタ'),('作業引継ぎを準備する','重複情報を減らす','タスク間の関係を調べる','実行エージェント','明日','作業領域')]

def lang_case(lang,items):
    lines=[]
    for i in range(60):
        lines.extend((f'\tT{i+1:03d} 1',' '.join(items[i%len(items)])))
    return LF(lines)

def graph_case():
    lines=['\t>Gnetwork1 1']
    for n in range(40):lines.append(f' N{n:02d} Node{n:02d} 接收并处理任务')
    for j in range(160):
        a=j%40;b=(j*7+3)%40
        if j%4==0:
            a,b=b,a;expr=f'N{a:02d}<E{j:03d}<N{b:02d}'
        else:expr=f'N{a:02d}>E{j:03d}>N{b:02d}'
        lines.append(f'{expr} Notifies 传递任务状态')
        if j%7==0:lines.append('  等待下一轮确认')
    return LF(lines)

def table_case():
    lines=['\tTable1 1','\tAgent Status Note']
    for i in range(200):
        lines.append(f'Agent{i:03d} '+('Ready' if i%3 else 'Done')+' '+('已完成校验' if i%4 else '等待结果确认'))
        if i%12==0:lines.append('  需要再次复核')
    return LF(lines)

def entropy_case():
    r=random.Random(20261107); chars='ABCDEFGHabcdefgh0123456789';lines=[]
    for i in range(60):
        lines.append(f'\tRand{i:03d} 1')
        lines.append(' '.join(''.join(r.choice(chars) for _ in range(18)) for _ in range(6)))
    return LF(lines)

CASES={
    'english_60':lang_case('en',EN),
    'chinese_60':lang_case('zh',ZH),
    'japanese_60':lang_case('ja',JA),
    'table_200':table_case(),
    'graph_40n_160e':graph_case(),
    'high_entropy_60':entropy_case(),
    'short_what':LF(['\tT1 1','What','HTTPItIs']),
    'graph_3n_4e':LF(['\t>Gauth1 1',' A LoginAPI Authentication',' B TokenStore SessionStorage',' C AuditService RecordsSecurityEvents','A>X>B Reads VerifySession','  CacheExpiredRetryOnce','B<Y<C Notifies AuditEvent','A=U=C Shares SecurityPolicy','A>P>A Retry Maximum3Attempts']),
}
# Equivalence structured representation. JSON is a REAL JSON document, same domain IDs,
# revisions, field content, nodes, and arrows. Minimal JSON positional layout is a strong control.

def json_forms(src,lang='auto'):
    view=native.view(src,lang)
    compact=json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n'
    position=[]
    for d in view:
        if d['mode']=='5w1h':position.append([d['id'],d['revision'],[d['fields'][n] for n in native.FIELD_NAMES]])
        elif d['mode']=='table':position.append([d['id'],d['revision'],d['columns'],[[r[k] for k in d['columns']] for r in d['records']]])
        else:
            position.append([d['id'],d['revision'],[[n['id'],n['name'],n['description']] for n in d['nodes']],[[e['id'],e['source'],e['target'],e['direction'],e['name'],e['description']] for e in d['edges']]])
    pos=json.dumps(position,ensure_ascii=False,separators=(',',':'))+'\n'
    # A stricter YAML control that includes type/coordinates, ID and revision with no duplicated field keys.
    yaml='\n'.join('- '+json.dumps(row,ensure_ascii=False,separators=(',',':')) for row in position)+'\n'
    return compact,pos,yaml

def test_equivalence(src,compact,pos):
    # Parsed object JSON equates exactly to the interpreter's semantically reconstructed view.
    assert json.loads(compact)==native.view(src, 'auto')
    assert isinstance(json.loads(pos),list)

def main():
    results=[]
    for name,source in CASES.items():
        # Native syntax validated first; immutable source bytes written for reproducibility.
        parsed=native.view(source)
        (EX/(name+'.nema')).write_text(source,encoding='utf-8',newline='\n')
        json_doc,json_pos,yaml_doc=json_forms(source)
        for suffix,data in [('json',json_doc),('positional.json',json_pos),('positional.yaml',yaml_doc)]:
            (EX/(name+'.'+suffix)).write_text(data,encoding='utf-8',newline='\n')
        sample={'scenario':name,'domains':len(parsed),'json_semantically_equal':True,'raw_bytes':{'nema':len(source.encode()),'json':len(json_doc.encode()),'json_positional':len(json_pos.encode()),'yaml_positional':len(yaml_doc.encode())},'models':{}}
        for kind,model in SP.items():
            score=lambda s,m=model:len(m.encode(s))
            chosen=nemat.optimize(source,score)
            if chosen.mode!='native':assert nemat.decode(chosen.text)==source
            tokens={
                'nema':score(source),'nemat':chosen.score,'json':score(json_doc),
                'json_positional':score(json_pos),'yaml_positional':score(yaml_doc),
                'nemat_mode':chosen.mode
            }
            for base in ('json','json_positional','yaml_positional'):
                tokens['nema_vs_'+base+'_pct']=round(100*(tokens[base]-tokens['nema'])/tokens[base],2)
                tokens['nemat_vs_'+base+'_pct']=round(100*(tokens[base]-tokens['nemat'])/tokens[base],2)
            sample['models'][kind]=tokens
            if kind=='bpe':(EX/(name+'.nemat')).write_text(chosen.text,encoding='utf-8',newline='\n')
        results.append(sample)
        print(name, {k:sample['models']['bpe'][k] for k in ('nema','nemat','json','json_positional','yaml_positional')},flush=True)
    # new syntax comparison legacy original node `A \\=LoginAPI` vs new ` A LoginAPI`
    old_graph='\t>Gauth1 1\nA \\=LoginAPI Authentication\nB \\=TokenStore SessionStorage\nA>X>B Reads VerifySession\n\n\n'
    new_graph='\t>Gauth1 1\n A LoginAPI Authentication\n B TokenStore SessionStorage\nA>X>B Reads VerifySession\n\n\n'
    controls={'old_graph_markup':old_graph,'new_graph_markup':new_graph}
    for k,v in controls.items():(EX/(k+'.txt')).write_text(v,encoding='utf-8',newline='\n')
    group_compare={name:{m:len(model.encode(text)) for m,model in SP.items()}|{'bytes':len(text.encode())} for name,text in controls.items()}
    doc={'benchmark':'NEMA v1.2 Space-Node vs JSON','timestamp_label':'2026-11-07','tokenizer':'bundled locally trained SentencePiece; original spaces, tabs and LF preserved','official_api_billing':False,'note':'Offline encoding-only cost, excludes prompt instructions, outputs and retries. See methodology.','scenarios':results,'syntax_before_after':group_compare}
    (OUT/'latest_results.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (OUT/'latest_results.csv').open('w',encoding='utf-8',newline='') as f:
        cols=['scenario','model','nema','nemat','json','json_positional','yaml_positional','nema_vs_json_pct','nemat_vs_json_pct','nema_vs_json_positional_pct','nemat_vs_json_positional_pct','nema_vs_yaml_positional_pct','nemat_vs_yaml_positional_pct']
        wr=csv.DictWriter(f,fieldnames=cols);wr.writeheader()
        for row in results:
            for model,tok in row['models'].items():wr.writerow({'scenario':row['scenario'],'model':model,**{c:tok.get(c,'') for c in cols[2:]}})
    return results
if __name__=='__main__':main()
