import re
import os

filepath = r'g:\Мій диск\Claude\SolarKP HTML\solarkp\index.html'

with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

# CSS Adds
css_add = r'''
.loader-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: var(--bg); z-index: 9999;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.spinner {
  width: 44px; height: 44px; border: 4px solid var(--sky-lt);
  border-top-color: var(--sky); border-radius: 50%;
  animation: spin 1s linear infinite; margin-bottom: 20px;
}
.loader-text { font-size: 16px; font-weight: 700; color: var(--sky); letter-spacing: 0.5px; }
@keyframes spin { 100% { transform: rotate(360deg); } }

.result-panel::-webkit-scrollbar{width:4px;}
.result-panel::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px}
.step-header:hover { background: linear-gradient(to right, var(--sky-lt), #F0F9FF); }

@media(max-width: 768px){
  .btn-kp { position: sticky; bottom: 16px; z-index: 100; box-shadow: 0 10px 30px rgba(22,163,74,.4); }
  .result-panel { max-height: none; overflow-y: visible; }
}

@page { size: A4 portrait; margin: 20mm; }
@media print{
  body, html { background: #fff; color: #000; font-size: 11pt; }
  .topbar,.kp-toolbar{display:none !important}
  #calc-page{display:none!important}
  #kp-page{display:block!important;background:#fff; min-height: auto;}
  .kp-doc{padding:0 !important; max-width: 100%; margin: 0; box-shadow: none; border: none;}
  .kp-banner { border-radius: 8px; margin-bottom: 20px; padding: 15px 20px; -webkit-print-color-adjust: exact; print-color-adjust: exact; color: #000 !important; background: #e0f2fe !important; border: 1px solid #bae6fd;}
  .kp-title-block, .kp-tbl-wrap, .kp-footer { box-shadow: none; border: 1px solid #ddd; }
  .kp-footer { page-break-inside: avoid; }
  table.kt th { background: #f1f5f9 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; color: #000 !important; }
  .tr-g td { background: #e0f2fe !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; color: #000 !important; }
  .tr-acc td { background: #e2e8f0 !important; color: #000 !important; font-weight: 800; -webkit-print-color-adjust: exact; print-color-adjust: exact; border-top: 2px solid #000;}
  .kp-bn, .kp-bs, .kp-brl, .kp-brd { color: #0f172a !important; }
  .tr-s td { color: #000 !important; background: #f8fafc !important; }
  .tr-tot td { color: #000 !important; }
  .tr-dim td { color: #333 !important; }
}
</style>'''
code = code.replace('</style>', css_add)

code = code.replace('.result-panel{position:sticky;top:80px;height:fit-content;display:flex;flex-direction:column;gap:16px}', '.result-panel{position:sticky;top:80px;height:fit-content;max-height:calc(100vh - 100px);overflow-y:auto;padding-right:5px;display:flex;flex-direction:column;gap:16px}')

code = code.replace('<body>', '<body>\n<div id="loader" class="loader-overlay"><div class="spinner"></div><div class="loader-text">Отримання актуальних цін...</div></div>')

dyn_vars = '''let PANELS = [];
let H_INV = {};
let G_INV = {};
let MOUNT = {
  flat_south:{label:"Баластна Південь",price:25.50},
  flat_ew:{label:"Баластна Схід-Захід",price:27.00},
  pitched:{label:"Під металопрофіль",price:18.50},
  ground:{label:"Наземна оцинкована",price:32.25},
};'''
code = re.sub(r'const PANELS=\[.*?\].*?const MOUNT=\{.*?\};', dyn_vars, code, flags=re.DOTALL)

code = code.replace('const STR=17, CABLE_K=1.5, CABLE_P=1009, AC_KW=35, GEN=0.10, VAT=0.20, KP_DAYS=10;', 'const STR=17, CABLE_K=1.5, AC_KW=35, GEN=0.10, VAT=0.20, KP_DAYS=10;\nlet CABLE_P=1009;')
code = code.replace('const STORE="solar_kp_v10";', 'const STORE="solar_kp_v21";')
code = code.replace('panelIdx:0,usdRate:44.5,', 'panelModel:null,usdRate:44.5,hardwareNoVAT:false,')

