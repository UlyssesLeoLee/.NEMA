// Real Three.js WebGL cel-shading accent — pinned upstream MIT version 0.187.0.
// Fully optional: the Greek myth illustration remains functional offline and under reduced motion.
const target=document.querySelector('#threeStage');
const reduced=window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
if(target&&!reduced&&window.innerWidth>=780){
  (async()=>{
    try{
      const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.187.0/build/three.module.js');
      if(!target.isConnected)return;
      const w=Math.max(320,target.clientWidth),h=Math.max(300,target.clientHeight);
      const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(38,w/h,.1,100);
      camera.position.set(0,0,12.8);
      const renderer=new THREE.WebGLRenderer({alpha:true,antialias:true,powerPreference:'low-power'});
      renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.6));renderer.setSize(w,h);
      renderer.setClearColor(0x000000,0);renderer.outputColorSpace=THREE.SRGBColorSpace;
      target.appendChild(renderer.domElement);
      scene.add(new THREE.HemisphereLight(0xffefd1,0x16233a,2));
      const key=new THREE.DirectionalLight(0xffd08c,2.4);key.position.set(-4,6,8);scene.add(key);
      const group=new THREE.Group();group.position.set(.4,-.1,0);scene.add(group);
      // Greek geometric frieze: substantial volumes with ink-outline passes (cel-shaded 3D→2D).
      const marble=new THREE.MeshToonMaterial({color:0xe6d4b6,gradientMap:null,flatShading:true});
      const ink=new THREE.LineBasicMaterial({color:0x0a1424,transparent:true,opacity:.9});
      for(const x of [-2.5,2.5]){
        const col=new THREE.Mesh(new THREE.CylinderGeometry(.22,.25,3.8,12),marble);col.position.set(x,-.85,-2);group.add(col);
        const capital=new THREE.Mesh(new THREE.BoxGeometry(.72,.36,.65),marble);capital.position.set(x,1.11,-2);group.add(capital);
        for(const mesh of [col,capital]){const edge=new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry,30),ink);mesh.add(edge)}
      }
      // Golden Ariadne thread, a physically 3D tapered tube following a braided spatial path.
      const pts=[];for(let i=0;i<=120;i++){let t=i/120*Math.PI*3.6;let rad=1.72-i/120*1.34;pts.push(new THREE.Vector3(Math.cos(t)*rad+.4,Math.sin(t)*rad-.65,Math.sin(t*1.65)*.6+1.6))}
      const curve=new THREE.CatmullRomCurve3(pts),geo=new THREE.TubeGeometry(curve,360,.034,8,false);
      const gold=new THREE.Mesh(geo,new THREE.MeshToonMaterial({color:0xffc66a,emissive:0x6e350a,emissiveIntensity:.25}));group.add(gold);
      const orb=new THREE.Mesh(new THREE.IcosahedronGeometry(.2,1),new THREE.MeshToonMaterial({color:0xffe2a1}));orb.position.copy(pts[pts.length-1]);group.add(orb);
      const scatter=new THREE.InstancedMesh(new THREE.TetrahedronGeometry(.042),new THREE.MeshBasicMaterial({color:0xf6c378}),12);
      const mat=new THREE.Matrix4();for(let i=0;i<12;i++){let p=pts[Math.min(120,8*i+7)];mat.makeTranslation(p.x+.18*Math.sin(i*7),p.y+.1*Math.cos(i*3),p.z);scatter.setMatrixAt(i,mat)}scatter.instanceMatrix.needsUpdate=true;group.add(scatter);
      let t=0,active=true,raf=0;
      const resize=()=>{const width=target.clientWidth,height=target.clientHeight;if(width<1||height<1)return;camera.aspect=width/height;camera.updateProjectionMatrix();renderer.setSize(width,height)};
      const io=('IntersectionObserver'in window)?new IntersectionObserver(es=>{active=es[0]?.isIntersecting??true}):null;if(io)io.observe(target);
      const ro=('ResizeObserver'in window)?new ResizeObserver(resize):null;if(ro)ro.observe(target);
      const frame=()=>{raf=requestAnimationFrame(frame);if(!active)return;t+=.006;group.rotation.y=Math.sin(t*.58)*.17;group.rotation.x=Math.sin(t*.41)*.065;gold.material.emissiveIntensity=.19+.11*(.5+.5*Math.sin(t));renderer.render(scene,camera)};
      frame();window.addEventListener('pagehide',()=>{cancelAnimationFrame(raf);io?.disconnect();ro?.disconnect();renderer.dispose();geo.dispose()},{once:true});
      target.dataset.three='live';
    }catch(e){target.dataset.three='fallback';/* Decorative fallback stays readable and offline. */}
  })();
}
