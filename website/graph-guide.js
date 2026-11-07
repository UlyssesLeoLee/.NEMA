(() => {'use strict';
const T={"zh":{"back":"← NEMA 首页","title":"节点有身份，边有方向，说明是可选内容。","lead":"Graph 是 NEMA 三模式之一。X0 定义 Node 或 Edge 身份，X1 是名称，X2 是职责或行为说明。","nodeTitle":"为什么写 Authentication？","tabNote":"⇥ 代表领域头前的一个真实 Tab。实际 .nema 文件使用 Tab；示例为了便于阅读使用 ⇥。","column":"列","value":"原文","meaning":"语义","column2":"列","value2":"原文","meaning2":"语义","x0node":"Node ID，图内引用节点 A","x1node":"Node 名称原样保留；行首一个空格声明 Node","x2node":"可选说明：身份认证。供 AI 理解、搜索和详情展示","x3":"可选扩展属性；不参与箭头语法判断","nodeMinimal":"最短合法 Node","nodeMinimalNote":"不写 X2 也合法。名称足够明确时，省略说明更省 Token。","nodeWithNote":"带职责说明的 Node","nodeNote":"Authentication 只是说明，不等于 Edge，也不会自动连接到某个认证服务。","nameCaveat":"注意：␠A LoginAPI Authentication 是合法的 Node 声明；但 Graph 的 X1 默认精确显示 LoginAPI。无需额外 \= 标识符。","edgeTitle":"Edge 的 X2 是独立关系的说明","x0edge":"A → B，X 是独立 Edge ID","x1edge":"关系名称","x2edge":"关系说明：校验会话；下一行两个前置空格继续 X2","edgeCaveat":"线的方向由 X0 唯一决定；X1、X2 和纵向续写只是这条 Edge 的内容，不会修改源节点和目标节点。","directionsTitle":"箭头、平行边、自循环","syntax":"原文","render":"渲染","rule":"规则","forward":"正向","reverse":"反向，不是 A → B","undirected":"无向关联，无箭头","loop":"自循环","parallel":"相同节点之间两条不同 ID 的边","bidirectional":"两个独立 Edge，各自具有内容与身份","shorthand":"正式 Graph 领域头是 ⇥>G1 1（ID 加版本）。单独的 ⇥>1 仅为不完整速记，不符合当前 v1.2 解析器语法。","home":"主页 / 交互图","token":"Token 实测","document":"Graph 设计文档","hoverGuide":"悬停在 Node / Edge 上显示 X2 描述；Tab 聚焦同样可见。点击固定说明，触屏轻触即可。","hoverN":"节点说明 · X2","hoverE":"关系说明 · X2","hoverNone":"未填写 X2（可选）","interTitle":"悬停只读，点击才选中。","interIntro":"Node 与 Edge 的说明都来自 X2。悬停不会添加连线、改变图方向、保存文件或请求 AI。","intPointer":"鼠标悬停","intPointerDesc":"移动到节点矩形、关系连线或名称标签，立即显示名称、真实方向与说明；移走后消失。","intKeyboard":"键盘与辅助功能","intKeyboardDesc":"Tab 聚焦同样预览；Escape 关闭；Enter / 空格选择，并在常驻字段检查器中显示完整内容。","intTouch":"触屏","intTouchDesc":"首页点击即可选中并查看详情；本说明页轻触固定说明，重复点击关闭，卡片在小屏的图下方展示。","intInvariant":"X2 为空时不生成虚构说明；说明只影响可读性，不影响图结构，也不改变 NEMA 的 Token 基准。"},"ja":{"back":"← NEMA トップ","title":"ノードには ID、辺には方向。説明は任意です。","lead":"Graph は NEMA の三つのモードの一つ。X0 は Node / Edge の ID と構造、X1 は名前、X2 は役割または動作の説明です。","nodeTitle":"Authentication は何を意味しますか？","tabNote":"⇥ は実際の Tab 1 文字の表示記号です。.nema では Tab を使用します。","column":"列","value":"元のテキスト","meaning":"意味","column2":"列","value2":"元のテキスト","meaning2":"意味","x0node":"Node ID。A ノードの参照に使用","x1node":"Node 名。Graph X1 は LoginAPI の綴りをそのまま保持します","x2node":"任意の説明：認証。AI の解釈・検索・詳細表示に使用","x3":"任意の拡張属性。矢印の判定には使用しません","nodeMinimal":"最小限の Node","nodeMinimalNote":"X2 は省略可能。名前だけで十分なら記述しない方が Token を節約できます。","nodeWithNote":"役割説明を持つ Node","nodeNote":"Authentication は説明であり、Edge でも自動的なリンク生成でもありません。","nameCaveat":"先頭スペース1文字は Node 宣言、先頭スペースなしは Edge 宣言です。Graph X1 は LoginAPI をそのまま保持します。","edgeTitle":"Edge の X2 は独立した関係説明です","x0edge":"A → B。X は固有の Edge ID","x1edge":"関係名","x2edge":"関係の説明。次の行で先頭スペース2文字により X2 を追加","edgeCaveat":"方向は X0 のみで決まり、X1 / X2 や下方向の追記では変わりません。","directionsTitle":"矢印・並列辺・自己ループ","syntax":"原文","render":"表示","rule":"規則","forward":"順方向","reverse":"逆方向。A → B ではありません","undirected":"無向の関係","loop":"自己ループ","parallel":"同じノード間の異なる ID の2本の辺","bidirectional":"独立した2つの Edge","shorthand":"正式な Graph ヘッダーは ⇥>G1 1（ID とリビジョン）。⇥>1 は省略例で、現在の v1.2 パーサでは無効です。","home":"トップ / インタラクティブ図","token":"Token 実測","document":"Graph 設計書","hoverGuide":"Node / Edge にホバーすると X2 の説明を表示。Tab フォーカスでも確認できます。クリックで固定、タッチでタップします。","hoverN":"Node 説明 · X2","hoverE":"Edge 説明 · X2","hoverNone":"X2 の説明なし（省略可）","interTitle":"ホバーは読み取り専用。選択はクリック時のみ。","interIntro":"Node / Edge の説明は X2 由来です。ホバーで辺の追加、方向変更、保存、AI 呼び出しをしません。","intPointer":"マウスホバー","intPointerDesc":"ノード、線、ラベルで名前・方向・説明を即時表示。離れると非表示。","intKeyboard":"キーボードと支援技術","intKeyboardDesc":"Tab でフォーカスすると同じプレビューを表示。Escape で閉じ、Enter / Space で固定の詳細を開きます。","intTouch":"タッチ操作","intTouchDesc":"トップの図はタップで詳細を選択。この説明ページではタップで表示を固定、再タップで閉じ、小画面では図の下に配置。","intInvariant":"X2 が空なら説明を創作しません。説明は構造と Token ベンチマークに影響しません。"},"en":{"back":"← NEMA Home","title":"Nodes have identity. Edges have direction. Notes are optional.","lead":"Graph is one of NEMA’s three modes. X0 identifies a Node or Edge, X1 names it, and X2 optionally describes its responsibility or behavior.","nodeTitle":"What exactly does Authentication do?","tabNote":"⇥ is a visible placeholder for one real Tab in a domain header; the actual .nema file contains a Tab.","column":"Column","value":"Source","meaning":"Role","column2":"Column","value2":"Source","meaning2":"Role","x0node":"Node ID; used to reference node A","x1node":"Node name. Graph X1 preserves the spelling LoginAPI exactly","x2node":"Optional description: authentication. For AI, search and detail views","x3":"Optional extended attributes; do not affect arrow direction","nodeMinimal":"Minimum valid Node","nodeMinimalNote":"X2 is optional. Omit the note when the name is already informative, saving tokens.","nodeWithNote":"Node with a description","nodeNote":"Authentication is just a note, not an Edge and not an automatic link to an authentication service.","nameCaveat":"Exactly one leading ASCII space declares a Node; an unindented relation declares an Edge. Graph X1 preserves LoginAPI exactly.","edgeTitle":"X2 on an Edge describes the relationship","x0edge":"A → B, with X as the unique Edge ID","x1edge":"Relationship name","x2edge":"Relationship description; two leading spaces on the next line continue X2","edgeCaveat":"X0 alone determines the arrow direction. The name, description and vertical continuation never change its endpoints.","directionsTitle":"Arrows, parallel edges and loops","syntax":"Source","render":"Rendering","rule":"Rule","forward":"Forward","reverse":"Reverse, not A → B","undirected":"Undirected, no arrowhead","loop":"Self-loop","parallel":"Two distinct IDs connecting the same nodes","bidirectional":"Two independent edges, each with its own identity and content","shorthand":"The formal Graph header is ⇥>G1 1 (ID and revision). ⇥>1 is incomplete shorthand and invalid in the current v1.2 parser.","home":"Home / interactive graph","token":"Token measurements","document":"Graph specification","hoverGuide":"Hover a Node or Edge to see its X2 description. Tab focuses the same preview; click pins it, and touch uses tap.","hoverN":"Node note · X2","hoverE":"Edge note · X2","hoverNone":"No X2 description (optional)","interTitle":"Hover is read-only. Click selects.","interIntro":"Node and Edge descriptions come from X2. Hover never creates links, changes direction, saves a file, or calls AI.","intPointer":"Pointer hover","intPointerDesc":"Hover a node, relationship line, or label to see its name, actual direction, and description immediately. Exit to dismiss.","intKeyboard":"Keyboard and accessibility","intKeyboardDesc":"Tab focus shows the same preview. Escape dismisses it; Enter or Space selects the item and opens a persistent field inspector.","intTouch":"Touch interactions","intTouchDesc":"Tap the graph on the homepage to select and inspect. On this guide, tap to pin a note and tap again to close; on phones, the note is placed beneath the diagram.","intInvariant":"Missing X2 means no fabricated description. Hover does not change graph topology or reported NEMA Token benchmark results."}};
let activeLang='zh',activeItem=null,sticky=false;
const graphEntries={A:{kind:'node',id:'A',name:'LoginAPI',route:'A',description:'Authentication'},X:{kind:'edge',id:'X',name:'Reads',route:'A → B',description:'Verify session'},B:{kind:'node',id:'B',name:'TokenStore',route:'B',description:'Session storage'}};
const showcase=document.getElementById('graphShowcase'),popover=document.getElementById('guideGraphTooltip');
function guidePosition(target,event){
  const r=showcase.getBoundingClientRect(),b=target.getBoundingClientRect(),w=popover.offsetWidth||210,h=popover.offsetHeight||120;
  const x=(event&&Number.isFinite(event.clientX)?event.clientX:b.left+b.width/2)-r.left;
  const y=(event&&Number.isFinite(event.clientY)?event.clientY:b.top+b.height/2)-r.top;
  popover.style.left=Math.min(Math.max(x+13,5),Math.max(5,r.width-w-6))+'px';
  popover.style.top=(y+16+h>r.height?Math.max(4,y-h-12):y+16)+'px';
}
function guideShow(itemId,event,keep=false){
  const item=graphEntries[itemId];if(!item)return;
  const el=showcase.querySelector('[data-graph-item="'+itemId+'"]');
  showcase.querySelectorAll('[data-graph-item]').forEach(x=>x.classList.toggle('is-active',x===el));
  document.getElementById('guidePopKind').textContent=T[activeLang][item.kind==='node'?'hoverN':'hoverE'];
  document.getElementById('guidePopTitle').textContent=item.id+' · '+item.name;
  document.getElementById('guidePopRoute').textContent=item.route;
  document.getElementById('guidePopDescription').textContent=item.description||T[activeLang].hoverNone;
  popover.hidden=false;popover.setAttribute('aria-hidden','false');
  activeItem=itemId;sticky=keep;
  guidePosition(el,event);
}
function guideHide(force=false){
  if(sticky&&!force)return;
  activeItem=null;sticky=false;popover.hidden=true;popover.setAttribute('aria-hidden','true');
  showcase.querySelectorAll('[data-graph-item]').forEach(x=>x.classList.remove('is-active'));
}
showcase.querySelectorAll('[data-graph-item]').forEach(el=>{
  const id=el.dataset.graphItem,item=graphEntries[id];
  el.setAttribute('aria-label',item.kind+' '+item.id+', '+item.name+', '+item.route+', X2: '+item.description);
  el.addEventListener('pointerenter',e=>{if(!sticky&&e.pointerType!=='touch')guideShow(id,e)});
  el.addEventListener('pointermove',e=>{if(!sticky&&e.pointerType!=='touch'&&activeItem===id)guidePosition(el,e)});
  el.addEventListener('pointerleave',()=>guideHide());
  el.addEventListener('focus',()=>{if(!sticky)guideShow(id)});
  el.addEventListener('blur',()=>guideHide());
  el.addEventListener('click',()=>{if(sticky&&activeItem===id)guideHide(true);else guideShow(id,null,true)});
  el.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();guideHide(true)}});
});
document.addEventListener('pointerdown',e=>{if(sticky&&!showcase.contains(e.target))guideHide(true)});
function setLang(lang){
  document.documentElement.lang=lang==='zh'?'zh-CN':lang==='ja'?'ja-JP':'en';
  for(const el of document.querySelectorAll('[data-t]'))el.textContent=T[lang][el.dataset.t]||'';
  document.querySelectorAll('[data-lang]').forEach(btn=>btn.setAttribute('aria-pressed',String(btn.dataset.lang===lang)));
  document.getElementById('guideDoc').href='../docs/GRAPH_RENDERER_v1.2.md';
  activeLang=lang;
  showcase.setAttribute('aria-label',T[lang].interTitle);
  showcase.querySelectorAll('[data-graph-item]').forEach(el=>{
   const item=graphEntries[el.dataset.graphItem];
   el.setAttribute('aria-label',T[lang][item.kind==='node'?'hoverN':'hoverE']+' '+item.id+', '+item.name+', '+item.route+', X2: '+(item.description||T[lang].hoverNone));
  });
  if(activeItem)guideShow(activeItem,null,sticky);
}
document.querySelectorAll('[data-lang]').forEach(btn=>btn.addEventListener('click',()=>setLang(btn.dataset.lang)));
setLang('zh');})();
