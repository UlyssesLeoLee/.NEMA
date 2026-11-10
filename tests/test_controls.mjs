import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const folder=new URL('../website/',import.meta.url);const src=name=>fs.readFileSync(new URL(name,folder),'utf8');
class Cls{constructor(){this.set=new Set()}add(k){this.set.add(k)}remove(k){this.set.delete(k)}contains(k){return this.set.has(k)}toggle(k){if(this.set.has(k)){this.set.delete(k);return false}this.set.add(k);return true}}
class El{constructor(id=''){this.id=id;this.listeners={};this.attrs={};this.classList=new Cls();this.textContent='';this.clicks=0}addEventListener(t,f){(this.listeners[t]??=[]).push(f)}fire(t='click'){this.clicks++;for(const fn of this.listeners[t]||[])fn({target:this,preventDefault(){}})}setAttribute(k,v){this.attrs[k]=String(v)}getAttribute(k){return this.attrs[k]}append(){}remove(){}click(){this.fire('click')}}
const ids=['menuBtn','navLinks','motionToggle','stageState','stageFront','stageLeft','stageRight','stageReset','stageCapture'];const nodes=new Map(ids.map(k=>[k,new El(k)]));
const body=new El('body');let downloads=0;const doc={body,getElementById:id=>nodes.get(id)||null,querySelectorAll:q=>q.includes('stage-control[data-view]')?[nodes.get('stageFront'),nodes.get('stageLeft'),nodes.get('stageRight')]:[],createElement:()=>{const a=new El();a.click=()=>{downloads++};return a}};
const win={addEventListener(){}};const context={window:win,document:doc,matchMedia:()=>({matches:false}),performance:{now:()=>1000},navigator:{},Math,console};
vm.runInNewContext(src('js/sculpture-motion.js'),context);
const calls=[];win.NEMA_STATUE={ready:true,mode:'native-webgl',turn:v=>calls.push(['turn',v]),reset:()=>calls.push(['reset']),pause:v=>calls.push(['pause',v]),screenshot:()=> 'data:image/png;base64,AAA'};
vm.runInNewContext(src('premier.js'),context);
vm.runInNewContext(src('js/sculpture-buttons.js'),context);
nodes.get('menuBtn').fire();assert(nodes.get('navLinks').classList.contains('open'));assert.equal(nodes.get('menuBtn').getAttribute('aria-expanded'),'true');
nodes.get('stageLeft').fire();assert.equal(calls.at(-1)[0],'turn');assert.equal(calls.at(-1)[1],-Math.PI/2);assert.equal(nodes.get('stageLeft').attrs['aria-pressed'],'true');
nodes.get('stageRight').fire();assert.equal(calls.at(-1)[1],Math.PI/2);assert.equal(nodes.get('stageLeft').attrs['aria-pressed'],'false');
nodes.get('stageFront').fire();assert.equal(calls.at(-1)[1],0);
nodes.get('stageReset').fire();assert.equal(calls.at(-1)[0],'reset');
nodes.get('motionToggle').fire();assert(body.classList.contains('motion-off'));assert.equal(win.NEMAMotion.paused,true);assert.equal(nodes.get('motionToggle').attrs['aria-pressed'],'true');
nodes.get('motionToggle').fire();assert(!body.classList.contains('motion-off'));assert.equal(win.NEMAMotion.paused,false);
nodes.get('stageCapture').fire();assert.equal(downloads,1);
win.NEMA_STATUE.ready=false;nodes.get('stageCapture').fire();assert.equal(downloads,1,'do not download an empty screenshot while GLB is loading');
console.log('PASS mobile menu, front/left/right, view reset, pause/resume, capture, loading failure notices');