# Correct the panel indexing code:
code = code.replace('const panel=PANELS[S.panelIdx];', 'const panel=PANELS.find(p=>p.model===S.panelModel)||PANELS[0];')
code = code.replace('const p=PANELS[S.panelIdx];', 'const p=PANELS.find(x=>x.model===S.panelModel)||PANELS[0];')
code = code.replace('PANELS[S.panelIdx]?.label||""', '(PANELS.find(p=>p.model===S.panelModel)||PANELS[0])?.label||""')

# VAT logic
code = code.replace('const sesVAT=sesNoVAT*VAT;', 'const sesVAT=(S.hardwareNoVAT ? (mountCost+cableCost+acNetCost+workCost+genCost) : sesNoVAT)*VAT;')

# Checkbox
vat_html = '''</div>
      <div class="fld" onclick="toggleHardwareVAT()">
        <div class="chk-row${S.hardwareNoVAT?" chk":""}">
          <div class="chkbox"><span class="chkmark">✓</span></div>
          <div>
            <div class="chk-title">Купівля панелей та інверторів у нерезидента (без ПДВ)</div>
            <div class="chk-sub">Вартість панелей та інверторів виключається з бази ПДВ (20%)</div>
          </div>
        </div>
      </div>'''
code = code.replace('</div>\n      <div class="step-nav">\n        <button class="btn-prev" onclick="goStep(3)">← Назад</button>\n      </div>`;',
                    vat_html + '\n      <div class="step-nav">\n        <button class="btn-prev" onclick="goStep(3)">← Назад</button>\n        <button class="btn-kp" style="padding:10px 22px;border-radius:8px;font-size:14px;box-shadow:none;width:auto" onclick="showKP()">📄 Сформувати КП →</button>\n      </div>`;')

code = code.replace('function calc(){', 'function toggleHardwareVAT(){S.hardwareNoVAT=!S.hardwareNoVAT;calc();renderBody(4);}\nfunction calc(){')

code = code.replace('S.panelIdx=+e.target.value;', 'S.panelModel=e.target.value;')

# Fix the map HTML
old_map = 'const opts=PANELS.map((pl,idx)=>\`<option value="${idx}"${S.panelIdx==idx?" selected":""}>${pl.label} · $${(pl.price*pl.power).toFixed(2)}/шт [${pl.avail}]</option>\`).join("");'
new_map = 'const opts=PANELS.map(pl=>`<option value="${esc(pl.model)}"${S.panelModel===pl.model?" selected":""}>${pl.label} · $${(pl.price*pl.power).toFixed(2)}/шт [${pl.avail}]</option>`).join("");'
code = code.replace(old_map, new_map)


# KP Table rows modifications
code = code.replace('["ПДВ 20%",C.sesVAT,"tr-dim"],', '[(S.hardwareNoVAT?"ПДВ 20% (без обладнання)":"ПДВ 20%"),C.sesVAT,"tr-dim"],')
code = code.replace('${S.notes?`<div class="kp-notes"><strong>Примітки:</strong> ${S.notes}</div>`:""}',
                    '${S.notes?`<div class="kp-notes" style="margin-bottom:12px"><strong>Примітки:</strong> ${S.notes}</div>`:""}\n    ${S.hardwareNoVAT?`<div class="kp-notes"><strong>Увага:</strong> Вартість фотомодулів та інверторів вказана без урахування ПДВ (закупівля у нерезидента).</div>`:""}')
code = code.replace('const pw=`$${(r.sum/C.actKwDC).toFixed(1)}`;', 'const pw=`$${(r.sum/C.actKwDC).toFixed(1)}`;\n    if (S.hardwareNoVAT && (r.n==="1.1" || r.n==="1.2")) r.name += " <i>(Без ПДВ)</i>";')

