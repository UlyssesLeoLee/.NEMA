(() => {
'use strict';
const L = {
 zh:{skip:'跳到示例',navFeatures:'能力',navExamples:'示例',navBenchmark:'性能',navDocs:'文档',navGet:'开始使用',heroTitle:'让多个智能体，沿着同一根线穿过迷宫。',heroDesc:'5W1H、表格与有向关系图，统一以 ASCII 空格横向分列、换行纵向延展。一个领域就是一个独立协作边界。',heroPrimary:'交互体验 NEMA',heroSecondary:'阅读语法规范',heroMeta1:'领域可独立分派',heroMeta2:'二维语义位置',heroMeta3:'可视化还原',f1:'一段一领域',f1d:'Agent 可独立协作与审查',f2:'二维语义',f2d:'横向列与纵向意群',f3:'三种模式',f3d:'5W1H、表格与 Graph',f4:'IDE1.0 渲染',f4d:'原文紧凑，视图清晰',exTitle:'一种格式，三种信息形态。',exDesc:'直接查看真正的 .nema 原文，并切换到人类可读视图。字段位置、关系方向和纵向意群都由解析器确定。',modeTask:'5W1H / 文本',modeTable:'表格 Table',modeGraph:'Node–Edge 图',copy:'复制源文件',sourceTitle:'NEMA 源文件',renderTitle:'IDE1.0 语义渲染',sourceHint:'领域头前只有一个真实 Tab；字段由 ASCII 空格坐标识别。',demoNote:'这是可运行的规范示例。复杂字符串的大小写和标点在源文件中始终原样保留。',syntaxTitle:'位置承载结构，内容无需装饰。',syntaxDesc:'NEMA 支持自适应 PascalCase，不需要类型括号或图形绘制代码。只有语法边界需要严格规则。',s1:'一个 Tab 识别领域',s1d:'领域头由 ID 与修订号组成，Graph 仅额外添加一个模式字符。',s2:'5W1H 默认启用',s2d:'首行顶格写，六列分别是 What、Why、How、Who、When、Where。',s3:'Tab 表头启动表格',s3d:'第一行以 Tab 开始即纯表格；后续单元可纵向续写。',s4:'Edge 拥有身份与方向',s4d:'A>X>B 定义独立关系 X；说明可以向下继续。',benchTitle:'不猜测 Token，用实验检验。',benchDesc:'等价语义对比原生 NEMA、Tab 分列控制、位置式 YAML 与可逆 .nemat。这里展示本地 SentencePiece BPE 的实测，不代表 GPT / Claude / Gemini 账单。',metricLabel:'英文 60 领域：相对位置式 YAML 的 BPE Token 节省',benchCaveat:'真实目标模型的 tokenizer 尚不可用；最终收益必须结合模型输入输出与纠错测试验证。',benchCard:'本地 BPE · 同一语义负载',benchLegend:'数值保留空格、Tab 和换行；中日语 Tab→空格不保证节省，高熵文本也可能没有压缩收益。',docsTitle:'从源文件到训练语料，一套完整的线索。',docsDesc:'所有示例、解析器、测试、模型训练资料和历史实验资料都与主页一同交付，可离线打开和查阅。',linkSpec:'核心语法规范',linkGuide:'人工书写指南',linkTrain:'AI 专项训练说明',linkBench:'实测 Token 报告',linkSample:'完整样品 .nema',footerText:'阿里阿德涅的线团，为协作留下通往出口的路径。',toTop:'回到顶部 ↑',edgeTitle:'选择一条关系查看说明',rev:'领域版本',node:'节点',relation:'关系',noRows:'没有数据',copied:'已复制',graphNote:'箭头由起点和终点生成，与画面布局无关。'},
 ja:{skip:'サンプルへ移動',navFeatures:'特徴',navExamples:'例',navBenchmark:'性能',navDocs:'資料',navGet:'はじめる',heroTitle:'多数の AI エージェントが、一本の糸で迷宮を進む。',heroDesc:'5W1H、テーブル、有向グラフを 空白の横方向座標と改行の縦方向意味単位で表現。ドメインごとに独立して協働できます。',heroPrimary:'NEMA を体験',heroSecondary:'構文仕様を読む',heroMeta1:'ドメイン単位の分担',heroMeta2:'二次元の意味座標',heroMeta3:'可視化レンダリング',f1:'ドメイン単位',f1d:'エージェントごとに独立した変更',f2:'二次元の意味',f2d:'横方向の列と縦方向の意味単位',f3:'三つのモード',f3d:'5W1H・表・Graph',f4:'IDE1.0 表示',f4d:'機械には短く、人には明瞭',exTitle:'一つの形式、三つのデータ形態。',exDesc:'実際の .nema ソースと、人間向けのレンダリングを比較できます。座標・矢印・意味単位を確定的に解釈します。',modeTask:'5W1H / テキスト',modeTable:'テーブル',modeGraph:'Node–Edge 図',copy:'原文をコピー',sourceTitle:'NEMA 原文',renderTitle:'IDE1.0 意味表示',sourceHint:'ドメインヘッダーの前には実際の Tab が１個。列は ASCII スペースの位置で判定します。',demoNote:'実行可能な仕様サンプルです。大文字小文字と句読点は原文のまま保持します。',syntaxTitle:'座標で構造を表し、内容には装飾を加えない。',syntaxDesc:'型用の括弧、描画専用コマンドは不要です。境界だけを厳密に定義します。',s1:'Tab 一個でドメイン識別',s1d:'ID とリビジョンを持つヘッダー。Graph だけ追加の識別文字を使用。',s2:'既定は 5W1H',s2d:'先頭行は左端から。What / Why / How / Who / When / Where の順です。',s3:'Tab 付き表頭はテーブル',s3d:'先頭行を Tab で始めるとテーブル。セルの文章を縦に続けられます。',s4:'Edge に ID と向きを持たせる',s4d:'A>X>B は関係 ID X。説明は次の行に続けられます。',benchTitle:'Token は推測でなく実測で。',benchDesc:'同一意味の NEMA、Tab 列制御、位置式 YAML、可逆 .nemat を比較。以下はローカル SentencePiece BPE による結果で、GPT 等の請求 Token ではありません。',metricLabel:'英語 60 ドメイン：位置式 YAML に対する BPE Token 削減率',benchCaveat:'対象モデルの公式 tokenizer は未使用です。モデルでの入出力・訂正回数の評価が必要です。',benchCard:'ローカル BPE · 同じ意味データ',benchLegend:'スペース、スペース・Tab・LFを保持したローカル BPE。辞書圧縮が常に有利とは限りません。',docsTitle:'原文から AI 学習資料まで、一つのパッケージ。',docsDesc:'仕様、サンプル、パーサー、テスト、学習素材、過去の実験資料を同梱。オフラインで確認できます。',linkSpec:'構文仕様',linkGuide:'人間向け記述ガイド',linkTrain:'AI 学習ガイド',linkBench:'Token 測定レポート',linkSample:'完全サンプル .nema',footerText:'アリアドネの糸。協働の道筋を残す。',toTop:'ページ上部へ ↑',edgeTitle:'関係を選択して説明を表示',rev:'リビジョン',node:'ノード',relation:'関係',noRows:'データなし',copied:'コピーしました',graphNote:'矢印はノードの座標でなく、有向辺の定義から生成されます。'},
 en:{skip:'Skip to examples',navFeatures:'Features',navExamples:'Examples',navBenchmark:'Benchmark',navDocs:'Docs',navGet:'Get started',heroTitle:'Many AI agents. One thread through the labyrinth.',heroDesc:'5W1H, tabular data, and directed graphs share one positional grammar: SPACE-separated columns and LF-separated semantic atoms, independently versioned domains.',heroPrimary:'Explore NEMA',heroSecondary:'Read the specification',heroMeta1:'Independent agent domains',heroMeta2:'2D semantic coordinates',heroMeta3:'Human-readable views',f1:'One domain, one task',f1d:'Independent work and review',f2:'2D semantics',f2d:'Horizontal fields, vertical atoms',f3:'Three modes',f3d:'5W1H, Table and Graph',f4:'IDE1.0 rendering',f4d:'Compact source, clear views',exTitle:'One syntax, three kinds of information.',exDesc:'Explore authentic .nema source alongside the human-readable interpretation. Coordinates, graph direction and atom boundaries follow deterministic parsing.',modeTask:'5W1H / Text',modeTable:'Table',modeGraph:'Node–Edge Graph',copy:'Copy source',sourceTitle:'NEMA source',renderTitle:'IDE1.0 semantic view',sourceHint:'One literal Tab precedes a domain header. ASCII spaces determine columns.',demoNote:'This is an executable specification example. Original case and punctuation remain intact.',syntaxTitle:'Let position carry the structure.',syntaxDesc:'Adaptive PascalCase and no typed braces, or separate visual diagram language. Syntax is limited to unambiguous boundaries.',s1:'One Tab marks a domain',s1d:'A header carries ID and revision. Graph adds one extra mode character.',s2:'Default to 5W1H',s2d:'The first row starts at column zero: What, Why, How, Who, When and Where.',s3:'Tab header selects Table',s3d:'A leading Tab on the first body row means a pure table, with vertical text continuation.',s4:'Edges have identity and direction',s4d:'A>X>B gives edge X an identity; the description can continue downward.',benchTitle:'Measure tokens. Do not guess.',benchDesc:'Compare equivalent NEMA, TAB-X control, positional YAML, and reversible .nemat. Results here use locally trained SentencePiece BPE—not GPT, Claude or Gemini billing tokens.',metricLabel:'60 English domains: BPE Token reduction vs positional YAML',benchCaveat:'Official target-model tokenizer tests are still needed, including outputs and correction retries.',benchCard:'Local BPE · equivalent content',benchLegend:'Whitespace-preserving local BPE; high-entropy data may not benefit from compression.',docsTitle:'From source to model training, all in one bundle.',docsDesc:'Examples, parser, tests, training materials and prior experimental versions ship with the site and can be browsed offline.',linkSpec:'Language specification',linkGuide:'Human authoring guide',linkTrain:'AI training guide',linkBench:'Token benchmark report',linkSample:'Complete .nema sample',footerText:"Ariadne's thread. A path through complexity for collaborating agents.",toTop:'Back to top ↑',edgeTitle:'Select a relationship to read its details',rev:'Revision',node:'Node',relation:'Relationship',noRows:'No data',copied:'Copied',graphNote:'Arrow direction follows the parsed source and target, never the visual layout.'}
};
const G = {"zh":{"navGraph":"图结构","graphTitle":"Node 与 Edge 的每一列代表什么？","graphIntro":"Graph 的 X0 负责图结构，X1 是名称，X2 是可选说明。说明不创建额外节点，也不改变箭头方向。","graphRead":"完整图语法与方向示例","nodeType":"NODE · 节点","node0":"稳定的 Node ID，用于引用","node1":"显示名称；精确保留需 \\=","node2":"可选说明：身份认证，不决定拓扑","edgeType":"EDGE · 关系","edge0":"A → B；X 是 Edge 的独立 ID","edge1":"关系名称","edge2":"可选关系说明，可纵向续写","humanView":"人类视图","humanView2":"人类视图","edgePreview":"Reads · Verify session","directionName":"方向速查","allDirections":"更多：自循环、平行边与复杂拓扑","linkGraphGuide":"Graph 字段与方向规范","metaNote":"真实解析器示例：\\= 可精确保留标识符，普通 PascalCase 会作语义拆读。","footerGraph":"Graph 字段与方向详解","footerToken":"Token 中英日实测","footerCodec":"Codec / 压缩传输","guideTask":"X0 What · X1 Why · X2 How · X3 Who · X4 When · X5 Where。X0 只写一句话也合法。","guideTable":"第一行以 Tab 开始选择 Table；该行是表头，数据行第一列非空时开始新记录。","guideGraph":"X0 是 Node ID 或 Edge 表达式，X1 名称，X2 可选说明。悬停即时预览 Node / Edge 的 X2，点击查看完整字段。","legendTask":"首列 What 为主，不需要强制填写 Who。纵向意群可以只追加到指定列。","legendTable":"单元格中的中文、日文可连写；英文如需分隔多个普通词可使用 PascalCase 或纵向意群。","legendGraph":"例如 A \\=LoginAPI Authentication：A 是节点 ID；LoginAPI 是精确名称；Authentication 是可选职责说明（X2），不改变拓扑。","nodeID":"节点 ID · X0","nodeName":"节点名称 · X1","nodeDesc":"节点说明 · X2（可选）","edgeID":"Edge ID · X0 中部","edgeDirection":"方向 · X0","edgeName":"关系名称 · X1","edgeDesc":"关系说明 · X2（可选）","optional":"未填写（允许省略）","selectNode":"节点","selectEdge":"关系","semantics":"该说明只为 AI / 搜索 / 详情视图提供语义，不会添加边或改变箭头。","edgeMeaning":"箭头只由 X0 中的 >、<、= 决定；X2 内容不会改变方向。","literalHint":"\\= 可保留标识符的原始拼写，例如 LoginAPI。","noTopology":"无向关联不显示箭头。","modeGraphNote":"当前 Graph 示例已按本地 Python 解析器输出生成。","hoverHelp":"悬停查看 X2 说明 · 点击固定完整字段 · Tab 聚焦，Enter 查看详情 · 触屏点击查看","hoverGraphCTA":"悬停 Node / Edge，立即阅读描述；点击打开完整字段","hoverNodeKind":"节点说明 · X2","hoverEdgeKind":"关系说明 · X2","hoverOptional":"未填写 X2（可省略）","hoverLabel":"悬停预览（不改变结构）","hoverShow":"悬停说明","hoverClick":"点击查看完整字段","hoverNode":"节点","hoverEdge":"关系","hoverDesc":"说明","hoverNoDescription":"未设置说明","auditReport":"五轮审查报告"},"ja":{"navGraph":"グラフ","graphTitle":"Node / Edge の各列の意味","graphIntro":"X0 は構造、X1 は名前、X2 は任意の説明です。説明はノードや接続方向を増減させません。","graphRead":"グラフ仕様と方向の実例","nodeType":"NODE · ノード","node0":"参照に使う固定 Node ID","node1":"表示名。表記を厳密に保つ場合は \\=","node2":"任意の説明：認証。接続には影響しない","edgeType":"EDGE · 関係","edge0":"A → B。X は Edge 固有 ID","edge1":"関係名","edge2":"任意の関係説明。下方向に継続可能","humanView":"表示例","humanView2":"表示例","edgePreview":"Reads · Verify session","directionName":"方向一覧","allDirections":"さらに詳しく：ループ・並列辺・複雑なグラフ","linkGraphGuide":"Graph フィールドと方向仕様","metaNote":"実際のパーサによるサンプル。\\= は識別子の綴りを保持します。","footerGraph":"Graph の各列と方向","footerToken":"Token 言語別実測","footerCodec":"Codec / 圧縮転送","guideTask":"X0 What · X1 Why · X2 How · X3 Who · X4 When · X5 Where。What だけの単文も有効。","guideTable":"最初の本文行の先頭 Tab で表モード。続く見出しは列名です。","guideGraph":"X0 は Node ID または Edge の表現、X1 は名前、X2 は任意の説明。ホバーで X2 を表示、クリックで詳細を選択します。","legendTask":"What が主列です。Who を必須にせず、必要な列だけ縦方向に延長できます。","legendTable":"日本語・中国語は連続して記述可能。英語は PascalCase または必要時のみ改行します。","legendGraph":"A \\=LoginAPI Authentication：A はノード ID、LoginAPI は厳密な名前、Authentication は任意の役割説明で、構造に影響しません。","nodeID":"Node ID · X0","nodeName":"Node 名 · X1","nodeDesc":"Node 説明 · X2（任意）","edgeID":"Edge ID · X0 の中央","edgeDirection":"方向 · X0","edgeName":"関係名 · X1","edgeDesc":"関係説明 · X2（任意）","optional":"省略可能","selectNode":"ノード","selectEdge":"関係","semantics":"この説明は AI の理解・検索・詳細表示向けで、ノードや矢印を追加しません。","edgeMeaning":"矢印は X0 の >、<、= だけで決まり、X2 の文章では変化しません。","literalHint":"\\= は LoginAPI などの識別子の厳密な綴りを保持します。","noTopology":"無向の関係には矢印が付きません。","modeGraphNote":"このサンプルの表示はローカル Python パーサの結果と一致します。","hoverHelp":"Node / Edge にホバーで X2 説明 · クリックで詳細を固定 · Tab でフォーカス、Enter で選択 · タッチはタップ","hoverGraphCTA":"Node / Edge にホバーすると説明を表示、クリックで詳細を表示","hoverNodeKind":"Node の説明 · X2","hoverEdgeKind":"Edge の説明 · X2","hoverOptional":"X2 は未記入（省略可）","hoverLabel":"ホバープレビュー（グラフ構造は不変）","hoverShow":"ホバー説明","hoverClick":"クリックしてフィールドを見る","hoverNode":"ノード","hoverEdge":"関係","hoverDesc":"説明","hoverNoDescription":"説明なし","auditReport":"5回の監査報告"},"en":{"navGraph":"Graph","graphTitle":"What does each Node and Edge column mean?","graphIntro":"X0 defines graph structure, X1 is the name and X2 is an optional description. A description does not create extra connections or affect arrow direction.","graphRead":"Graph syntax and direction examples","nodeType":"NODE · Vertex","node0":"Stable Node ID used by references","node1":"Display name; use \\= to preserve spelling exactly","node2":"Optional description: authentication; no topology effect","edgeType":"EDGE · Relationship","edge0":"A → B, where X is the independent Edge ID","edge1":"Relationship name","edge2":"Optional edge description; may continue vertically","humanView":"Human view","humanView2":"Human view","edgePreview":"Reads · Verify session","directionName":"Direction cheatsheet","allDirections":"More: loops, parallel edges and complex graphs","linkGraphGuide":"Graph fields and directions","metaNote":"Executable parser sample: \\= preserves exact identifiers; regular PascalCase is semantically split.","footerGraph":"Graph fields and directions","footerToken":"Token benchmarks, EN/ZH/JA","footerCodec":"Codec / transport","guideTask":"X0 What · X1 Why · X2 How · X3 Who · X4 When · X5 Where. A single What column is valid plain text.","guideTable":"The first body line begins with a Tab to select Table mode; that line supplies column labels.","guideGraph":"X0 identifies a Node or Edge, X1 names it, and X2 optionally describes it. Hover for X2; click to inspect all fields.","legendTask":"What is the primary column. Who is optional; vertical continuations can extend any specific column.","legendTable":"Chinese/Japanese may be written continuously; English can use PascalCase and only split into vertical atoms when needed.","legendGraph":"A \\=LoginAPI Authentication: A is the Node ID, LoginAPI is the exact display name, and Authentication is an optional responsibility note (X2), not a connection.","nodeID":"Node ID · X0","nodeName":"Node name · X1","nodeDesc":"Node description · X2 (optional)","edgeID":"Edge ID · inside X0","edgeDirection":"Direction · X0","edgeName":"Relation name · X1","edgeDesc":"Relation description · X2 (optional)","optional":"Omitted (valid)","selectNode":"Node","selectEdge":"Edge","semantics":"The note helps AI understanding, search and detail views. It does not create an edge or change a direction.","edgeMeaning":"Only >, < and = in X0 determine direction; X2 text never changes direction.","literalHint":"\\= preserves exact identifier spelling, such as LoginAPI.","noTopology":"An undirected link has no arrowhead.","modeGraphNote":"This graph example is generated from the local Python parser output.","hoverHelp":"Hover for X2 notes · Click for full fields · Tab to focus, Enter to select · Tap on touchscreens","hoverGraphCTA":"Hover a Node or Edge for its description; click for complete fields","hoverNodeKind":"Node description · X2","hoverEdgeKind":"Edge description · X2","hoverOptional":"No X2 description (optional)","hoverLabel":"Hover preview (does not modify topology)","hoverShow":"Hover description","hoverClick":"Click to inspect all fields","hoverNode":"Node","hoverEdge":"Edge","hoverDesc":"Description","hoverNoDescription":"No description provided","auditReport":"Five-round audit"}};
let locale='zh', mode='task', selectedGraph={kind:'node',id:'A'};
const $=s=>document.querySelector(s);
function elt(tag, cls, txt){const e=document.createElement(tag);if(cls)e.className=cls;if(txt!==undefined)e.textContent=String(txt);return e}
function setLang(lang){locale=lang;document.documentElement.lang=lang==='zh'?'zh-CN':lang==='ja'?'ja':'en';document.body.classList.toggle('lang-ja',lang==='ja');document.body.classList.toggle('lang-en',lang==='en');for(const el of document.querySelectorAll('[data-i]')){el.textContent=L[lang][el.dataset.i]||'';}for(const el of document.querySelectorAll('[data-g]')){el.textContent=G[lang][el.dataset.g]||'';}document.querySelector('[data-i="demoNote"]').textContent=G[lang].metaNote;document.querySelectorAll('.lang').forEach(el=>{const active=el.dataset.lang===lang;el.classList.toggle('active',active);el.setAttribute('aria-pressed',String(active));});$('#humanGuide').href='../docs/NEMA_SPEC_v1.1_'+lang+'.md';renderMode();}
function selectMode(next){mode=next;document.querySelectorAll('.mode').forEach(el=>{const chosen=el.dataset.mode===mode;el.classList.toggle('active',chosen);el.setAttribute('aria-selected',String(chosen));el.tabIndex=chosen?0:-1;});$('#rendered').setAttribute('aria-labelledby','nema-tab-'+mode);renderMode();}
function field(name,value){const row=elt('div','field-card');row.append(elt('div','field-name',name),elt('div','field-value',value||'—'));return row}
function table(data){const t=elt('table','data-table');const thead=elt('thead'),hr=elt('tr');data.headers.forEach(h=>hr.append(elt('th',null,h)));thead.append(hr);t.append(thead);const tbody=elt('tbody');data.rows.forEach(r=>{const tr=elt('tr');r.forEach(c=>tr.append(elt('td',null,c||'—')));tbody.append(tr)});t.append(tbody);return t}
const NS='http://www.w3.org/2000/svg';
function sEl(tag,attrs={}){const e=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,String(v)));return e}
function graphic(data){
 const t=G[locale],wrap=elt('div','graph-view'),stage=elt('div','graph-stage');
 const svg=sEl('svg',{viewBox:'0 0 440 285',class:'graph-svg','aria-label':t.guideGraph,'role':'group'});
 const defs=sEl('defs'),m=sEl('marker',{id:'nema-graph-arrow',viewBox:'0 0 10 10',refX:'9',refY:'5',markerWidth:'7',markerHeight:'7',orient:'auto-start-reverse'});
 m.append(sEl('path',{d:'M0 0 L10 5 L0 10Z',fill:'#f1c17a'}));defs.append(m);svg.append(defs);
 const nodes=data.items.filter(x=>x.kind==='node'),edges=data.items.filter(x=>x.kind==='edge');
 const bundles=new Map();
 for(const edge of edges){const key=[edge.left,edge.right].sort().join('\u0000');if(!bundles.has(key))bundles.set(key,[]);bundles.get(key).push(edge)}
 const laneByEdge=new Map();for(const bundle of bundles.values())bundle.forEach((edge,i)=>laneByEdge.set(edge,i));
 // Geometry is illustrative; semantics and arrow direction always come from X0.
 const coord={A:{x:85,y:138},B:{x:346,y:69},C:{x:346,y:218}};
 nodes.forEach((n,i)=>{if(!coord[n.id]){const a=2*Math.PI*i/nodes.length;coord[n.id]={x:213+125*Math.cos(a),y:140+95*Math.sin(a)}}});
 const selected=(kind,id)=>selectedGraph.kind===kind&&selectedGraph.id===id;
 const tooltip=elt('div','graph-hover-tooltip');tooltip.id='nema-graph-hover';tooltip.setAttribute('role','tooltip');tooltip.setAttribute('aria-hidden','true');tooltip.hidden=true;
 const k=elt('div','hover-kind'),h=elt('strong','hover-heading'),r=elt('span','hover-route'),d=elt('p','hover-description'),hint=elt('small','hover-detail-hint',t.hoverClick);
 tooltip.append(k,h,r,d,hint);
 let openTarget=null,hoveredGroup=null;
 function routeOf(item){if(item.kind==='node')return item.id;
  const src=item.direction==='<'?item.right:item.left,dst=item.direction==='<'?item.left:item.right;
  return item.direction==='='?src+' — '+dst:src+' → '+dst;}
 function positionTooltip(clientX,clientY){
  const rect=stage.getBoundingClientRect(),tw=tooltip.offsetWidth||224,th=tooltip.offsetHeight||100;
  const px=clientX-rect.left,py=clientY-rect.top;
  const maxX=Math.max(6,rect.width-tw-6);
  const x=Math.min(Math.max(px+14,6),maxX);
  const y=py+18+th>rect.height?Math.max(4,py-th-14):py+18;
  tooltip.style.left=x+'px';tooltip.style.top=y+'px';
 }
 function show(item,group,event){
  openTarget=item.id+'|'+item.kind;
  k.textContent=item.kind==='node'?t.hoverNodeKind:t.hoverEdgeKind;
  h.textContent=item.id+' · '+(item.columns[0]||item.id);
  r.textContent=routeOf(item);
  d.textContent=item.columns[1]||t.hoverOptional;
  tooltip.hidden=false;tooltip.setAttribute('aria-hidden','false');
  const rect=group.getBoundingClientRect();
  positionTooltip(event&&Number.isFinite(event.clientX)?event.clientX:rect.left+rect.width/2,
                  event&&Number.isFinite(event.clientY)?event.clientY:rect.top+rect.height/2);
  if(hoveredGroup&&hoveredGroup!==group)hoveredGroup.classList.remove('is-hovered');
  hoveredGroup=group;group.classList.add('is-hovered');
 }
 function hide(){openTarget=null;tooltip.hidden=true;tooltip.setAttribute('aria-hidden','true');if(hoveredGroup)hoveredGroup.classList.remove('is-hovered');hoveredGroup=null}
 function choose(kind,id,restore=''){
  hide();selectedGraph={kind,id};renderMode();
  // Both the SVG and picker are rebuilt: restore focus to the corresponding replacement.
  if(restore){
   const selector=restore==='picker'?'.graph-choice':'[data-graph-kind]';
   const next=Array.from(document.querySelectorAll(selector)).find(el=>(restore==='picker'?el.dataset.pickerKind===kind&&el.dataset.pickerId===id:el.dataset.graphKind===kind&&el.dataset.graphId===id));
   if(next)next.focus({preventScroll:true});
  }
 }
 function affordance(group,item){
  const kind=item.kind,id=item.id,note=item.columns[1]||t.hoverOptional;
  group.setAttribute('role','button');group.setAttribute('tabindex','0');
  group.setAttribute('aria-pressed',String(selected(kind,id)));group.setAttribute('aria-controls','nema-graph-inspector');
  group.setAttribute('aria-label',(kind==='node'?t.hoverNode:t.hoverEdge)+' '+id+', '+(item.columns[0]||'')+', '+routeOf(item)+', '+t.hoverDesc+': '+note);
  group.setAttribute('data-graph-kind',kind);group.setAttribute('data-graph-id',id);
  group.addEventListener('pointerenter',event=>{if(event.pointerType!=='touch')show(item,group,event)});
  group.addEventListener('pointermove',event=>{if(event.pointerType!=='touch'&&openTarget===id+'|'+kind)positionTooltip(event.clientX,event.clientY)});
  group.addEventListener('pointerleave',()=>hide());
  group.addEventListener('focus',()=>show(item,group));
  group.addEventListener('blur',()=>hide());
  group.addEventListener('click',()=>choose(kind,id,'graph'));
  group.addEventListener('keydown',ev=>{
   if(ev.key==='Escape'){ev.preventDefault();hide()}
   if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();choose(kind,id,'graph')}
  });
 }
 edges.forEach(e=>{
  const a=coord[e.left],b=coord[e.right];if(!a||!b)return;
  const from=e.direction==='<'?b:a,to=e.direction==='<'?a:b;
  let path,tx,ty;
  const pair=[e.left,e.right].sort(),bundle=bundles.get(pair.join('\u0000'));
  const lane=laneByEdge.get(e);
  if(e.left===e.right){
   // Multiple self-loops have independent hit targets and visibly distinct paths.
   const extra=lane*24;
   path=`M${from.x-25} ${from.y-15} C${from.x-104-extra} ${from.y-113-extra} ${from.x+99+extra} ${from.y-113-extra} ${from.x+26} ${from.y-14}`;
   tx=from.x;ty=from.y-74-extra*.64;
  } else{
   const dx=to.x-from.x,dy=to.y-from.y,len=Math.hypot(dx,dy)||1,ux=dx/len,uy=dy/len;
   // Use a canonical pair normal: reversing A/B must not flip the lane offset.
   const pa=coord[pair[0]],pb=coord[pair[1]],pl=Math.hypot(pb.x-pa.x,pb.y-pa.y)||1;
   const px=-(pb.y-pa.y)/pl,py=(pb.x-pa.x)/pl;
   const shift=(lane-(bundle.length-1)/2)*26;
   const sx=from.x+ux*48,sy=from.y+uy*29,ex=to.x-ux*48,ey=to.y-uy*29,cx=(sx+ex)/2+px*shift,cy=(sy+ey)/2+py*shift;
   path=`M${sx} ${sy} Q${cx} ${cy} ${ex} ${ey}`;tx=(sx+2*cx+ex)/4;ty=(sy+2*cy+ey)/4-9;
  }
  const group=sEl('g',{class:'graph-edge'+(selected('edge',e.id)?' selected':'')});affordance(group,e);
  group.append(sEl('path',{d:path,class:'edge-visible','marker-end':e.direction==='='?'':'url(#nema-graph-arrow)'}));
  group.append(sEl('path',{d:path,class:'edge-hit'}));
  const lbl=sEl('text',{x:tx,y:ty,'text-anchor':'middle',class:'edge-caption'});lbl.textContent=e.id+' · '+(e.columns[0]||'');group.append(lbl);svg.append(group);
 });
 nodes.forEach(n=>{
  const p=coord[n.id],group=sEl('g',{class:'graph-node'+(selected('node',n.id)?' selected':'')});affordance(group,n);
  group.append(sEl('rect',{x:p.x-47,y:p.y-29,width:94,height:58,rx:11}));
  const id=sEl('text',{x:p.x,y:p.y-5,'text-anchor':'middle',class:'node-label'});id.textContent=n.id;group.append(id);
  const name=sEl('text',{x:p.x,y:p.y+12,'text-anchor':'middle',class:'node-sub'});name.textContent=n.columns[0]||'';group.append(name);svg.append(group);
 });
 stage.append(svg,tooltip);wrap.append(stage,elt('p','graph-hover-help',t.hoverHelp));
 const picker=elt('div','graph-pickers');for(const kind of ['node','edge']){
  const block=elt('div','graph-picker-group');block.append(elt('span','picker-label',t[kind==='node'?'selectNode':'selectEdge']));
  for(const item of data.items.filter(x=>x.kind===kind)){
   const b=elt('button','graph-choice'+(selected(kind,item.id)?' active':''),item.id+' · '+(item.columns[0]||''));b.type='button';b.dataset.pickerKind=kind;b.dataset.pickerId=item.id;b.setAttribute('aria-pressed',String(selected(kind,item.id)));b.setAttribute('aria-controls','nema-graph-inspector');b.addEventListener('click',()=>choose(kind,item.id,'picker'));block.append(b)
  }picker.append(block)
 }
 wrap.append(picker);
 const item=data.items.find(x=>selected(x.kind,x.id))||data.items[0];if(item){
  const box=elt('div','graph-inspector');box.id='nema-graph-inspector';box.setAttribute('role','region');box.setAttribute('aria-live','polite');box.setAttribute('aria-label',t.modeGraphNote);
  const add=(name,value,optional=false)=>{const r=elt('div','inspect-row');r.append(elt('span','inspect-key',name),elt('strong','inspect-value',value||t.optional));if(optional)r.classList.add('optional');box.append(r)};
  if(item.kind==='node'){
   add(t.nodeID,item.id);add(t.nodeName,item.columns[0]);add(t.nodeDesc,item.columns[1]||'',true);
   box.append(elt('p','inspect-note',t.semantics+' '+t.literalHint));
  }else{
   add(t.edgeID,item.id);add(t.edgeDirection,routeOf(item));
   add(t.edgeName,item.columns[0]);add(t.edgeDesc,item.columns[1]||'',true);
   box.append(elt('p','inspect-note',t.edgeMeaning));
  }
  wrap.append(box)
 }
 wrap.append(elt('div','field-caption',t.modeGraphNote));return wrap;
}

