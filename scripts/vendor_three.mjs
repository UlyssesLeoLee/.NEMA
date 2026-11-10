import {cp,copyFile,mkdir,readFile,writeFile,access} from 'node:fs/promises';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
const repo=fileURLToPath(new URL('../',import.meta.url));
const base=join(repo,'node_modules','three');
try{await access(join(base,'build','three.module.js'))}catch{throw Error('先运行 npm install，再执行 npm run bundle:offline')}
const target=join(repo,'website','vendor','three');
await mkdir(join(target,'build'),{recursive:true});
for(const n of ['three.module.js','three.core.js'])await copyFile(join(base,'build',n),join(target,'build',n));
const neededAddons=[
  ['controls','OrbitControls.js'],
  ['loaders','GLTFLoader.js'],
  ['utils','BufferGeometryUtils.js']
];
for(const [dir,file] of neededAddons){
  await mkdir(join(target,'addons',dir),{recursive:true});
  await copyFile(join(base,'examples','jsm',dir,file),join(target,'addons',dir,file));
}
const website=join(repo,'website','index.html');
let html=await readFile(website,'utf8');
html=html.replaceAll('https://cdn.jsdelivr.net/npm/three@0.171.0/build/three.module.js','./vendor/three/build/three.module.js');
html=html.replaceAll('https://cdn.jsdelivr.net/npm/three@0.171.0/examples/jsm/','./vendor/three/addons/');
await writeFile(website,html);
const script=join(repo,'website','js','sculpture-three.js');
let js=await readFile(script,'utf8');
js=js.replaceAll('https://cdn.jsdelivr.net/npm/three@0.171.0/build/three.module.js','../vendor/three/build/three.module.js');
js=js.replaceAll('https://cdn.jsdelivr.net/npm/three@0.171.0/examples/jsm/','../vendor/three/addons/');
await writeFile(script,js);
console.log('Three.js 已复制到 website/vendor/three；现在可完全离线用 Three.js + GLTFLoader 渲染本地 GLB。');