fetch_init = r'''
const GIDS = { panels: "397532524", mounts: "134973451", gridInv: "457704901", hybridInv: "732265429", cable: "1236649776" };
const B_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRLVRljrTAFt1BL9b7IBJBIxvHMc0PI2EAliBj1z6i2LkhjlnLSlqSHUNmJPIKLPHhYGdvkRUYmgxUb/pub?single=true&output=csv&gid=";
function parseCSVLine(l){let r=[],c="",q=false;for(let i=0;i<l.length;i++){const ch=l[i];if(ch==='"'){if(q&&l[i+1]==='"'){c+='"';i++;}else q=!q;}else if(ch===','&&!q){r.push(c);c="";}else c+=ch;}r.push(c);return r;}
function parsePrice(s){if(!s)return 0;const m=s.replace(',','.').match(/[\d.]+/);return m?parseFloat(m[0]):0;}
async function fetchCSV(g){const res=await fetch(B_URL+g);if(!res.ok)throw new Error("X");const t=await res.text();return t.split('\n').map(l=>l.trim()).filter(Boolean).map(parseCSVLine);}

async function initApp() {
  try {
    const [p, m, g, h, c] = await Promise.all([fetchCSV(GIDS.panels), fetchCSV(GIDS.mounts), fetchCSV(GIDS.gridInv), fetchCSV(GIDS.hybridInv), fetchCSV(GIDS.cable)]);
    
    PANELS=[];
    for(const r of p){
      if(r.length>=5){
        const model=r[0]?(r[0].trim()):"", desc=r[1]?(r[1].trim()):"", avail=r[2]?(r[2].trim()):"", priceStr=r[4];
        if(model&&desc&&priceStr&&!model.includes("Модель")){
           const price = parsePrice(priceStr);
           const powMatch=desc.match(/(\d+)\s*(В|W|Вт)/i);
           const pow=powMatch?parseInt(powMatch[1]):0;
           if(pow>0 && price>0) PANELS.push({model, label:desc.split(' ').slice(0,6).join(' '), power:pow, price, avail});
        }
      }
    }

    const parseI = (csv, map) => {
      for(const r of csv){
        if(r.length>=5){
          const model=r[0]?(r[0].trim()):"", desc=r[1]?(r[1].trim()):"", priceStr=r[4];
          if(model&&priceStr&&!model.includes("Модель")){
            const price = parsePrice(priceStr);
            const kwMatch=model.match(/(\d+)K/i)||desc.match(/(\d+)\s*[kк][WВ]/i);
            const nom=kwMatch?parseInt(kwMatch[1]):0;
            if(nom>0 && price>0) map[nom]={model:model, price:price};
          }
        }
      }
    };
    H_INV={}; G_INV={};
    parseI(h, H_INV); parseI(g, G_INV);

    for(const r of c){ const desc=r[1]?(r[1].trim()):"", priceStr=r[4]; if(desc&&desc.includes("1*6")&&priceStr){ const p=parsePrice(priceStr); if(p>0) CABLE_P=p*1000; }}

    for(const r of m){
      const desc=r[1]?(r[1].trim()):"", priceStr=r[4];
      if(desc&&priceStr){
        const p=parsePrice(priceStr);
        if(p>0){
          if(desc.includes("Південь")) MOUNT.flat_south.price=p;
          else if(desc.includes("Схід-Захід")) MOUNT.flat_ew.price=p;
          else if(desc.includes("металопрофіль")) MOUNT.pitched.price=p;
          else if(desc.includes("Наземна")) MOUNT.ground.price=p;
        }
      }
    }

    localStorage.setItem("skp_cache_v21", JSON.stringify({PANELS, H_INV, G_INV, MOUNT, CABLE_P}));
  } catch(e) {
    console.warn("Google Sheets error, using cache", e);
    const cStr=localStorage.getItem("skp_cache_v21");
    if(cStr){
       const c=JSON.parse(cStr);
       if(c.PANELS&&c.PANELS.length)PANELS=c.PANELS; 
       if(c.H_INV)H_INV=c.H_INV; 
       if(c.G_INV)G_INV=c.G_INV;
       if(c.MOUNT)MOUNT=c.MOUNT; 
       if(c.CABLE_P)CABLE_P=c.CABLE_P;
    }
  }

  if(PANELS.length===0) PANELS.push({model:"Unknown", label:"Дані не завантажено", power:500, price:0.15, avail:"-"});
  if(Object.keys(H_INV).length===0) H_INV[10] = {model:"Unknown", price:1000};
  if(Object.keys(G_INV).length===0) G_INV[10] = {model:"Unknown", price:800};

  if(!S.panelModel && PANELS.length) S.panelModel=PANELS[0].model;
  
  const loaderEl = document.getElementById("loader"); if(loaderEl) loaderEl.style.display="none";
  buildUI();
}
'''

code = code.replace('buildUI();\n</script>', fetch_init + 'initApp();\n</script>')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(code)

print("Update completed successfully.")
