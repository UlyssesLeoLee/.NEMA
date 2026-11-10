/* Accessible controls for either renderer; methods are swapped after Three.js upgrade. */
(()=>{'use strict';
const status=document.getElementById('stageState');
function tell(msg){if(status)status.textContent=msg}
function act(fn,description){const model=window.NEMA_STATUE;if(!model||model.ready===false){tell('模型仍在加载中，请完成加载后重试');return}try{fn(model);tell(description+' · '+(window.NEMAMotion?.status||''))}catch(e){tell('操作失败：'+e.message)}}
for(const [id,angle,desc] of [['stageFront',0,'正面视角'],['stageLeft',-Math.PI/2,'左侧视角'],['stageRight',Math.PI/2,'右侧视角']])document.getElementById(id)?.addEventListener('click',()=>{act(model=>model.turn(angle),desc);for(const button of document.querySelectorAll('.stage-control[data-view]'))button.setAttribute('aria-pressed',String(button.id===id))});
document.getElementById('stageReset')?.addEventListener('click',()=>{act(model=>model.reset(),'已复位，稍后继续自动旋转');for(const button of document.querySelectorAll('.stage-control[data-view]'))button.setAttribute('aria-pressed','false')});
document.getElementById('stageCapture')?.addEventListener('click',()=>act(model=>{const uri=model.screenshot();if(!uri||!uri.startsWith('data:image/png'))throw Error('画面尚不可保存');const a=document.createElement('a');a.href=uri;a.download='nema-ariadne-3d-view.png';document.body.append(a);a.click();a.remove()},'已生成 PNG 截图'));
document.getElementById('motionToggle')?.addEventListener('click',()=>{window.NEMAMotion?.pause(document.body.classList.contains('motion-off'));window.NEMA_STATUE?.pause?.(document.body.classList.contains('motion-off')); tell(window.NEMAMotion?.status||'动画状态已切换')});
window.addEventListener('nema-statue-ready',()=>tell((window.NEMA_STATUE?.mode||'3D')+' · '+(window.NEMAMotion?.status||'自动旋转中')));
})();
