'use strict';
const themeButton=document.querySelector('#theme');
let theme='system';try{const stored=localStorage.getItem('haal-theme');if(['system','dark','light'].includes(stored))theme=stored;}catch{}
function applyTheme(){if(theme==='system')document.documentElement.removeAttribute('data-theme');else document.documentElement.dataset.theme=theme;themeButton.textContent='Theme: '+theme;}
themeButton.addEventListener('click',()=>{theme=theme==='system'?'dark':theme==='dark'?'light':'system';applyTheme();try{localStorage.setItem('haal-theme',theme);}catch{}});applyTheme();
const search=document.querySelector('#search');
if(search)search.addEventListener('input',()=>{const q=search.value.toLowerCase().trim();let count=0;document.querySelectorAll('.entry').forEach(e=>{e.hidden=!e.textContent.toLowerCase().includes(q);if(!e.hidden)count++;});document.querySelector('#result-count').textContent=count+' matching entries';});

