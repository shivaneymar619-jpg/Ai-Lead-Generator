"""FastAPI web server for the AI Lead Generation Agent."""
from __future__ import annotations
import asyncio
import json
import sys
import warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import urllib3
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from lead_gen_agent.pipeline import run_pipeline

app = FastAPI(title="AI Lead Generation Agent", version="1.0.0")
_executor = ThreadPoolExecutor(max_workers=4)

# ── Request model ────────────────────────────────────────────────────────────

class LeadRequest(BaseModel):
    business_description: str


# ── HTML ─────────────────────────────────────────────────────────────────────

_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>LeadGen AI — Where Leads Grow</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700;9..40,800&display=swap" rel="stylesheet">
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  :root{
    --bg:#f0ede8;--navy:#17122e;--navy2:#231b42;--lavender:#e8e2f7;
    --purple:#7c5cbf;--purple-light:#b09dd6;--text:#17122e;--muted:#6b6580;
    --white:#fff;--card-radius:16px;
  }
  html{scroll-behavior:smooth}
  body{font-family:'DM Sans',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}

  /* ── Layout ── */
  .wrap{max-width:1120px;margin:0 auto;padding:0 28px}

  /* ── Nav ── */
  nav{position:sticky;top:0;z-index:100;background:var(--bg);border-bottom:1px solid #ddd8d0}
  .nav-inner{display:flex;align-items:center;justify-content:space-between;height:60px;gap:16px}
  .nav-logo{display:flex;align-items:center;gap:8px;font-weight:700;font-size:1.05rem;color:var(--text);text-decoration:none}
  .nav-logo .plus{color:var(--purple);font-size:1.3rem;line-height:1}
  .nav-links{display:flex;gap:28px;list-style:none}
  .nav-links a{font-size:.88rem;color:var(--muted);text-decoration:none;font-weight:500;transition:color .2s}
  .nav-links a:hover{color:var(--text)}
  .btn-pill{background:var(--navy);color:#fff;border:none;padding:9px 22px;border-radius:100px;
    font-size:.88rem;font-weight:600;cursor:pointer;transition:background .2s;font-family:inherit;white-space:nowrap}
  .btn-pill:hover{background:var(--navy2)}
  .btn-pill:disabled{background:#b0aac0;cursor:not-allowed}
  .btn-pill.outline{background:transparent;border:1.5px solid var(--navy);color:var(--navy)}
  .btn-pill.outline:hover{background:var(--navy);color:#fff}
  .btn-pill.sm{padding:7px 18px;font-size:.82rem}

  /* ── Hero ── */
  .hero-wrap{padding:32px 28px 0;max-width:1120px;margin:0 auto}
  .hero{border-radius:24px;overflow:hidden;position:relative;min-height:460px;
    background:linear-gradient(145deg,#2b1060 0%,#5c3596 30%,#9b72c8 60%,#c9b0e8 80%,#ede6f7 100%);
    display:flex;flex-direction:column;align-items:center;justify-content:center;
    text-align:center;padding:60px 32px 40px;gap:0}
  /* decorative orbs */
  .hero::before,.hero::after{content:'';position:absolute;border-radius:50%;pointer-events:none}
  .hero::before{width:260px;height:260px;
    background:radial-gradient(circle at 40% 40%,#c8aaee88,#7c5cbf44,transparent 70%);
    bottom:-40px;left:-40px}
  .hero::after{width:300px;height:300px;
    background:radial-gradient(circle at 60% 35%,#e8d8f888,#9b72c855,transparent 70%);
    top:-60px;right:-60px}
  .hero-tag{background:#ffffff22;color:#ffffffcc;border:1px solid #ffffff33;
    border-radius:100px;padding:5px 16px;font-size:.78rem;font-weight:500;margin-bottom:20px;
    backdrop-filter:blur(6px)}
  .hero h1{font-size:clamp(2rem,5vw,3.4rem);font-weight:800;color:#fff;line-height:1.15;
    max-width:620px;margin-bottom:16px;letter-spacing:-.5px}
  .hero p{font-size:.98rem;color:#e2d8f5;max-width:440px;line-height:1.7;margin-bottom:28px}
  .hero-btns{display:flex;gap:12px;flex-wrap:wrap;justify-content:center}
  .btn-hero{background:#fff;color:var(--navy);border:none;padding:11px 28px;border-radius:100px;
    font-size:.92rem;font-weight:700;cursor:pointer;transition:transform .15s,box-shadow .15s;font-family:inherit}
  .btn-hero:hover{transform:translateY(-1px);box-shadow:0 6px 20px #0003}
  .btn-hero.ghost{background:#ffffff22;color:#fff;border:1px solid #ffffff44;backdrop-filter:blur(6px)}
  .btn-hero.ghost:hover{background:#ffffff33}
  /* coin shapes */
  .coin{position:absolute;border-radius:50%;opacity:.85;pointer-events:none}
  .coin-l{width:130px;height:130px;left:5%;top:50%;transform:translateY(-50%);
    background:radial-gradient(circle at 35% 35%,#d8c8f0,#8054b8,#3d1a7a);
    box-shadow:inset -6px -8px 18px #0004,0 8px 32px #5c359644}
  .coin-r{width:180px;height:180px;right:4%;top:50%;transform:translateY(-55%);
    background:radial-gradient(circle at 38% 32%,#ede0ff,#9b72c8,#4a2490);
    box-shadow:inset -8px -10px 24px #0003,0 12px 40px #7c5cbf44}

  /* ── What is ── */
  .section{padding:72px 0}
  .what-grid{display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center}
  .section-label{font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;color:var(--muted);margin-bottom:12px}
  .section h2{font-size:clamp(1.6rem,3vw,2.4rem);font-weight:800;line-height:1.2;letter-spacing:-.3px}
  .section p{font-size:.95rem;color:var(--muted);line-height:1.75;margin-top:8px}

  /* ── Feature cards ── */
  .features{padding-bottom:72px}
  .feat-grid{display:grid;grid-template-columns:1.5fr 1fr 1fr;gap:14px}
  .feat-card{border-radius:var(--card-radius);padding:28px 24px;position:relative;overflow:hidden;min-height:200px;
    display:flex;flex-direction:column;justify-content:space-between}
  .feat-card.light{background:var(--lavender)}
  .feat-card.dark{background:var(--navy);color:#fff}
  .feat-card h3{font-size:1.2rem;font-weight:700;line-height:1.3;max-width:180px}
  .feat-card p{font-size:.85rem;line-height:1.65;margin-top:10px;opacity:.8}
  .feat-card .feat-icon{font-size:2.4rem;margin-bottom:12px;opacity:.7}
  .feat-card.light .feat-orb{position:absolute;right:-20px;bottom:-20px;width:100px;height:100px;
    border-radius:50%;background:radial-gradient(circle,#c0a8e8,#9b72c8 60%,transparent 80%);opacity:.5}

  /* ── Powered by ── */
  .partners{padding:32px 0 56px;border-top:1px solid #ddd8d0}
  .partners-label{font-size:.78rem;color:var(--muted);font-weight:500;margin-bottom:20px}
  .partner-logos{display:flex;align-items:center;gap:36px;flex-wrap:wrap;opacity:.55}
  .partner-logos span{font-size:.82rem;font-weight:700;letter-spacing:.5px;color:var(--text);font-variant:small-caps}

  /* ── Form section ── */
  .form-section{padding:72px 0;border-top:1px solid #ddd8d0}
  .form-label-top{font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;color:var(--muted);margin-bottom:8px}
  .form-card{background:var(--white);border-radius:var(--card-radius);padding:36px;box-shadow:0 2px 20px #0000000a}
  .form-card label{font-weight:600;font-size:.9rem;color:var(--text);display:block;margin-bottom:10px}
  textarea{width:100%;border:1.5px solid #ddd8d0;border-radius:10px;padding:14px 16px;font-size:.94rem;
    font-family:inherit;resize:vertical;min-height:88px;transition:border .2s;color:var(--text);background:#faf9f7}
  textarea:focus{outline:none;border-color:var(--purple)}
  .form-row{display:flex;gap:14px;align-items:center;margin-top:18px;flex-wrap:wrap}
  #timer{font-size:.82rem;color:var(--muted)}

  /* ── Progress ── */
  #progress-box{display:none;margin-top:20px}
  .prog-card{background:var(--navy);border-radius:var(--card-radius);padding:24px 28px}
  .prog-title{font-size:.78rem;text-transform:uppercase;letter-spacing:1px;color:#9986c4;font-weight:600;margin-bottom:14px}
  .log{font-family:'DM Mono',monospace;font-size:.82rem;color:#c4b8e8;min-height:48px;max-height:180px;
    overflow-y:auto;line-height:1.9}
  .log .step::before{content:"▸ ";color:#7c5cbf}

  /* ── ICP ── */
  #icp-box{display:none;margin-top:20px}
  .icp-card{background:var(--white);border-radius:var(--card-radius);padding:32px 36px;box-shadow:0 2px 20px #0000000a}
  .icp-desc{font-size:.95rem;color:var(--muted);line-height:1.75;margin-bottom:20px}
  .icp-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}
  .icp-item{background:var(--lavender);border-radius:12px;padding:14px 16px}
  .icp-item h4{font-size:.7rem;text-transform:uppercase;letter-spacing:.8px;color:var(--purple);font-weight:700;margin-bottom:5px}
  .icp-item p{font-size:.85rem;color:var(--text);line-height:1.55}

  /* ── Leads ── */
  #leads-box{display:none;margin-top:20px}
  .leads-card{background:var(--white);border-radius:var(--card-radius);padding:32px 36px;box-shadow:0 2px 20px #0000000a}
  .leads-header{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:20px}
  .leads-header h3{font-size:1.1rem;font-weight:700}
  .export-btns{display:flex;gap:10px}
  .summary-bar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:20px}
  .badge{padding:5px 14px;border-radius:100px;font-size:.78rem;font-weight:700}
  .badge.hot{background:#fce8e8;color:#c0392b}
  .badge.warm{background:#fef6dc;color:#9a6d00}
  .badge.cold{background:#e3eeff;color:#1a56a0}
  .badge.total{background:var(--lavender);color:var(--purple)}
  .avg-tag{font-size:.8rem;color:var(--muted)}
  table{width:100%;border-collapse:collapse;font-size:.84rem}
  thead tr{background:var(--navy)}
  th{padding:11px 14px;text-align:left;font-weight:600;color:#fff;font-size:.78rem;
    text-transform:uppercase;letter-spacing:.6px;white-space:nowrap}
  td{padding:10px 14px;vertical-align:top;border-bottom:1px solid #f0ede8}
  tr.hot  td{background:#fff8f8}
  tr.warm td{background:#fffdf0}
  tr.cold td{background:#f5f8ff}
  tr:hover td{filter:brightness(.975)}
  .score{font-weight:800;font-size:1rem;text-align:center}
  .score.hot{color:#c0392b}
  .score.warm{color:#9a6d00}
  .score.cold{color:#1a56a0}
  .type-pill{display:inline-block;padding:3px 12px;border-radius:100px;font-size:.75rem;font-weight:700}
  .type-pill.hot{background:#fce8e8;color:#c0392b}
  .type-pill.warm{background:#fef6dc;color:#9a6d00}
  .type-pill.cold{background:#e3eeff;color:#1a56a0}
  .reason{color:var(--muted);font-size:.8rem;line-height:1.55}
  a.site{color:var(--purple);text-decoration:none;font-weight:600}
  a.site:hover{text-decoration:underline}
  a.mail{color:var(--muted);font-size:.78rem;text-decoration:none}
  a.mail:hover{color:var(--purple)}

  /* ── Error ── */
  #error-box{display:none;background:#fef2f2;border:1px solid #fca5a5;color:#b91c1c;
    border-radius:10px;padding:14px 18px;margin-top:16px;font-size:.9rem}

  @media(max-width:720px){
    .feat-grid{grid-template-columns:1fr}
    .what-grid{grid-template-columns:1fr}
    .nav-links{display:none}
  }
</style>
</head>
<body>

<!-- ── Nav ─────────────────────────────────────────────────────────────── -->
<nav>
  <div class="wrap nav-inner">
    <a class="nav-logo" href="#"><span class="plus">✦</span> LeadGen AI</a>
    <ul class="nav-links">
      <li><a href="#how">How it works</a></li>
      <li><a href="#features">Features</a></li>
      <li><a href="#generate">Use it</a></li>
    </ul>
    <button class="btn-pill" onclick="document.getElementById('desc').focus();document.getElementById('generate').scrollIntoView({behavior:'smooth'})">
      Launch Beta
    </button>
  </div>
</nav>

<!-- ── Hero ─────────────────────────────────────────────────────────────── -->
<div class="hero-wrap">
  <div class="hero">
    <div class="coin coin-l"></div>
    <div class="coin coin-r"></div>
    <div class="hero-tag">AI · Powered by Groq LLaMA 3.3 70B</div>
    <h1>Where Leads Grow</h1>
    <p>A programmable, AI-driven lead engine designed for native prospect discovery and seamless B2B targeting.</p>
    <div class="hero-btns">
      <button class="btn-hero" onclick="document.getElementById('generate').scrollIntoView({behavior:'smooth'})">Try it now</button>
      <button class="btn-hero ghost" onclick="document.getElementById('how').scrollIntoView({behavior:'smooth'})">Learn more</button>
    </div>
  </div>
</div>

<!-- ── What is ── -->
<div class="wrap">
  <div class="section" id="how">
    <div class="what-grid">
      <div>
        <p class="section-label">What is LeadGen AI?</p>
        <h2>Your next client is already online.</h2>
        <button class="btn-pill outline" style="margin-top:20px" onclick="document.getElementById('generate').scrollIntoView({behavior:'smooth'})">Explore now</button>
      </div>
      <div>
        <p style="font-size:1.1rem;font-weight:500;line-height:1.7;color:var(--text)">
          LeadGen AI is an intelligent B2B prospecting engine that transforms a plain business description into a ranked list of qualified leads — complete with ICP analysis, live web search, site scraping, and LLM scoring.
        </p>
      </div>
    </div>
  </div>

  <!-- ── Feature cards ── -->
  <div class="features" id="features">
    <div class="feat-grid">
      <div class="feat-card light">
        <div>
          <div class="feat-icon">🌱</div>
          <h3>Leads that convert</h3>
          <p>AI scoring identifies your highest-value prospects by matching every company against your exact Ideal Customer Profile.</p>
        </div>
        <div class="feat-orb"></div>
      </div>
      <div class="feat-card dark">
        <div class="feat-icon">⚡</div>
        <h3>Always live, always fresh</h3>
        <p>Real-time DuckDuckGo search means every run discovers new companies — no stale databases.</p>
      </div>
      <div class="feat-card dark">
        <div class="feat-icon">🤖</div>
        <h3>100% hands-free</h3>
        <p>Paste a description and walk away. ICP generation, scraping, and scoring happen automatically.</p>
      </div>
    </div>
  </div>

  <!-- ── Powered by ── -->
  <div class="partners">
    <p class="partners-label">Powered by the best AI infrastructure</p>
    <div class="partner-logos">
      <span>Groq</span>
      <span>LLaMA 3.3</span>
      <span>FastAPI</span>
      <span>DuckDuckGo</span>
      <span>BeautifulSoup</span>
      <span>Pydantic</span>
    </div>
  </div>

  <!-- ── Form ── -->
  <div class="form-section" id="generate">
    <p class="form-label-top">LeadGen AI in Action</p>
    <h2 style="font-size:clamp(1.5rem,3vw,2.2rem);font-weight:800;margin-bottom:28px;letter-spacing:-.3px">Generate leads</h2>
    <div class="form-card">
      <label for="desc">Describe your business</label>
      <textarea id="desc" rows="3"
        placeholder="e.g. We sell HR software for startups and mid-size companies in India and the US"></textarea>
      <div style="margin-top:16px">
        <label for="loc" style="display:flex;align-items:center;gap:6px;margin-bottom:8px">
          <span>Target Location</span>
          <span style="font-size:.75rem;color:var(--muted);font-weight:400">(optional — e.g. India, Bangalore, US, Europe)</span>
        </label>
        <input id="loc" type="text" placeholder="e.g. India  or  New York, US  or  Europe"
          style="width:100%;border:1.5px solid #ddd8d0;border-radius:10px;padding:11px 14px;
          font-size:.92rem;font-family:inherit;color:var(--text);background:#faf9f7;
          transition:border .2s;outline:none"
          onfocus="this.style.borderColor='var(--purple)'" onblur="this.style.borderColor='#ddd8d0'"/>
      </div>
      <div class="form-row">
        <button class="btn-pill" id="run-btn" onclick="runAgent()">Generate Leads</button>
        <span id="timer"></span>
      </div>
    </div>

    <div id="error-box"></div>

    <!-- Progress -->
    <div id="progress-box">
      <div class="prog-card">
        <div class="prog-title">Pipeline Progress</div>
        <div class="log" id="log"></div>
      </div>
    </div>

    <!-- ICP -->
    <div id="icp-box">
      <div class="icp-card">
        <p class="form-label-top">Ideal Customer Profile</p>
        <div class="icp-desc" id="icp-desc"></div>
        <div class="icp-grid" id="icp-grid"></div>
      </div>
    </div>

    <!-- Leads -->
    <div id="leads-box">
      <div class="leads-card">
        <div class="leads-header">
          <h3>Lead Results</h3>
          <div class="export-btns">
            <button class="btn-pill sm outline" onclick="downloadJSON()">JSON</button>
            <button class="btn-pill sm" onclick="downloadCSV()">CSV</button>
          </div>
        </div>
        <div class="summary-bar" id="summary-bar"></div>
        <div style="overflow-x:auto">
          <table>
            <thead><tr>
              <th>#</th><th>Company</th><th>Industry</th><th>Location</th><th>Score</th>
              <th>Fit</th><th>Type</th><th>Email</th><th>Reason</th>
            </tr></thead>
            <tbody id="leads-body"></tbody>
          </table>
        </div>
      </div>
    </div>

  </div><!-- /form-section -->
</div><!-- /wrap -->

<script>
let _leads=[], _icp={}, _timerInterval;

function startTimer(){let s=0;clearInterval(_timerInterval);_timerInterval=setInterval(()=>{document.getElementById('timer').textContent=`${++s}s elapsed`;},1000);}
function stopTimer(){clearInterval(_timerInterval);}
function escHtml(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function tc(t){return t.toLowerCase();}

function log(msg){
  const el=document.getElementById('log');
  el.innerHTML+=`<div class="step">${escHtml(msg)}</div>`;
  el.scrollTop=el.scrollHeight;
}

function runAgent(){
  const desc=document.getElementById('desc').value.trim();
  if(!desc){alert('Please enter a business description.');return;}
  const loc=(document.getElementById('loc').value||'').trim();
  document.getElementById('run-btn').disabled=true;
  document.getElementById('error-box').style.display='none';
  document.getElementById('progress-box').style.display='block';
  document.getElementById('icp-box').style.display='none';
  document.getElementById('leads-box').style.display='none';
  document.getElementById('log').innerHTML='';
  startTimer();

  let url=`/stream?q=${encodeURIComponent(desc)}`;
  if(loc) url+=`&loc=${encodeURIComponent(loc)}`;
  const es=new EventSource(url);
  es.onmessage=(e)=>{
    const msg=JSON.parse(e.data);
    if(msg.type==='progress'){log(msg.msg);}
    else if(msg.type==='result'){
      es.close();stopTimer();
      _icp=msg.icp;_leads=msg.leads;
      renderICP(msg.icp);renderLeads(msg.leads);
      document.getElementById('run-btn').disabled=false;
      document.getElementById('timer').textContent='';
      document.getElementById('icp-box').scrollIntoView({behavior:'smooth',block:'start'});
    }
    else if(msg.type==='error'){
      es.close();stopTimer();
      document.getElementById('error-box').textContent='Error: '+msg.msg;
      document.getElementById('error-box').style.display='block';
      document.getElementById('run-btn').disabled=false;
    }
  };
  es.onerror=()=>{es.close();stopTimer();document.getElementById('run-btn').disabled=false;};
}

function renderICP(icp){
  document.getElementById('icp-desc').textContent=icp.description||'';
  const items=[
    ['Target Industries',(icp.target_industries||[]).join(', ')],
    ['Company Size',icp.company_size||''],
    ['Geographies',(icp.geographies||[]).join(', ')],
    ['Pain Points',(icp.pain_points||[]).join(' · ')],
  ];
  document.getElementById('icp-grid').innerHTML=items.map(([h,v])=>
    `<div class="icp-item"><h4>${h}</h4><p>${escHtml(v)}</p></div>`).join('');
  document.getElementById('icp-box').style.display='block';
}

function renderLeads(leads){
  const hot=leads.filter(l=>l.lead_type==='Hot').length;
  const warm=leads.filter(l=>l.lead_type==='Warm').length;
  const cold=leads.filter(l=>l.lead_type==='Cold').length;
  const avg=leads.length?Math.round(leads.reduce((s,l)=>s+l.lead_score,0)/leads.length):0;
  document.getElementById('summary-bar').innerHTML=
    `<span class="badge total">${leads.length} Total</span>
     <span class="badge hot">${hot} Hot</span>
     <span class="badge warm">${warm} Warm</span>
     <span class="badge cold">${cold} Cold</span>
     <span class="avg-tag">avg score ${avg}</span>`;
  document.getElementById('leads-body').innerHTML=leads.map((l,i)=>{
    const t=tc(l.lead_type);
    const loc=l.location&&l.location!=='Unknown'
      ?`<span style="display:inline-flex;align-items:center;gap:4px;font-size:.8rem;color:var(--muted)">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>
          ${escHtml(l.location)}</span>`
      :'<span style="color:#ccc">—</span>';
    return `<tr class="${t}">
      <td style="text-align:center;font-weight:700;color:var(--muted)">${i+1}</td>
      <td><a class="site" href="${escHtml(l.website)}" target="_blank">${escHtml(l.company_name)}</a>
          <div style="font-size:.74rem;color:#b0aac0;margin-top:2px">${escHtml(l.website)}</div></td>
      <td>${escHtml(l.industry||'')}</td>
      <td>${loc}</td>
      <td class="score ${t}">${l.lead_score}</td>
      <td style="text-align:center;font-weight:600">${escHtml(l.fit_percentage)}</td>
      <td><span class="type-pill ${t}">${escHtml(l.lead_type)}</span></td>
      <td>${l.contact_email?`<a class="mail" href="mailto:${escHtml(l.contact_email)}">${escHtml(l.contact_email)}</a>`:'—'}</td>
      <td class="reason">${escHtml(l.reason||'')}</td>
    </tr>`;
  }).join('');
  document.getElementById('leads-box').style.display='block';
}

function downloadJSON(){
  const b=new Blob([JSON.stringify({icp:_icp,leads:_leads},null,2)],{type:'application/json'});
  const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='leads.json';a.click();
}
function downloadCSV(){
  const cols=['company_name','website','industry','location','description','contact_email','lead_score','fit_percentage','lead_type','reason'];
  const rows=[cols.join(','),..._leads.map(l=>cols.map(c=>`"${(l[c]||'').toString().replace(/"/g,'""')}"`).join(','))];
  const b=new Blob([rows.join('\\n')],{type:'text/csv'});
  const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='leads.csv';a.click();
}
</script>
</body>
</html>"""


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    return _HTML


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/stream")
async def stream_leads(q: str, loc: Optional[str] = None):
    """SSE endpoint — streams pipeline progress then final results."""
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required.")

    location_filter = loc.strip() if loc and loc.strip() else None

    async def event_generator():
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()

        def on_step(msg: str):
            asyncio.run_coroutine_threadsafe(queue.put({"type": "progress", "msg": msg}), loop)

        async def run():
            try:
                icp, leads = await loop.run_in_executor(
                    _executor,
                    lambda: run_pipeline(q.strip(), location_filter=location_filter, on_step=on_step),
                )
                await queue.put({
                    "type": "result",
                    "icp": icp.model_dump(mode="json"),
                    "leads": [l.model_dump(mode="json") for l in leads],
                })
            except Exception as exc:
                await queue.put({"type": "error", "msg": str(exc)})
            await queue.put(None)

        asyncio.create_task(run())

        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=180)
            except asyncio.TimeoutError:
                yield "data: {\"type\":\"error\",\"msg\":\"Pipeline timed out\"}\n\n"
                break
            if item is None:
                break
            yield f"data: {json.dumps(item, default=str)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)
