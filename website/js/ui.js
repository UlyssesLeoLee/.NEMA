/* Shared user-facing action feedback and clipboard fallback for local-http websites. */
(()=>{'use strict';
let toast=null,timer=null;
function notify(text){if(!toast){toast=document.createElement('div');toast.className='ui-toast';toast.setAttribute('role','status');toast.setAttribute('aria-live','polite');document.body.append(toast)}toast.textContent=text;toast.classList.add('show');clearTimeout(timer);timer=setTimeout(()=>toast.classList.remove('show'),2600)}
async function copy(text){try{if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(text);notify('已复制到剪贴板');return true}}catch{}
 const temp=document.createElement('textarea');temp.value=text;temp.setAttribute('readonly','');temp.style.cssText='position:fixed;opacity:0;left:-10000px;top:0';document.body.append(temp);temp.select();let ok=false;try{ok=document.execCommand('copy')}catch{}temp.remove();notify(ok?'已复制到剪贴板':'当前浏览器禁止复制，请在源码区手动复制');return ok}
function download(name,text,mime='text/plain'){const url=URL.createObjectURL(new Blob([text],{type:mime+';charset=utf-8'}));const link=document.createElement('a');link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1200);notify('已准备下载 '+name)}
window.NEMA_UI={notify,copy,download};
})();
