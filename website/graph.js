/* NEMA v1.5 deterministic directed multigraph layout. No graph semantics inferred from drawing order.
   The parsed edge.from/edge.to is the single source of truth. */
(function (root) {'use strict';
  const WIDTH=620, HEIGHT=380, NODE_WIDTH=110, NODE_HEIGHT=54;
  const point=(x,y)=>({x,y});
  const round=n=>Math.round(n*100)/100;
  function border(center, toward) {
    const dx=toward.x-center.x, dy=toward.y-center.y;
    if (dx===0 && dy===0) return point(center.x,center.y);
    const scale=1/Math.max(Math.abs(dx)/(NODE_WIDTH/2),Math.abs(dy)/(NODE_HEIGHT/2));
    return point(round(center.x+dx*scale),round(center.y+dy*scale));
  }
  function positions(nodeIds) {
    const positions={};const count=nodeIds.length;
    nodeIds.forEach((id,i)=>{
      if(count===1) positions[id]=point(WIDTH/2,HEIGHT/2);
      else if(count===2) positions[id]=point(i===0?175:445,190);
      else {
        const ang=-Math.PI/2+Math.PI*2*i/count;
        positions[id]=point(round(WIDTH/2+213*Math.cos(ang)),round(HEIGHT/2+95*Math.sin(ang)));
      }
    });
    return positions;
  }
  function layout(domain) {
    const nodes=domain.rows.filter(r=>r.node);
    const inputEdges=domain.rows.filter(r=>r.edge);
    const pos=positions(nodes.map(r=>r.node.id));
    const graphNodes=nodes.map(r=>({id:r.node.id,name:r.cells[1]||'',...pos[r.node.id]}));
    const grouped=new Map();
    for(const r of inputEdges) {
      const e=r.edge;
      if(!pos[e.from]||!pos[e.to]) continue;
      const pair=[e.from,e.to].sort();const key=pair.join('\u0000');
      if(!grouped.has(key)) grouped.set(key,[]);
      grouped.get(key).push(r);
    }
    const graphEdges=[];
    for(const rows of grouped.values()){
      const total=rows.length;
      rows.forEach((r,index)=>{
        const e=r.edge,a=pos[e.from],b=pos[e.to];
        let path, start, end, label;
        if(e.from===e.to){
          const lift=70+index*27;
          start=point(round(a.x+NODE_WIDTH*.28),round(a.y-NODE_HEIGHT/2));
          end=point(round(a.x-NODE_WIDTH*.28),round(a.y-NODE_HEIGHT/2));
          // Curved arrow pointing into the *same* node, entirely outside its top edge.
          const c1=point(a.x+90+index*8,a.y-lift);
          const c2=point(a.x-90-index*8,a.y-lift);
          path=`M ${start.x} ${start.y} C ${c1.x} ${c1.y} ${c2.x} ${c2.y} ${end.x} ${end.y}`;
          label=point(round(a.x),round(a.y-lift*.85));
        } else {
          const dx=b.x-a.x,dy=b.y-a.y,dist=Math.hypot(dx,dy)||1;
          const ux=dx/dist,uy=dy/dist;
          const canonical=e.from<e.to?1:-1;
          const lane=(index-(total-1)/2)*42;
          const local=lane*canonical;
          const control=point(round((a.x+b.x)/2-uy*local*2),round((a.y+b.y)/2+ux*local*2));
          start=border(a,control);end=border(b,control);
          path=`M ${start.x} ${start.y} Q ${control.x} ${control.y} ${end.x} ${end.y}`;
          const mid=point((start.x+end.x+2*control.x)/4,(start.y+end.y+2*control.y)/4);
          label=point(round(mid.x),round(mid.y-14));
        }
        graphEdges.push({id:e.id,from:e.from,to:e.to,direction:e.direction,relation:r.cells[1]||'',description:r.cells.slice(2).join(' · '),path,start,end,label});
      });
    }
    // Keep labels legible for dense crossings; never alter the directed edge paths.
    const placed=[];
    const rect=(x,y,w,h)=>({l:x-w/2,r:x+w/2,t:y-h,b:y+5});
    const overlap=(a,b)=>a.l<b.r+5&&a.r+5>b.l&&a.t<b.b+3&&a.b+3>b.t;
    const blocked=graphNodes.map(n=>({l:n.x-NODE_WIDTH/2,r:n.x+NODE_WIDTH/2,t:n.y-NODE_HEIGHT/2,b:n.y+NODE_HEIGHT/2}));
    for(const edge of graphEdges){
      const labelText=`${edge.id} · ${edge.relation||'Edge'}`;
      const w=Math.max(25,labelText.length*6.6),h=17;
      const shifts=[[0,0],[0,-20],[0,20],[-40,0],[40,0],[-50,-20],[50,20],[-65,10],[65,-10],[0,-42],[0,42]];
      let winner=null,best=Infinity;
      for(const [dx,dy] of shifts){
        const pt=point(edge.label.x+dx,edge.label.y+dy);
        const box=rect(pt.x,pt.y,w,h);
        const obstruction=[...placed,...blocked].reduce((a,b)=>a+(overlap(box,b)?1:0),0);
        const out=box.l<6||box.r>WIDTH-6||box.t<6||box.b>HEIGHT-6?10:0;
        const cost=obstruction*100+out*100+Math.hypot(dx,dy)*.3;
        if(cost<best){winner={pt,box};best=cost}
        if(cost===0)break;
      }
      if(winner){edge.label=winner.pt;placed.push(winner.box)}
    }
    return {width:WIDTH,height:HEIGHT,nodes:graphNodes,edges:graphEdges};
  }
  root.NEMAGraph={layout,border};
})(typeof window!=='undefined'?window:globalThis);
