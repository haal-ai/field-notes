'use strict';
const themeButton=document.querySelector('#theme');
let theme='system';try{const stored=localStorage.getItem('haal-theme');if(['system','dark','light'].includes(stored))theme=stored;}catch{}
function applyTheme(){if(theme==='system')document.documentElement.removeAttribute('data-theme');else document.documentElement.dataset.theme=theme;themeButton.textContent='Theme: '+theme;}
themeButton.addEventListener('click',()=>{theme=theme==='system'?'dark':theme==='dark'?'light':'system';applyTheme();try{localStorage.setItem('haal-theme',theme);}catch{}});applyTheme();
const $=id=>document.getElementById(id);
const rows=[...document.querySelectorAll('#entries .entry')];
if(rows.length){
  const state={kind:'all',query:'',archive:false};
  const setActive=(sel,attr,val)=>document.querySelectorAll(sel).forEach(b=>{const on=b.getAttribute(attr)===val;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});
  const side=document.querySelectorAll('.side-articles li');
  function render(){
    let n=0;
    rows.forEach(e=>{
      const show=(state.kind==='all'||e.dataset.kind===state.kind)&&(state.archive||e.dataset.outdated!=='true')&&e.textContent.toLowerCase().includes(state.query);
      e.hidden=!show;if(show)n++;
    });
    side.forEach(li=>{const r=rows.find(e=>e.dataset.slug===li.dataset.slug);li.hidden=!r||r.hidden;});
    document.querySelectorAll('.side-group').forEach(g=>{g.hidden=!g.querySelector('li:not([hidden])');});
    document.querySelectorAll('#entries .entry-section').forEach(s=>{s.hidden=!s.querySelector('.entry:not([hidden])');});
    const filtered=state.kind!=='all'||state.query!=='';
    const pad=x=>String(x).padStart(2,'0'),inScope=e=>state.archive||e.dataset.outdated!=='true';
    const label=(shown,total)=>filtered?shown+' of '+total:pad(total);
    const secOf=e=>e.closest('.entry-section').dataset.section;
    document.querySelectorAll('#entries .entry-section').forEach(sec=>{
      const all=[...sec.querySelectorAll('.entry')].filter(inScope);
      const t=label(all.filter(e=>!e.hidden).length,all.length);
      sec.querySelector('.section-count').textContent=t;
      const g=document.querySelector('.side-group[data-section="'+sec.dataset.section+'"] .side-count');if(g)g.textContent=t;
    });
    const total=rows.filter(inScope).length,allCount=document.querySelector('.side-all .side-count');
    if(allCount)allCount.textContent=label(n,total);
    $('result-count').textContent=n+(n===1?' entry':' entries');
    $('empty').hidden=n!==0;
    setActive('.type-button','data-kind',state.kind);
  }
  document.addEventListener('click',e=>{
    const k=e.target.closest('[data-kind]');if(k&&k.tagName==='BUTTON'){state.kind=k.dataset.kind;render();}
  });
  $('search').addEventListener('input',e=>{state.query=e.target.value.toLowerCase().trim();render();});
  $('archive').addEventListener('change',e=>{state.archive=e.target.checked;render();});
  render();
}
const sideBox=document.querySelector('.side-sections');
const narrow=()=>matchMedia('(max-width:760px)').matches;
if(sideBox&&narrow()){sideBox.removeAttribute('open');
  // Close before the browser scrolls, so the heading lands near the top.
  sideBox.addEventListener('click',e=>{if(e.target.closest('a'))sideBox.removeAttribute('open');});}
function markSection(){document.querySelectorAll('.side-section').forEach(a=>{if(a.getAttribute('href')===location.hash)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');});}
addEventListener('hashchange',markSection);markSection();
