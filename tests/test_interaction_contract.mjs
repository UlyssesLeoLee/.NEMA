import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const dir=new URL('../website/',import.meta.url);const file=x=>fs.readFileSync(new URL(x,dir),'utf8');
function runScript(source,ctx){vm.runInNewContext(source,ctx,{timeout:4000})}
// R1: real continuous 360° rotation, pause, manual hold, resume, reset
let now=0;const doc={body:{classList:{add(){}}},getElementById(){return null}};
const win={};const context={window:win,document:doc,performance:{now:()=>now},matchMedia:()=>({matches:false}),Math};
runScript(file('js/sculpture-motion.js'),context);
const m=win.NEMAMotion;assert.equal(m.period,24000);assert.equal(m.tick(0),0);
for(let i=1;i<=60;i++){now=i*50;m.tick(now)}const a1=m.angle;assert(a1>.70&&a1<.82,'should rotate 45 degrees within 3 seconds, not sway ±3°');
m.pause(true);for(let i=61;i<=95;i++){now=i*50;m.tick(now)}assert.equal(m.angle,a1,'pause must freeze rotation');
m.pause(false);now=4800;m.tick(now);now=4850;m.tick(now);assert(m.angle>a1,'resume must progress');
now=4850;m.setAngle(Math.PI/2);const view=m.angle;for(let i=1;i<=70;i++){now=4850+i*50;m.tick(now)}assert.equal(m.angle,view,'manual view holds for 5 seconds');
for(let i=71;i<=130;i++){now=4850+i*50;m.tick(now)}assert(m.angle>view,'auto rotation resumes after hold');
m.reset();assert.equal(m.angle,0);now=11900;m.tick(now);m.setVisible(false);const frozen=m.angle;for(let i=1;i<30;i++){now+=50;m.tick(now)}assert.equal(m.angle,frozen,'off-screen pauses automatically');
// R2: all Graph variants derive from strict AST, render disjoint 2-node layouts
const svgNodes=[];
class FakeElement{constructor(name){this.nodeName=name;this.children=[];this.attrs={};this.listeners={};this.classList={add(){},remove(){}};this.textContent='';this.id='test-graph'}setAttribute(k,v){this.attrs[k]=String(v)}getAttribute(k){return this.attrs[k]}append(...e){this.children.push(...e)}replaceChildren(...e){this.children=[...e]}addEventListener(name,f){this.listeners[name]=f}}
const graphWin={};const graphCtx={window:graphWin,document:{createElementNS:(ns,name)=>new FakeElement(name)},Math};
runScript(file('strict-parser.js'),graphCtx);runScript(file('js/graph-renderer.js'),graphCtx);
const p=graphWin.NemaStrict.parse;
const cases={
 forward:' \\>3 1\nA LoginAPI Authentication\nB TokenStore Storage\nA>X>B Reads Session',
 reverse:' \\>3 1\nA LoginAPI Authentication\nB TokenStore Storage\nA<X<B Responds Session',
 undirected:' \\>3 1\nA LoginAPI Authentication\nB TokenStore Storage\nA=U=B Shares SecurityPolicy',
 loop:' \\>3 1\nA Worker Executor\nA>P>A Retry Once',
 parallel:' \\>3 1\nA LoginAPI Authentication\nB TokenStore Storage\nA>X>B Reads Session\nA>Y>B Writes Audit\nB>Z>A Returns Result'
};
for(const [kind,code] of Object.entries(cases)){
 const svg=new FakeElement('svg'),info={textContent:''};const graph=p(code);const result=graphWin.NEMAGraph.render(svg,graph,{info});
 assert.equal(result.nodes.length,kind==='loop'?1:2,kind);assert.equal(result.edges.length,kind==='parallel'?3:1,kind);
 assert.equal(svg.children.filter(n=>n.attrs.class==='graph-node').length,result.nodes.length,kind);
 const edgeGroups=svg.children.filter(n=>n.attrs.class==='graph-link');assert.equal(edgeGroups.length,result.edges.length,kind);
 if(result.nodes.length===2){const a=result.positions.get('A'),b=result.positions.get('B');assert(b.x-a.x>250,'two nodes must not overlap')}
 for(const g of edgeGroups){const path=g.children.find(x=>x.nodeName==='path'&&x.attrs['data-from']);assert(path,'rendered edge must have real path');if(kind==='undirected')assert(!path.attrs['marker-end']);else assert(path.attrs['marker-end'],'directed edge must show arrow')}
 if(kind==='reverse')assert.equal(result.edges[0].from,'B');
 edgeGroups[0].listeners.click();assert(info.textContent.includes('Edge'),'click edge should update detail');
 console.log('PASS graph',kind,result.nodes.length,'nodes',result.edges.length,'edges');
}
// R3: benchmark source must agree with graph rendering
const benchWin={};runScript(file('benchmark-data.js'),{window:benchWin});const src=benchWin.NEMA_BENCH.records.find(x=>x.scenario==='node_edge'&&x.format==='nema').source;const nodeGraph=p(src).find(x=>x.mode==='graph');assert.equal(nodeGraph.records.filter(r=>r.kind==='edge').length,3);
// R4: page-level linked affordances and key IDs
for(const htmlName of ['index.html','grammar.html','playground.html','downloads.html']){const html=file(htmlName);assert(html.includes('id="navLinks"'));assert(html.includes('premier.js'));}
for(const id of ['stageFront','stageLeft','stageRight','stageReset','motionToggle','stageCapture','benchmarkGraph'])assert(file('index.html').includes(`id="${id}"`));
for(const id of ['parseNow','saveText','copyText','sampleSelect','liveNodeGraph','graphLegend'])assert(file('playground.html').includes(`id="${id}"`));
console.log('PASS motion/controls/AST graph layout/format benchmarks/navigation contracts');
