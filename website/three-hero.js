/** .NEMA — Ariadne's marble thread / comic-toon installation.
 * Decorative, entirely procedural geometry. No external 3D model required.
 * Rendering pauses when hidden and respects prefers-reduced-motion.
 */
const stage = document.querySelector('#threeStage');
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
if (stage && !reduceMotion.matches) {
  (async () => {
    let renderer, observer, resizeObserver, frameId = 0, destroyed = false;
    const cleanups = [];
    const geometries = new Set(), materials = new Set(), textures = new Set();
    try {
      const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.171.0/build/three.module.js');
      if (!stage.isConnected) return;
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(34, 1, .1, 80);
      camera.position.set(0.1, .2, 11.7);
      const world = new THREE.Group(); scene.add(world);
      renderer = new THREE.WebGLRenderer({alpha:true,antialias:true,powerPreference:'low-power'});
      renderer.setClearColor(0x000000, 0);
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.7));
      stage.prepend(renderer.domElement);
      renderer.domElement.setAttribute('aria-label','阿里阿德捏的大理石卡通渲染雕像：手持金色线团，金线在空中缓缓流动');
      renderer.domElement.setAttribute('role','img');
      scene.add(new THREE.HemisphereLight(0xf1f5ff, 0x20334d, 2.15));
      const key = new THREE.DirectionalLight(0xffe3b7,3.05);key.position.set(-3.5,6.5,7);scene.add(key);
      const fill = new THREE.DirectionalLight(0x8baecf,1.7);fill.position.set(4,-1,4);scene.add(fill);
      const rim = new THREE.DirectionalLight(0xf3c77b,1.3);rim.position.set(4,4,-4);scene.add(rim);
      // Discrete lighting palette gives the sculpture hard American comic-book shadow masses.
      const rampCanvas = document.createElement('canvas');rampCanvas.width=5;rampCanvas.height=1;
      const g = rampCanvas.getContext('2d');
      ['#3a4656','#7d8690','#aeb4b9','#e2e4e3','#fff8e8'].forEach((v,i)=>{g.fillStyle=v;g.fillRect(i,0,1,1)});
      const ramp = new THREE.CanvasTexture(rampCanvas); ramp.magFilter=THREE.NearestFilter;ramp.minFilter=THREE.NearestFilter;textures.add(ramp);
      const marble = new THREE.MeshToonMaterial({color:0xf0ede5,gradientMap:ramp});materials.add(marble);
      const shade = new THREE.MeshToonMaterial({color:0xbec4c9,gradientMap:ramp});materials.add(shade);
      const dark = new THREE.MeshBasicMaterial({color:0x34435a});materials.add(dark);
      const gold = new THREE.MeshToonMaterial({color:0xeebd64,emissive:0x58330d,emissiveIntensity:.16});materials.add(gold);
      const goldHighlight = new THREE.MeshBasicMaterial({color:0xffedb9});materials.add(goldHighlight);
      const ink = new THREE.MeshBasicMaterial({color:0x111a2c,side:THREE.BackSide});materials.add(ink);
      const statue = new THREE.Group();world.add(statue);
      function addMesh(geo,mat,parent=statue,outline=.027){
        geometries.add(geo);const mesh=new THREE.Mesh(geo,mat);parent.add(mesh);
        if(outline){const line=new THREE.Mesh(geo,ink);line.scale.setScalar(1+outline);mesh.add(line)}
        return mesh;
      }
      function ellipsoid(x,y,z,sx,sy,sz,mat=marble,parent=statue,outline=.03){
        const m=addMesh(new THREE.SphereGeometry(1,24,16),mat,parent,outline);
        m.position.set(x,y,z);m.scale.set(sx,sy,sz);return m;
      }
      function tube(points,radius,mat=marble,parent=statue,segments=56,outline=.015){
        const curve = new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)));
        return addMesh(new THREE.TubeGeometry(curve,segments,radius,8,false),mat,parent,outline);
      }
      // Marble bust: shoulders, classical carved drapery and raised forearm.
      ellipsoid(-.22,-1.86,-.1,1.37,.86,.68,marble);
      ellipsoid(-.4,-2.35,.28,1.10,.61,.57,shade);
      ellipsoid(-.22,-.98,-.05,.36,.58,.39,marble);
      // Folded asymmetrical Greek himation / tunic.
      for(let i=0;i<8;i++){
        const x=-1.12+i*.255;
        tube([[x,-1.33,.49],[x+.06,-1.75,.72],[x+.16,-2.26,.63]],.052+(i%3)*.009,i%3===0?shade:marble,statue,28,.008);
      }
      // Head profile, jaw, brows, nose, lips, incised stone eyes.
      const head = ellipsoid(-.35,.42,.10,.69,.90,.59,marble);
      ellipsoid(-.35,-.10,.22,.54,.38,.52,marble);
      ellipsoid(-.35,1.17,.05,.69,.30,.58,shade);
      ellipsoid(-.34,.25,.67,.13,.37,.20,marble); // carved nose
      ellipsoid(-.35,-.17,.67,.19,.055,.095,shade);
      for(const side of [-1,1]){
        ellipsoid(-.35+side*.31,.43,.58,.23,.09,.06,shade);
        ellipsoid(-.35+side*.31,.43,.635,.13,.031,.03,dark,statue,0);
        ellipsoid(-.35+side*.65,.30,.03,.14,.23,.16,marble);
      }
      // Greek hair sculpted as large flowing S-shaped stone locks.
      ellipsoid(-.35,1.13,.01,.72,.34,.57,marble);
      const hairPaths=[];
      for(let i=0;i<11;i++){
        const a=i/10*Math.PI;
        const x=-.35+.68*Math.cos(a);
        const z=.17+.38*Math.sin(a);
        const len=.67+(i%4)*.17;
        hairPaths.push([[x,1.14,z],[x+Math.sin(i*2)*.11,.77,z+.06],[x+Math.sin(i*1.9)*.13,.28-len*.14,z+.08],[x+.12,-.05-len*.29,z-.03]]);
      }
      hairPaths.forEach((p,i)=>tube(p,.085+(i%3)*.012,i%4===0?shade:marble,statue,42,.009));
      // Circlet and Greek-inspired laurel leaves.
      tube([[-.99,1.17,.33],[-.78,1.38,.48],[-.38,1.45,.53],[.02,1.39,.44],[.32,1.16,.2]],.035,gold,statue,48,.006);
      for(let i=0;i<7;i++){
        const a=i/6*Math.PI;
        const leaf=ellipsoid(-.38+.65*Math.cos(a),1.41+.055*Math.sin(a),.46,.085,.032,.033,gold,statue,0);
        leaf.rotation.z=a-.6;
      }
      // Raised right arm and sculpted palm support the golden ball of thread.
      ellipsoid(.71,-1.60,.35,.34,.34,.39,marble);
      tube([[.61,-1.59,.30],[1.07,-1.10,.50],[1.53,-.40,.88],[1.69,.06,1.05]],.175,marble,statue,56,.022);
      ellipsoid(1.73,.19,1.04,.24,.21,.19,marble);
      for(let i=0;i<4;i++)tube([[1.61+i*.085,.22,1.15],[1.62+i*.088,.39,1.18],[1.55+i*.08,.46,1.05]],.041,marble,statue,18,.01);
      const yarnGroup = new THREE.Group();yarnGroup.position.set(1.67,.66,1.08);world.add(yarnGroup);
      const ball=ellipsoid(0,0,0,.37,.37,.37,gold,yarnGroup,.02);
      ball.scale.set(.36,.36,.36);
      // Interwoven visibly 3D spun thread around the sphere.
      for(let j=0;j<11;j++){
        const pts=[],phase=j*2.399;
        for(let i=0;i<=96;i++){
          const t=i/96*Math.PI*2,rad=.395+.017*Math.sin(5*t+phase);
          pts.push(new THREE.Vector3(rad*Math.cos(t)*Math.cos(phase)+.04*Math.sin(t*2),rad*Math.sin(t),rad*Math.cos(t)*Math.sin(phase)));
        }
        const c=new THREE.CatmullRomCurve3(pts,true);
        addMesh(new THREE.TubeGeometry(c,110,.011,5,true),j%4===0?goldHighlight:gold,yarnGroup,0);
      }
      // Thread trails from the ball into the domain / graph visual language.
      const trail=new THREE.CatmullRomCurve3([
        [1.91,.87,1.08],[2.33,1.22,1.10],[2.56,.64,.65],[2.05,.05,.32],
        [1.76,-.6,.35],[2.2,-1.04,.62],[2.94,-.95,.41],[3.23,-.35,.1]
      ].map(p=>new THREE.Vector3(...p)));
      const thread=addMesh(new THREE.TubeGeometry(trail,180,.024,8,false),gold,world,.013);
      const sparks=[];
      const sparkGeo=new THREE.OctahedronGeometry(.047,0);geometries.add(sparkGeo);
      for(let i=0;i<9;i++){
        const s=new THREE.Mesh(sparkGeo,goldHighlight);world.add(s);sparks.push(s);
      }
      // Antique stepped display plinth and unobtrusive halo.
      const base=addMesh(new THREE.CylinderGeometry(1.22,1.39,.29,10),shade,statue,.012);
      base.position.set(-.2,-2.65,-.16);
      const halo=addMesh(new THREE.TorusGeometry(1.94,.009,4,90),goldHighlight,world,0);
      halo.position.set(-.26,.05,-1.6);halo.rotation.y=.23;halo.material.transparent=true;halo.material.opacity=.28;
      // Unanimated mode still displays the complete 3D sculpture.
      let visible=true,last=0,time=0;
      function resize(){
        const w=stage.clientWidth,h=stage.clientHeight;if(w<2||h<2)return;
        camera.aspect=w/h;
        camera.position.z=w<480?15.5:w<740?13.5:11.7;
        camera.updateProjectionMatrix();renderer.setSize(w,h,false);
      }
      resize();
      if('ResizeObserver'in window){resizeObserver=new ResizeObserver(resize);resizeObserver.observe(stage)}else{window.addEventListener('resize',resize);cleanups.push(()=>window.removeEventListener('resize',resize))}
      if('IntersectionObserver'in window){observer=new IntersectionObserver(e=>{visible=e[0]?.isIntersecting??true});observer.observe(stage)}
      function frame(t){if(destroyed)return;frameId=requestAnimationFrame(frame);if(!visible||document.hidden){last=t;return}
        const dt=Math.min((t-last||16)/1000,.04);time+=dt;last=t;
        statue.rotation.y=Math.sin(time*.25)*.075-.08;
        statue.rotation.x=Math.sin(time*.17)*.015;
        yarnGroup.rotation.y=time*.24;yarnGroup.rotation.x=Math.sin(time*.35)*.16;
        for(let i=0;i<sparks.length;i++){
          const u=(time*.095+i/sparks.length)%1;
          sparks[i].position.copy(trail.getPoint(u));
          sparks[i].rotation.y=time+i;
          sparks[i].scale.setScalar(.65+.3*Math.sin(time*3+i));
        }
        renderer.render(scene,camera);
      }
      frameId=requestAnimationFrame(frame);
      stage.dataset.three='statue-live';
      function dispose(){if(destroyed)return;destroyed=true;cancelAnimationFrame(frameId);observer?.disconnect();resizeObserver?.disconnect();cleanups.forEach(fn=>fn());geometries.forEach(x=>x.dispose());materials.forEach(x=>x.dispose());textures.forEach(x=>x.dispose());renderer?.dispose();}
      window.addEventListener('pagehide',dispose,{once:true});
      reduceMotion.addEventListener('change',e=>{if(e.matches){dispose();stage.dataset.three='reduced'}},{once:true});
    }catch(error){
      stage.dataset.three='fallback';
      console.warn('.NEMA statue display fallback:',error);
      renderer?.dispose();
    }
  })();
}
