/* .NEMA Graph Visualizer: an AST-driven geometric renderer for homepage and workbench.
 * Edge geometry, labels, arrowheads and node positions are derived strictly from parsed AST.
 * Two-node layout explicitly separates nodes; reverse links use resolved AST direction. */
(function(root){'use strict';
const NS='http://www.w3.org/2000/svg';
function E(name,attrs={},value){const e=document.createElementNS(NS,name);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));if(value!==undefined)e.textContent=String(value);return e}
function positions(nodes){const n=nodes.length,out=new Map();if(n===1){out.set(nodes[0].id,{x:350,y:172});return out}
if(n===2){out.set(nodes[0].id,{x:165,y:173});out.set(nodes[1].id,{x:535,y:173});return out}
if(n===3){[[142,115],[558,115],[350,264]].forEach(([x,y],i)=>out.set(nodes[i].id,{x,y}));return out}
nodes.forEach((node,i)=>{const angle=i*Math.PI*2/n-Math.PI/2;out.set(node.id,{x:350+242*Math.cos(angle),y:167+112*Math.sin(angle)})});return out}
function anchor(a,b){const dx=b.x-a.x,dy=b.y-a.y;const f=Math.min(64/Math.max(0.000001,Math.abs(dx)),34/Math.max(0.000001,Math.abs(dy)),.5);return{x:a.x+dx*f,y:a.y+dy*f}}
function render(svg,domains,opts={}){
 svg.replaceChildren();svg.setAttribute('viewBox','0 0 700 340');
 const info=opts.info||null,graph=domains.find(d=>d.mode==='graph');
 if(!graph){const t=E('text',{x:350,y:170,'text-anchor':'middle',fill:opts.light?'#657a87':'#b4d5e1','font-size':16,'font-family':'serif'},'当前源码无 Node–Edge 拓扑领域');svg.append(t);if(info)info.textContent='请选择 Node–Edge 案例或输入 Graph 源码。';return {nodes:[],edges:[]}}
 const nodes=graph.records.filter(r=>r.kind==='node'),edges=graph.records.filter(r=>r.kind==='edge'),pos=positions(nodes);
 if(!nodes.length){svg.append(E('text',{x:350,y:170,'text-anchor':'middle'},'没有节点'));return {nodes,edges}}
 const prefix=opts.idPrefix||svg.id||'graph';const defs=E('defs');
 for(const [id,color] of [['edge','#f5cf62'],['reverse','#5ccbbd']]){
   const marker=E('marker',{id:prefix+'-'+id,viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:8,markerHeight:8,orient:'auto'});
   marker.append(E('path',{d:'M0 1.5L9 5L0 8.5L2.5 5Z',fill:color}));
   defs.append(marker);
 }
 svg.append(defs);
 let selection=null;const select=(target,description)=>{selection?.classList.remove('selected');selection=target;target.classList.add('selected');if(info)info.textContent=description;};
 function selectable(group,description){group.setAttribute('role','button');group.setAttribute('tabindex','0');group.setAttribute('aria-label',description);group.addEventListener('click',()=>select(group,description));group.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select(group,description)}})}
 const pairs=new Map();
 edges.forEach(edge=>{
  const a=pos.get(edge.from),b=pos.get(edge.to);if(!a||!b)return;
  const key=[edge.from,edge.to].sort().join('|'),index=pairs.get(key)||0;pairs.set(key,index+1);
  const undirected=edge.operator==='=',reverse=edge.operator==='<',loop=edge.from===edge.to;
  let d,labelX,labelY;
  if(loop){d=`M ${a.x+36} ${a.y-28} C ${a.x+136} ${a.y-143} ${a.x-132} ${a.y-143} ${a.x-36} ${a.y-28}`;labelX=a.x;labelY=a.y-115}
  else{const start=anchor(a,b),end=anchor(b,a),dx=end.x-start.x,dy=end.y-start.y,len=Math.hypot(dx,dy)||1;
   const side=index%2===0?1:-1,bend=(index===0?20:34+index*17)*side,nx=-dy/len,ny=dx/len;
   const cx=(start.x+end.x)/2+nx*bend,cy=(start.y+end.y)/2+ny*bend;
   d=`M ${start.x.toFixed(2)} ${start.y.toFixed(2)} Q ${cx.toFixed(2)} ${cy.toFixed(2)} ${end.x.toFixed(2)} ${end.y.toFixed(2)}`;
   labelX=(start.x+2*cx+end.x)/4;labelY=(start.y+2*cy+end.y)/4-15;
  }
  const group=E('g',{class:'graph-link','data-edge-id':edge.id});
  const path=E('path',{d,class:'graph-edge'+(reverse?' reverse':'')+(undirected?' undirected':''),'data-from':edge.from,'data-to':edge.to});
  if(!undirected)path.setAttribute('marker-end',`url(#${prefix}-${reverse?'reverse':'edge'})`);
  const hit=E('path',{d,class:'graph-hit',stroke:'transparent','stroke-width':24,fill:'none'});
  const label=E('text',{x:labelX,y:labelY,class:'graph-label'+(opts.light?' on-light':'')},`${edge.id} · ${edge.values[1]||edge.operator}`);
  group.append(path,hit,label,E('title',{},`Edge ${edge.id}: ${edge.from} ${undirected?'—':'→'} ${edge.to} · ${edge.values.slice(1).join(' / ')}`));
  selectable(group,`Edge ${edge.id}：${edge.from} ${undirected?'—':'→'} ${edge.to}，${edge.values.slice(1).join(' / ')}`);
  svg.append(group);
 });
 nodes.forEach(node=>{
  const p=pos.get(node.id),g=E('g',{class:'graph-node','data-node-id':node.id});
  // Main Stele Rect
  g.append(E('rect',{x:p.x-64,y:p.y-33,width:128,height:66,rx:8}));
  // Fine Inlaid Inner Hairline
  g.append(E('rect',{x:p.x-59,y:p.y-28,width:118,height:56,rx:5,class:'node-inner-border'}));
  // Four Corner Bronze Rivets
  [[-55,-24],[55,-24],[-55,24],[55,24]].forEach(([ox,oy])=>{
    g.append(E('circle',{cx:p.x+ox,cy:p.y+oy,r:1.8,class:'node-rivet'}));
  });
  g.append(E('text',{x:p.x,y:p.y-5,'text-anchor':'middle',class:'graph-id'},node.id));
  g.append(E('text',{x:p.x,y:p.y+17,'text-anchor':'middle',class:'graph-name'},String(node.values[1]||'').slice(0,18)));
  g.append(E('title',{},node.values.join(' / ')));
  selectable(g,`Node ${node.id}：${node.values.slice(1).join(' / ')}`);
  svg.append(g);
 });
 if(info)info.textContent=`Graph #${graph.id} · ${nodes.length} 个 Node · ${edges.length} 条 Edge。点击节点或关系可查看具体语义。`;
 return {nodes,edges,positions:pos};
}
root.NEMAGraph={render,positions};
})(typeof window!=='undefined'?window:globalThis);