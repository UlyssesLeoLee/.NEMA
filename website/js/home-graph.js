/* Home explanatory visualization is driven by the SAME .NEMA sources in benchmark data. */
(()=>{'use strict';const panel=document.getElementById('benchmarkRendered');if(!panel)return;
const dataset=window.NEMA_BENCH?.records||[],names=['What','Why','How','Who','When','Where'];
function dom(n,cl,text){const e=document.createElement(n);if(cl)e.className=cl;if(text!==undefined)e.textContent=String(text);return e}
function val(v){return v===null?'Null':v&&typeof v==='object'?'Missing':v===''?'""':String(v)}
function draw(scenario){panel.replaceChildren();const row=dataset.find(x=>x.scenario===scenario&&x.format==='nema');if(!row)return;
let domains;try{domains=window.NemaStrict.parse(row.source)}catch(e){panel.append(dom('p','bench-fail','源数据解析失败：'+e.message));return}
const entity=domains[0];if(!entity)return;
if(entity.mode==='graph'){
 const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('role','img');svg.setAttribute('aria-label','Node–Edge 实际关系图，点击节点或关系可查看说明');svg.id='benchGraphSVG';
 const caption=dom('p','bench-diagram-caption');panel.append(svg,caption);
 window.NEMAGraph.render(svg,domains,{info:caption,light:true,idPrefix:'bench-home'});
}else if(entity.mode==='table'){
 panel.append(dom('h4','bench-render-title','Table · 实际列结构'));
 const grid=dom('div','bench-table-scroll'),table=dom('table','bench-actual-table'),thead=dom('thead'),hr=dom('tr');entity.columns.forEach(k=>hr.append(dom('th','',k)));thead.append(hr);table.append(thead);
 const body=dom('tbody');entity.records.forEach(r=>{const tr=dom('tr');r.values.forEach(v=>tr.append(dom('td','',val(v))));body.append(tr)});table.append(body);grid.append(table);panel.append(grid,dom('p','bench-diagram-caption','表头、缺失列与 Null 均由解析后的 AST 渲染；不是单独绘制的示意表。'));
}else if(entity.mode==='5w1h'){
 panel.append(dom('h4','bench-render-title','5W1H · 六个固定语义坐标'));
 const row=entity.records[0],grid=dom('div','bench-six');names.forEach((n,i)=>{const card=dom('div','bench-dimension'),tag=dom('b','',n),value=dom('span','',val(row.values[i]));card.append(tag,value);grid.append(card)});panel.append(grid,dom('p','bench-diagram-caption','六列 What / Why / How / Who / When / Where 按固定索引渲染。'));
}}
window.addEventListener('nema-benchmark-case',e=>draw(e.detail.scenario));draw('node_edge');
})();
