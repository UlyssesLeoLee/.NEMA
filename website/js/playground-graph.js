/* Workbench: all five graph types share one source-driven visualization. */
(()=>{'use strict';const svg=document.getElementById('liveNodeGraph'),source=document.getElementById('source'),legend=document.getElementById('graphLegend');if(!svg||!source)return;
const cases={
forward:' \\>3 1\nA LoginAPI Authentication\nB TokenStore SessionStorage\nA>X>B Reads VerifySession',
reverse:' \\>3 1\nA LoginAPI Authentication\nB TokenStore SessionStorage\nA<X<B Responds SessionReady',
undirected:' \\>3 1\nA LoginAPI Authentication\nB TokenStore SessionStorage\nA=U=B Shares SecurityPolicy',
loop:' \\>3 1\nA RetryWorker Executor\nA>P>A Retry Maximum3Attempts',
parallel:' \\>3 1\nA LoginAPI Authentication\nB TokenStore SessionStorage\nA>X>B Reads VerifySession\nA>Y>B Writes AuditLog\nB>Z>A Returns SessionReady'
};
function update(){try{window.NEMAGraph.render(svg,window.NemaStrict.parse(source.value),{info:legend,idPrefix:'workbench'})}catch(e){svg.replaceChildren();legend.textContent='解析错误：'+e.message;const t=document.createElementNS('http://www.w3.org/2000/svg','text');t.setAttribute('x','350');t.setAttribute('y','170');t.setAttribute('text-anchor','middle');t.setAttribute('fill','#f1a99d');t.textContent='请修正语法后重试';svg.append(t)}}
source.addEventListener('input',update);document.getElementById('parseNow')?.addEventListener('click',update);document.getElementById('sampleSelect')?.addEventListener('change',()=>setTimeout(update,0));
document.querySelectorAll('[data-graph-case]').forEach(btn=>btn.addEventListener('click',()=>{source.value=cases[btn.dataset.graphCase];source.dispatchEvent(new Event('input',{bubbles:true}));document.querySelectorAll('[data-graph-case]').forEach(b=>{b.classList.toggle('active',b===btn);b.setAttribute('aria-pressed',String(b===btn))});}));
update();
})();
