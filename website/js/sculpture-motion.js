/* Shared deterministic motion timeline used by BOTH Three.js and offline WebGL2.
 * The default is a full 360-degree rotation every 24 seconds, not a 3-degree sway.
 * Manual view/drag temporarily holds the view, then resumes automatically. */
(function(root){'use strict';
 const TWO_PI=Math.PI*2,PERIOD=24000,HOLD_MS=5000;
 const reduce=typeof matchMedia==='function'&&matchMedia('(prefers-reduced-motion: reduce)').matches;
 let angle=0,last=null,paused=reduce,visible=true,holdUntil=0,manual=false;
 function wrap(v){return ((v%TWO_PI)+TWO_PI)%TWO_PI}
 const api={
  tick(now){if(last===null){last=now;return angle}const dt=Math.min(100,Math.max(0,now-last));last=now;if(!paused&&visible&&now>=holdUntil&&!manual)angle=wrap(angle+dt*TWO_PI/PERIOD);return angle},
  setAngle(v,hold=HOLD_MS){angle=wrap(v);holdUntil=hold>0?(typeof performance!=='undefined'?performance.now():last||0)+hold:0;return angle},
  interaction(active){manual=!!active;if(!manual)holdUntil=(typeof performance!=='undefined'?performance.now():last||0)+HOLD_MS},
  nudge(dx){angle=wrap(angle+dx);holdUntil=(typeof performance!=='undefined'?performance.now():last||0)+HOLD_MS},
  pause(value){paused=!!value;last=null},
  setVisible(value){visible=!!value;last=null},
  reset(){angle=0;manual=false;holdUntil=(typeof performance!=='undefined'?performance.now():last||0)+2500;last=null},
  get angle(){return angle},get paused(){return paused},get reduced(){return reduce},get period(){return PERIOD},get visible(){return visible},
  get status(){return paused?(reduce?'系统减少动画：静止 · 点击恢复可覆盖':'已暂停 · 点击恢复动画'):'自动旋转中 · 24 秒 / 周'}
 };
 root.NEMAMotion=api;
 if(reduce&&typeof document!=='undefined'){document.body.classList.add('motion-off');const b=document.getElementById('motionToggle');if(b){b.textContent='恢复动画 ▶';b.setAttribute('aria-pressed','true');}}
})(typeof window!=='undefined'?window:globalThis);
