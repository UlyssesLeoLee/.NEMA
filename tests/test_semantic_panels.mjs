import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const root=new URL('../website/',import.meta.url),load=p=>fs.readFileSync(new URL(p,root),'utf8');
class El{constructor(tag){this.tagName=tag;this.children=[];this.className='';this.textContent='';this.attrs={};this.id='';this.classList={add(){},remove(){}};this.listeners={};}append(...c){this.children.push(...c)}replaceChildren(...c){this.children=[...c]}setAttribute(k,v){this.attrs[k]=String(v)}addEventListener(k,v){this.listeners[k]=v}}
const panel=new El('div');const handlers={};const window={addEventListener:(k,fn)=>handlers[k]=fn};const document={getElementById:id=>id==='benchmarkRendered'?panel:null,createElement:n=>new El(n),createElementNS:(ns,n)=>new El(n)};
const context={window,document,Math,console};for(const f of ['strict-parser.js','benchmark-data.js','js/graph-renderer.js','js/home-graph.js'])vm.runInNewContext(load(f),context);
const all=(e)=>[e,...e.children.flatMap(all)];
assert(all(panel).some(e=>e.tagName==='svg'),'Node-Edge visual present on page load');
assert.equal(all(panel).filter(e=>e.attrs['data-node-id']).length,3,'must render 3 benchmark nodes from AST');
assert.equal(all(panel).filter(e=>e.attrs['data-edge-id']).length,3,'must render 3 benchmark edges from AST');
handlers['nema-benchmark-case']({detail:{scenario:'table_with_null'}});
assert(all(panel).some(e=>e.tagName==='table'),'Table must visibly render an actual table');
assert(all(panel).some(e=>e.tagName==='td'),'Table must show actual parsed row cells');
handlers['nema-benchmark-case']({detail:{scenario:'five_w_one_h'}});
assert.equal(all(panel).filter(e=>e.className==='bench-dimension').length,6,'5W1H must show six semantic fields');
handlers['nema-benchmark-case']({detail:{scenario:'node_edge'}});
assert.equal(all(panel).filter(e=>e.attrs['data-edge-id']).length,3);
console.log('PASS benchmark semantic visual switching: Table rows, 5W1H six fields, Graph 3 nodes and 3 edges');
