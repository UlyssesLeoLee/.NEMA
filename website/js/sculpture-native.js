/* .NEMA • Labyrinthus Aureus · Sacred Geometry & Celestial Astrolabe of Ariadne
 * An interactive, museum-grade classical Greek astrolabe and 7-circuit Cretan Labyrinth.
 * Replaces polygonal 3D mesh with pure mathematical sacred art and timeless typography. */
(()=>{'use strict';
const stage=document.getElementById('ariadneStatue3d');if(!stage)return;
const state=document.getElementById('stageState');
const box=stage.querySelector('.sculpture-viewport');if(!box)return;

// Create high-resolution astrolabe canvas
const canvas=document.createElement('canvas');
canvas.className='sculpture-canvas native sacred-astrolabe';
canvas.setAttribute('aria-label','克里特神圣星盘迷宫与阿里阿德涅之线，可交互旋转的几何艺术画作');
box.replaceChildren(canvas);

const ctx=canvas.getContext('2d');
if(!ctx){if(state)state.textContent='Canvas 渲染不可用';return;}

const motion=window.NEMAMotion;
let moving=false,lastX=0,lastY=0,dragOffset=0,currentAngle=0;

// Path points along the 7 circuits of the classical Cretan labyrinth (normalized coordinates)
function generateLabyrinthPath(R){
  const pts=[];
  const dr=R*0.075;
  // Entrance at bottom (angle PI/2)
  const baseAngles=[
    {r:R*0.78,start:Math.PI*0.5,end:Math.PI*2.35},
    {r:R*0.705,start:Math.PI*2.35,end:Math.PI*0.8},
    {r:R*0.63,start:Math.PI*0.8,end:Math.PI*2.15},
    {r:R*0.555,start:Math.PI*2.15,end:Math.PI*0.95},
    {r:R*0.48,start:Math.PI*0.95,end:Math.PI*1.95},
    {r:R*0.405,start:Math.PI*1.95,end:Math.PI*1.1},
    {r:R*0.33,start:Math.PI*1.1,end:Math.PI*1.75},
    {r:R*0.255,start:Math.PI*1.75,end:Math.PI*1.25},
    {r:R*0.16,start:Math.PI*1.25,end:Math.PI*2.5}
  ];
  return baseAngles;
}

function drawAstrolabe(now){
  const rect=box.getBoundingClientRect();
  const dpr=Math.min(window.devicePixelRatio||1,2.0);
  const w=Math.max(2,Math.round(rect.width*dpr));
  const h=Math.max(2,Math.round(rect.height*dpr));
  if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}

  ctx.save();
  ctx.scale(dpr,dpr);
  const width=rect.width,height=rect.height;
  const cx=width*0.5,cy=height*0.5;
  const R=Math.min(width,height)*0.44;

  // Background deep Aegean radial vignette
  const bgGrad=ctx.createRadialGradient(cx,cy,R*0.15,cx,cy,R*1.3);
  bgGrad.addColorStop(0,'#0d2238');
  bgGrad.addColorStop(0.5,'#071524');
  bgGrad.addColorStop(1,'#030910');
  ctx.fillStyle=bgGrad;
  ctx.fillRect(0,0,width,height);

  // Compute rotation angle from shared motion timeline + user drag
  const autoYaw=motion?motion.tick(now):0;
  currentAngle=autoYaw+dragOffset;

  ctx.save();
  ctx.translate(cx,cy);
  ctx.rotate(currentAngle);

  // 1. Concentric astronomical reference circles
  ctx.strokeStyle='rgba(212, 175, 55, 0.12)';
  ctx.lineWidth=1;
  [0.96,0.88,0.80,0.68,0.52,0.36,0.20].forEach(factor=>{
    ctx.beginPath();ctx.arc(0,0,R*factor,0,Math.PI*2);ctx.stroke();
  });

  // 2. Faint Golden Spiral / Sacred Coordinate Rays
  ctx.strokeStyle='rgba(212, 175, 55, 0.08)';
  for(let i=0;i<12;i++){
    const ang=i*(Math.PI/6);
    ctx.beginPath();
    ctx.moveTo(Math.cos(ang)*R*0.2,Math.sin(ang)*R*0.2);
    ctx.lineTo(Math.cos(ang)*R*0.96,Math.sin(ang)*R*0.96);
    ctx.stroke();
  }

  // 3. Outer Graduated Bezel: 360 degree ticks
  for(let deg=0;deg<360;deg+=2){
    const rad=deg*(Math.PI/180);
    const cos=Math.cos(rad),sin=Math.sin(rad);
    const isMajor=deg%30===0;
    const isMid=deg%10===0;
    const len=isMajor?14:isMid?9:5;
    ctx.strokeStyle=isMajor?'#f5cf62':isMid?'rgba(245, 207, 98, 0.65)':'rgba(212, 175, 55, 0.28)';
    ctx.lineWidth=isMajor?2:1;
    ctx.beginPath();
    ctx.moveTo(cos*(R*0.96-len),sin*(R*0.96-len));
    ctx.lineTo(cos*R*0.96,sin*R*0.96);
    ctx.stroke();
  }

  // 4. Four Cardinal Greek Celestial Inscriptions
  const cardinals=[
    {label:'ΒΟΡΕΑΣ',angle:-Math.PI/2,color:'#f7d77b',symbol:'✦'},
    {label:'ΑΠΗΛΙΩΤΗΣ',angle:0,color:'#d4af37',symbol:'◈'},
    {label:'ΝΟΤΟΣ',angle:Math.PI/2,color:'#d4af37',symbol:'◈'},
    {label:'ΖΕΦΥΡΟΣ',angle:Math.PI,color:'#d4af37',symbol:'◈'}
  ];
  ctx.font='bold 9px "Cinzel", "Times New Roman", Georgia, serif';
  ctx.textAlign='center';
  ctx.textBaseline='middle';
  cardinals.forEach(c=>{
    const tx=Math.cos(c.angle)*R*0.84;
    const ty=Math.sin(c.angle)*R*0.84;
    ctx.save();
    ctx.translate(tx,ty);
    ctx.rotate(c.angle+Math.PI/2);
    ctx.fillStyle=c.color;
    ctx.fillText(c.symbol+' '+c.label,0,0);
    ctx.restore();
  });

  // 5. Inscribed Epigraphic Greek Ring
  const epigraph='· ΕΝ ΤΩΙ ΛΑΒΥΡΙΝΘΩΙ ΤΟ ΝΗΜΑ · IN LABYRINTHO FILUM · KOSMOS ET ORDO ·';
  ctx.font='700 8.5px "Cinzel", Georgia, serif';
  ctx.fillStyle='rgba(212, 175, 55, 0.55)';
  const epiRad=R*0.76;
  const step=(Math.PI*2)/epigraph.length;
  for(let i=0;i<epigraph.length;i++){
    const a=i*step;
    ctx.save();
    ctx.rotate(a);
    ctx.fillText(epigraph[i],0,-epiRad);
    ctx.restore();
  }

  // 6. The Classical 7-Circuit Cretan Labyrinth Walls
  const circuits=8;
  const stepR=(R*0.70-R*0.16)/circuits;
  ctx.strokeStyle='rgba(240, 232, 218, 0.45)';
  ctx.lineWidth=2;
  for(let k=1;k<=circuits;k++){
    const rk=R*0.16+k*stepR;
    const openingAngle=((k%2===0)?Math.PI*0.45:Math.PI*1.45);
    ctx.beginPath();
    ctx.arc(0,0,rk,openingAngle+0.25,openingAngle+Math.PI*2-0.25);
    ctx.stroke();
  }

  // 7. Ariadne's Golden Thread (Aureum Nema)
  const threadArcs=generateLabyrinthPath(R);
  ctx.save();
  // Multi-pass radiant golden glow
  ctx.shadowColor='#f5cf62';
  ctx.shadowBlur=12;
  ctx.strokeStyle='#ffd700';
  ctx.lineWidth=3.2;
  ctx.lineCap='round';
  ctx.beginPath();
  threadArcs.forEach((seg,idx)=>{
    if(idx===0)ctx.arc(0,0,seg.r,seg.start,seg.end);
    else ctx.arc(0,0,seg.r,seg.start,seg.end,idx%2===1);
  });
  ctx.stroke();

  // Core bright gold highlight
  ctx.shadowBlur=0;
  ctx.strokeStyle='#fffef0';
  ctx.lineWidth=1.2;
  ctx.stroke();
  ctx.restore();

  // 8. The Living Guide Ember (Ariadne's Star) traversing the labyrinth
  const t=(now*0.00008)%1;
  const segIdx=Math.floor(t*threadArcs.length);
  const segFraction=(t*threadArcs.length)-segIdx;
  const activeSeg=threadArcs[Math.min(segIdx,threadArcs.length-1)];
  const emberAngle=activeSeg.start+(activeSeg.end-activeSeg.start)*segFraction;
  const ex=Math.cos(emberAngle)*activeSeg.r;
  const ey=Math.sin(emberAngle)*activeSeg.r;

  // Ember Outer Aura
  const aura=ctx.createRadialGradient(ex,ey,1,ex,ey,16);
  aura.addColorStop(0,'rgba(255, 235, 130, 0.85)');
  aura.addColorStop(0.35,'rgba(212, 175, 55, 0.45)');
  aura.addColorStop(1,'rgba(212, 175, 55, 0)');
  ctx.fillStyle=aura;
  ctx.beginPath();ctx.arc(ex,ey,16,0,Math.PI*2);ctx.fill();

  // Ember Core
  ctx.fillStyle='#ffffff';
  ctx.beginPath();ctx.arc(ex,ey,3.5,0,Math.PI*2);ctx.fill();

  // 9. Central Sanctuary of Daedalus & Ariadne
  const centerR=R*0.14;
  const centGrad=ctx.createRadialGradient(0,0,0,0,0,centerR);
  centGrad.addColorStop(0,'#f8e5a8');
  centGrad.addColorStop(0.7,'#d4af37');
  centGrad.addColorStop(1,'#876214');
  ctx.fillStyle=centGrad;
  ctx.beginPath();ctx.arc(0,0,centerR,0,Math.PI*2);ctx.fill();

  ctx.strokeStyle='#fff4d0';
  ctx.lineWidth=1.5;
  ctx.stroke();

  // Central Epigraphic Inscription
  ctx.font='bold 14px "Cinzel", Georgia, serif';
  ctx.fillStyle='#091624';
  ctx.textAlign='center';
  ctx.textBaseline='middle';
  ctx.fillText('νῆμα',0,0);

  ctx.restore(); // restore rotation
  ctx.restore(); // restore dpr scale
}

let visible=true;
const obs=new IntersectionObserver(es=>{visible=es[0].isIntersecting;motion?.setVisible(visible);});
obs.observe(stage);

function frame(now){
  requestAnimationFrame(frame);
  if(!visible)return;
  drawAstrolabe(now);
}
requestAnimationFrame(frame);

// Pointer interaction for graceful manual rotation
box.addEventListener('pointerdown',e=>{
  moving=true;
  motion?.interaction(true);
  lastX=e.clientX;
  box.setPointerCapture(e.pointerId);
});
box.addEventListener('pointermove',e=>{
  if(!moving)return;
  const dx=e.clientX-lastX;
  dragOffset+=dx*0.008;
  motion?.nudge(dx/240);
  lastX=e.clientX;
});
function endDrag(){moving=false;motion?.interaction(false);}
box.addEventListener('pointerup',endDrag);
box.addEventListener('pointercancel',endDrag);

// Unified Public API matching all contract expectations
window.NEMA_STATUE={
  ready:true,
  mode:'sacred-astrolabe',
  turn(y){
    dragOffset=0;
    motion?.setAngle(y);
  },
  reset(){
    dragOffset=0;
    motion?.reset();
  },
  pause(v){motion?.pause(v);},
  screenshot(){
    return canvas.toDataURL('image/png');
  },
  get angle(){return currentAngle;},
  stop(){obs.disconnect();}
};

stage.classList.add('is-live');
if(state)state.textContent='克里特神圣星盘迷宫 · 阿里阿德涅之线 · 运转中';
window.dispatchEvent(new Event('nema-statue-ready'));
})();