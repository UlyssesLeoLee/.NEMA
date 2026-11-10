/* .NEMA • Three.js Real 3D Cel-Shading (三渲二) Production Engine
 * Renders the bundled ariadne-relief-3d.glb with classical Greek comic cel-shading:
 * - 3-tier stepped toon diffuse lighting (Toon ramp: shadow / midtone / full lit)
 * - Stylized sacred gold materials with high metalness, mirror specular & emissive glow
 * - Dynamic Ariadne Catmull-Rom living golden spark comet
 * - Concentric 3D astronomical armillary rings with Greek zodiac markers
 * - Floating temple stardust particle cloud
 * - Interactive OrbitControls with smooth inertia, perspective snapping & PNG export
 */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

(async () => {
  'use strict';
  const host = document.getElementById('ariadneStatue3d');
  if (!host) return;
  const stage = host.querySelector('.sculpture-viewport');
  const label = document.getElementById('stageState');

  // 1. Create standard Three.js 3-tier stepped toon ramp texture (RedFormat)
  function createToonRampTexture(levels = 3) {
    const data = new Uint8Array(levels);
    for (let i = 0; i < levels; i++) {
      data[i] = Math.round((i / (levels - 1)) * 255);
    }
    const texture = new THREE.DataTexture(data, levels, 1, THREE.RedFormat);
    texture.minFilter = THREE.NearestFilter;
    texture.magFilter = THREE.NearestFilter;
    texture.generateMipmaps = false;
    texture.needsUpdate = true;
    return texture;
  }

  const toonRamp = createToonRampTexture(3);

  // 2. Initialize Three.js Scene, Camera, and WebGLRenderer
  const scene = new THREE.Scene();
  window.NEMA_SCENE = scene;
  const camera = new THREE.OrthographicCamera(-3.58, 3.58, 3.58, -3.58, 0.1, 100);
  camera.position.set(0, 0.06, 13);
  camera.lookAt(0, 0.04, 0);

  const renderer = new THREE.WebGLRenderer({
    alpha: true,
    antialias: true,
    powerPreference: 'high-performance',
    preserveDrawingBuffer: true
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2.0));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.25;
  renderer.setClearColor(0x000000, 0);

  // Stop 2D canvas fallback if running
  const priorStatue = window.NEMA_STATUE;
  if (priorStatue && priorStatue.stop) priorStatue.stop();

  renderer.domElement.className = 'sculpture-canvas three is-cel-3d';
  renderer.domElement.setAttribute('aria-label', '3D 阿里阿德涅克里特浮雕雕塑 · 古希腊美漫三渲二交互场景');
  stage.replaceChildren(renderer.domElement);
  host.classList.add('is-live', 'is-three');

  // 3. Dramatic Greek Comic Lighting (美漫戏剧光照)
  // Warm Apollo Key Light
  const warmKey = new THREE.DirectionalLight(0xfff0db, 2.4);
  warmKey.position.set(-3.2, 5.0, 7.5);
  scene.add(warmKey);

  // Cool Aegean Rim/Accent Light
  const coolRim = new THREE.DirectionalLight(0x7ac4f0, 1.8);
  coolRim.position.set(4.2, -1.2, -5.5);
  scene.add(coolRim);

  // Temple Floor Bounce Fill
  const floorFill = new THREE.DirectionalLight(0xe8dec8, 0.7);
  floorFill.position.set(0, -4, 3);
  scene.add(floorFill);

  // Atmosphere Ambient
  const hemi = new THREE.HemisphereLight(0xfffaee, 0x182c40, 1.3);
  scene.add(hemi);

  // 4. Load Real 3D GLB Model
  const loader = new GLTFLoader();
  let asset;
  try {
    asset = await loader.loadAsync('assets/ariadne-relief-3d.glb');
  } catch (loadErr) {
    console.warn('GLB load failed in Three.js:', loadErr);
    return;
  }

  const pivot = new THREE.Group();
  const hero = asset.scene;
  hero.scale.set(1, 1, 1);
  pivot.add(hero);
  scene.add(pivot);

  // 5. Apply Cel-Shading Materials and Gold Stylization
  hero.traverse(o => {
    if (!o.isMesh) return;
    if (o.geometry) {
      o.geometry.computeVertexNormals();
    }
    const part = o.name || '';

    // A. Front Relief Sculpt: Comic Toon Material with Step-Lighting
    if (part === 'sculpture_front') {
      const origMap = o.material && o.material.map;
      if (origMap) {
        origMap.wrapT = THREE.RepeatWrapping;
        origMap.repeat.y = -1;
        origMap.offset.y = 1;
        origMap.needsUpdate = true;
      }
      o.material = new THREE.MeshToonMaterial({
        map: origMap || null,
        gradientMap: toonRamp,
        color: 0xffffff
      });
    }
    // B. Relief Back & Marble Edges: Cel-Shaded Pentelic Marble
    else if (part === 'sculpture_back' || part === 'side_marble') {
      o.material = new THREE.MeshToonMaterial({
        color: part === 'sculpture_back' ? 0xe2dac9 : 0xc7bba9,
        gradientMap: toonRamp
      });
    }
    // C. Golden Orb, Golden Thread & Coils: Lustrous Sacred Gold
    else if (part === 'gold_orb' || part === 'gold_thread' || part.startsWith('skein_')) {
      o.material = new THREE.MeshStandardMaterial({
        color: 0xf5cf62,
        roughness: 0.18,
        metalness: 0.95,
        emissive: 0xd4af37,
        emissiveIntensity: 0.36
      });
    }
  });

  // 6. Concentric 3D Astronomical Armillary Rings (神圣天球浑天仪 3D 动态环带)
  const armillary = new THREE.Group();
  pivot.add(armillary);

  const ringGoldMat = new THREE.MeshStandardMaterial({
    color: 0xe6bd48,
    roughness: 0.25,
    metalness: 0.85,
    emissive: 0x94721a,
    emissiveIntensity: 0.22
  });

  // Outer Zodiac Ring (tilted at 23.5° celestial obliquity)
  const outerRingGeom = new THREE.TorusGeometry(3.32, 0.018, 16, 120);
  const outerRing = new THREE.Mesh(outerRingGeom, ringGoldMat);
  outerRing.rotation.x = 0.41; // 23.5 degrees
  armillary.add(outerRing);

  // 12 Greek Zodiac / Cardinal Astrolabe Markers along the outer ring
  const markerGeom = new THREE.OctahedronGeometry(0.048, 0);
  const markerMat = new THREE.MeshBasicMaterial({ color: 0xfff0ad });
  for (let i = 0; i < 12; i++) {
    const angle = (i / 12) * Math.PI * 2;
    const marker = new THREE.Mesh(markerGeom, markerMat);
    marker.position.set(Math.cos(angle) * 3.32, Math.sin(angle) * 3.32, 0);
    outerRing.add(marker);
  }

  // Equator Ring (elegantly inclined to form an astronomical armillary ellipse)
  const equatorRingGeom = new THREE.TorusGeometry(3.14, 0.012, 12, 96);
  const equatorRing = new THREE.Mesh(equatorRingGeom, ringGoldMat);
  equatorRing.rotation.set(Math.PI * 0.42, 0, 0.22);
  armillary.add(equatorRing);

  // Meridian Ring (inclined armillary coordinate ring)
  const meridianRingGeom = new THREE.TorusGeometry(3.22, 0.012, 12, 96);
  const meridianRing = new THREE.Mesh(meridianRingGeom, ringGoldMat);
  meridianRing.rotation.set(0.18, Math.PI * 0.38, 0);
  armillary.add(meridianRing);

  // 7. Animated Ariadne Catmull-Rom Golden Thread Spark (灵动流光彗尾)
  const threadWaypoints = [
    [-0.65, -2.42, 0.85],
    [-1.25, -1.90, 0.85],
    [-0.80, -1.10, 0.78],
    [ 0.60, -0.15, 0.70],
    [ 1.17,  1.05, 0.74],
    [ 1.15,  2.43, 0.90]
  ].map(v => new THREE.Vector3(...v));

  const threadCurve = new THREE.CatmullRomCurve3(threadWaypoints);

  const sparkGroup = new THREE.Group();
  const sparkCore = new THREE.Mesh(
    new THREE.SphereGeometry(0.056, 16, 16),
    new THREE.MeshBasicMaterial({ color: 0xfff8d6 })
  );
  sparkGroup.add(sparkCore);

  const sparkHalo = new THREE.Mesh(
    new THREE.TorusGeometry(0.095, 0.014, 12, 32),
    new THREE.MeshBasicMaterial({ color: 0xf5cf62 })
  );
  sparkHalo.rotation.x = Math.PI * 0.35;
  sparkGroup.add(sparkHalo);

  // 3 trailing comet sparks
  const tailSparks = [];
  for (let i = 0; i < 3; i++) {
    const s = new THREE.Mesh(
      new THREE.SphereGeometry(0.034 - i * 0.007, 12, 12),
      new THREE.MeshBasicMaterial({ color: 0xf0c74b, transparent: true, opacity: 0.8 - i * 0.24 })
    );
    scene.add(s);
    tailSparks.push(s);
  }
  scene.add(sparkGroup);

  // 8. Floating Temple Stardust Particles (神庙浮游金尘粒子)
  const particleCount = 80;
  const particlePositions = new Float32Array(particleCount * 3);
  const particlePhases = new Float32Array(particleCount);

  for (let i = 0; i < particleCount; i++) {
    const radius = 1.2 + Math.random() * 2.3;
    const theta = Math.random() * Math.PI * 2;
    const y = (Math.random() - 0.5) * 5.2;
    particlePositions[i * 3 + 0] = Math.cos(theta) * radius;
    particlePositions[i * 3 + 1] = y;
    particlePositions[i * 3 + 2] = Math.sin(theta) * radius;
    particlePhases[i] = Math.random() * Math.PI * 2;
  }

  const particleGeom = new THREE.BufferGeometry();
  particleGeom.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
  const particleMat = new THREE.PointsMaterial({
    color: 0xf5d378,
    size: 0.055,
    transparent: true,
    opacity: 0.75
  });
  const stardust = new THREE.Points(particleGeom, particleMat);
  pivot.add(stardust);

  // 9. OrbitControls Setup with Damping & Constraints
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.055;
  controls.enablePan = false;
  controls.minZoom = 0.75;
  controls.maxZoom = 1.6;
  controls.minAzimuthAngle = -1.1;
  controls.maxAzimuthAngle = 1.1;
  controls.minPolarAngle = Math.PI / 2 - 0.35;
  controls.maxPolarAngle = Math.PI / 2 + 0.35;
  controls.target.set(0, 0.04, 0);
  controls.update();

  const motion = window.NEMAMotion;
  controls.addEventListener('start', () => motion?.interaction(true));
  controls.addEventListener('end', () => motion?.interaction(false));

  // 10. Viewport Resizing
  function getStageSize() {
    const r = stage.getBoundingClientRect();
    return {
      w: Math.max(2, Math.round(r.width)),
      h: Math.max(2, Math.round(r.height))
    };
  }

  let lastSize = '';
  function resize() {
    const { w, h } = getStageSize();
    const key = w + 'x' + h;
    if (key === lastSize) return;
    lastSize = key;
    renderer.setSize(w, h, false);
    const aspect = w / h;
    const baseSize = 3.58;
    camera.left = -baseSize * aspect;
    camera.right = baseSize * aspect;
    camera.top = baseSize;
    camera.bottom = -baseSize;
    camera.updateProjectionMatrix();
  }
  resize();

  // 11. Visibility & Intersection Observer
  let visible = true;
  const observer = new IntersectionObserver(entries => {
    visible = entries[0].isIntersecting;
    motion?.setVisible(visible);
  });
  observer.observe(host);

  // 12. Public Statue API
  const api = {
    ready: true,
    mode: 'threejs-cel-3d',
    turn(rad) {
      motion?.setAngle(rad);
      controls.reset();
    },
    reset() {
      motion?.reset();
      controls.reset();
    },
    pause(val) {
      motion?.pause(val);
    },
    screenshot() {
      return renderer.domElement.toDataURL('image/png');
    },
    get angle() {
      return motion?.angle || 0;
    },
    stop() {
      observer.disconnect();
      controls.dispose();
      renderer.dispose();
    }
  };

  window.NEMA_STATUE = api;
  window.NEMA_THREE = api;

  if (label) {
    label.textContent = 'Three.js 3D 美漫三渲二 · 阿里阿德涅 · ' + (motion?.status || '自动旋转中');
  }
  window.dispatchEvent(new Event('nema-statue-ready'));

  // 13. Render Animation Loop
  function frame(now) {
    requestAnimationFrame(frame);
    if (!visible) return;
    resize();

    const isMoving = !motion?.paused && !motion?.reduced && !document.body.classList.contains('motion-off');
    const angle = motion ? motion.tick(now) : 0;
    pivot.rotation.y = angle;

    if (isMoving) {
      // Counter-rotate the outer zodiac ring for rich astronomical celestial motion
      outerRing.rotation.z = -now * 0.0003;
      equatorRing.rotation.z = now * 0.00015;

      // Spark comet traveling along Ariadne's golden thread
      const t = (now * 0.00012) % 1;
      const sparkPos = threadCurve.getPoint(t);
      sparkGroup.position.copy(sparkPos);
      sparkHalo.rotation.z = now * 0.004;

      // Trailing tail sparks
      for (let i = 0; i < tailSparks.length; i++) {
        const tTail = (t - (i + 1) * 0.025 + 1) % 1;
        tailSparks[i].position.copy(threadCurve.getPoint(tTail));
        tailSparks[i].visible = true;
      }

      // Gentle stardust particle floating motion
      const posAttr = particleGeom.attributes.position;
      for (let i = 0; i < particleCount; i++) {
        const origY = particlePositions[i * 3 + 1];
        posAttr.setY(i, origY + Math.sin(now * 0.0015 + particlePhases[i]) * 0.12);
      }
      posAttr.needsUpdate = true;
    } else {
      for (let i = 0; i < tailSparks.length; i++) {
        tailSparks[i].visible = false;
      }
    }

    controls.update();
    renderer.render(scene, camera);
  }

  requestAnimationFrame(frame);
})();