function renderMode(){const id=mode==='task'?'Tja1':mode==='table'?'Ttable1':'Gauth1';const item=NEMA_DEMO.find(e=>e.id===id);if(!item)return;$('#sourceCode').textContent=item.raw;$('#filename').textContent=item.id+'.nema';$('#domainType').textContent=mode==='task'?'5W1H':mode==='table'?'Table':'Graph';$('#modeExplainer').textContent=G[locale]['guide'+(mode==='task'?'Task':mode==='table'?'Table':'Graph')];$('#demoLegend').textContent=G[locale]['legend'+(mode==='task'?'Task':mode==='table'?'Table':'Graph')];let root=$('#rendered');root.replaceChildren();if(item.mode==='5w1h'){root.append(elt('div','field-caption',`${item.id} · ${L[locale].rev} ${item.revision}`));Object.entries(item.data).forEach(([k,v])=>root.append(field(k,v)))}else if(item.mode==='table'){root.append(elt('div','field-caption',item.id));root.append(table(item.data))}else{root.append(graphic(item.data))}}
function renderBench(){const data=typeof BENCHMARK!=='undefined'?BENCHMARK.cases.find(c=>c.scenario==='en_60_compact')?.tokenizers?.bpe:null;if(!data)return;const vals=[['NEMA 1.1',data.native],['YAML positional',data.yaml],['NEMA 1.1 + .nemat',data.optimized]];const max=Math.max(...vals.map(x=>x[1]));$('#metricValue').textContent=data.vs_yaml_pct.toFixed(2)+'%';const box=$('#benchmarkBars');box.replaceChildren();for(const [name,v] of vals){const row=elt('div','bar-row'+(name==='NEMA 1.1'?' gold':''));row.append(elt('span',null,name));const track=elt('div','bar-track'),fill=elt('div','bar-fill');fill.style.width=Math.round(100*v/max)+'%';track.append(fill);row.append(track,elt('em',null,v.toLocaleString()));box.append(row)} }
function start(){document.querySelectorAll('.lang').forEach(b=>b.addEventListener('click',()=>setLang(b.dataset.lang)));document.querySelectorAll('.mode').forEach(b=>{b.addEventListener('click',()=>selectMode(b.dataset.mode));b.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const tabs=Array.from(document.querySelectorAll('.mode'));const idx=tabs.indexOf(b);const next=e.key==='Home'?0:e.key==='End'?tabs.length-1:e.key==='ArrowRight'?(idx+1)%tabs.length:(idx+tabs.length-1)%tabs.length;selectMode(tabs[next].dataset.mode);tabs[next].focus()})});$('#copyButton').addEventListener('click',()=>{const raw=$('#sourceCode').textContent;if(navigator.clipboard?.writeText)navigator.clipboard.writeText(raw).catch(()=>fallbackCopy(raw));else fallbackCopy(raw)});$('#navToggle').addEventListener('click',()=>$('#mainNav').classList.toggle('open'));$('#mainNav').querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>$('#mainNav').classList.remove('open')));renderBench();setLang('zh')}
function fallbackCopy(s){const t=elt('textarea');t.value=s;document.body.append(t);t.select();try{document.execCommand('copy')}finally{t.remove()}}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();
