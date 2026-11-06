// NEMA v1.5 geometry validation: real edge direction, on-border arrow tips, parallel lanes.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
require('../website/graph.js');
const root=path.join(__dirname,'..');
const domain=JSON.parse(fs.readFileSync(path.join(root,'examples/03_graph_complex.render.json'),'utf8')).domains[0];
const graph=globalThis.NEMAGraph.layout(domain);
const byId=Object.fromEntries(graph.edges.map(e=>[e.id,e]));
const nodes=Object.fromEntries(graph.nodes.map(n=>[n.id,n]));
assert.equal(byId.X.from,'A');assert.equal(byId.X.to,'B');
assert.equal(byId.Z.from,'C');assert.equal(byId.Z.to,'B'); // B<Z<C -> C→B
assert.equal(byId.R.from,'A');assert.equal(byId.R.to,'B'); // B<R<A -> A→B
assert.equal(byId.U.direction,'undirected');
assert.equal(byId.P.from,'A');assert.equal(byId.P.to,'A');
assert.match(byId.P.path,/ C /); // cubic self-loop
assert.notEqual(byId.X.path,byId.Y.path); // A→B parallel
assert.notEqual(byId.X.path,byId.R.path); // A→B triple parallel
for(const e of graph.edges){
  for(const [point,nodeName] of [[e.start,e.from],[e.end,e.to]]){
    const n=nodes[nodeName];assert.ok(n,`missing node ${nodeName}`);
    const dx=Math.abs(point.x-n.x),dy=Math.abs(point.y-n.y);
    const onBorder=Math.abs(dx-55)<0.02 || Math.abs(dy-27)<0.02;
    assert.ok(onBorder,`arrow anchor not on node border ${e.id}/${nodeName}: ${JSON.stringify(point)}`);
    assert.ok(dx<=55.01 && dy<=27.01,`anchor outside node ${e.id}`);
  }
  assert.ok(Number.isFinite(e.label.x)&&Number.isFinite(e.label.y),`missing label ${e.id}`);
}
console.log(`GRAPH GEOMETRY PASS: ${graph.nodes.length} nodes, ${graph.edges.length} independently selectable edges, directed/reverse/parallel/undirected/self-loop, border arrowheads`);
