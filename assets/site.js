'use strict';
const T=JSON.parse(document.getElementById('i18n').textContent);
const themeButton=document.querySelector('#theme');
let theme='system';try{const stored=localStorage.getItem('haal-theme');if(['system','dark','light'].includes(stored))theme=stored;}catch{}
function applyTheme(){if(theme==='system')document.documentElement.removeAttribute('data-theme');else document.documentElement.dataset.theme=theme;themeButton.textContent=T.theme+' : '+T['theme_'+theme];}
themeButton.addEventListener('click',()=>{theme=theme==='system'?'dark':theme==='dark'?'light':'system';applyTheme();try{localStorage.setItem('haal-theme',theme);}catch{}});applyTheme();
const $=id=>document.getElementById(id);

// Home page: "Parcourir par section" cards by default; typing a query or picking a type filter
// switches to a flat list of matching notes across every section, each tagged with its section name.
const searchIndex=$('search-index');
if(searchIndex){
  const rows=[...searchIndex.querySelectorAll('.entry')];
  const cards=$('section-cards'),results=$('search-results'),filters=$('search-filters'),countEl=$('result-count');
  rows.forEach(r=>results.appendChild(r));
  const state={kind:'all',query:'',archive:false};
  const setActive=(sel,attr,val)=>document.querySelectorAll(sel).forEach(b=>{const on=b.getAttribute(attr)===val;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});
  function render(){
    const searching=state.kind!=='all'||state.query!=='';
    cards.hidden=searching;results.hidden=!searching;filters.hidden=!searching;countEl.hidden=!searching;
    if(!searching)return;
    let n=0;
    rows.forEach(e=>{
      const show=(state.kind==='all'||e.dataset.kind===state.kind)&&(state.archive||e.dataset.outdated!=='true')&&e.textContent.toLowerCase().includes(state.query);
      e.hidden=!show;if(show)n++;
    });
    countEl.textContent=T.notes_count[n===1?'one':'other'].replace('{n}',n);
    $('empty').hidden=n!==0;
    setActive('.type-button','data-kind',state.kind);
  }
  document.addEventListener('click',e=>{
    const k=e.target.closest('[data-kind]');if(k&&k.tagName==='BUTTON'){state.kind=k.dataset.kind;render();}
  });
  $('search').addEventListener('input',e=>{state.query=e.target.value.toLowerCase().trim();render();});
  const archive=$('archive');if(archive)archive.addEventListener('change',e=>{state.archive=e.target.checked;render();});
  render();
}

// Section pages: the same type filter and a search box, scoped to this section's own list (no JS: full list; works without it).
const sectionRows=document.querySelectorAll('#entries .entry');
if(sectionRows.length && !searchIndex){
  const rows=[...sectionRows];
  const state={kind:'all',query:''};
  const setActive=(sel,attr,val)=>document.querySelectorAll(sel).forEach(b=>{const on=b.getAttribute(attr)===val;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});
  function render(){
    let n=0;
    rows.forEach(e=>{
      const show=(state.kind==='all'||e.dataset.kind===state.kind)&&e.textContent.toLowerCase().includes(state.query);
      e.hidden=!show;if(show)n++;
    });
    $('empty').hidden=n!==0;
    setActive('.type-button','data-kind',state.kind);
  }
  document.addEventListener('click',e=>{
    const k=e.target.closest('[data-kind]');if(k&&k.tagName==='BUTTON'){state.kind=k.dataset.kind;render();}
  });
  const sectionSearch=$('section-search');
  if(sectionSearch)sectionSearch.addEventListener('input',e=>{state.query=e.target.value.toLowerCase().trim();render();});
}

const sideBox=document.querySelector('.side-sections');
const narrow=()=>matchMedia('(max-width:760px)').matches;
if(sideBox&&narrow()){sideBox.removeAttribute('open');
  // Close before the browser scrolls, so the heading lands near the top.
  sideBox.addEventListener('click',e=>{if(e.target.closest('a'))sideBox.removeAttribute('open');});}
function markSection(){document.querySelectorAll('.side-section').forEach(a=>{if(a.getAttribute('href')===location.hash)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');});}
addEventListener('hashchange',markSection);markSection();

// News page: theme chips + search, scoped to #news-list; day headings with no visible cards hide too.
const newsCards=document.querySelectorAll('#news-list .news-card');
if(newsCards.length){
  const cards=[...newsCards];
  const state={theme:'all',query:''};
  const setActive=(sel,attr,val)=>document.querySelectorAll(sel).forEach(b=>{const on=b.getAttribute(attr)===val;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});
  function render(){
    let n=0;
    cards.forEach(c=>{
      const show=(state.theme==='all'||c.dataset.theme===state.theme)&&c.textContent.toLowerCase().includes(state.query);
      c.hidden=!show;if(show)n++;
    });
    document.querySelectorAll('#news-list .news-day').forEach(day=>{day.hidden=!day.querySelector('.news-card:not([hidden])');});
    $('empty').hidden=n!==0;
    setActive('.news-chip','data-theme',state.theme);
  }
  document.addEventListener('click',e=>{
    const k=e.target.closest('[data-theme]');if(k&&k.tagName==='BUTTON'){state.theme=k.dataset.theme;render();}
  });
  const newsSearch=$('news-search');
  if(newsSearch)newsSearch.addEventListener('input',e=>{state.query=e.target.value.toLowerCase().trim();render();});
}
