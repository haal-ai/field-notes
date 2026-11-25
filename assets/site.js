'use strict';
const themeButton=document.querySelector('#theme');
let theme='system';try{const stored=localStorage.getItem('haal-theme');if(['system','dark','light'].includes(stored))theme=stored;}catch{}
function applyTheme(){if(theme==='system')document.documentElement.removeAttribute('data-theme');else document.documentElement.dataset.theme=theme;themeButton.textContent='Theme: '+theme;}
themeButton.addEventListener('click',()=>{theme=theme==='system'?'dark':theme==='dark'?'light':'system';applyTheme();try{localStorage.setItem('haal-theme',theme);}catch{}});applyTheme();
const $=id=>document.getElementById(id);
const rows=[...document.querySelectorAll('#entries .entry')];
if(rows.length){
  const state={topic:'all',kind:'all',query:'',archive:false};
  const setActive=(sel,attr,val)=>document.querySelectorAll(sel).forEach(b=>{const on=b.getAttribute(attr)===val;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});
  function render(){
    let n=0;
    rows.forEach(e=>{
      const show=(state.topic==='all'||e.dataset.topic===state.topic)&&(state.kind==='all'||e.dataset.kind===state.kind)&&(state.archive||e.dataset.outdated!=='true')&&e.textContent.toLowerCase().includes(state.query);
      e.hidden=!show;if(show)n++;
    });
    document.querySelectorAll('#entries .entry-section').forEach(s=>{s.hidden=!s.querySelector('.entry:not([hidden])');});
    $('result-count').textContent=n+(n===1?' entry':' entries');
    $('empty').hidden=n!==0;
    setActive('.topic-button','data-topic',state.topic);setActive('.type-button','data-kind',state.kind);
  }
  document.addEventListener('click',e=>{
    const t=e.target.closest('[data-topic]');if(t&&t.tagName==='BUTTON'){state.topic=t.dataset.topic;render();return;}
    const k=e.target.closest('[data-kind]');if(k&&k.tagName==='BUTTON'){state.kind=k.dataset.kind;render();}
  });
  $('search').addEventListener('input',e=>{state.query=e.target.value.toLowerCase().trim();render();});
  $('archive').addEventListener('change',e=>{state.archive=e.target.checked;render();});
  render();
}
