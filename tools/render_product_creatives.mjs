import {spawn} from 'node:child_process';
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
const root=process.cwd().replaceAll('\\','/');
const folder=`${root}/assets/images/product-gallery`;
const version=process.env.CREATIVE_VERSION || 'v3';
const before=createHash('sha256').update(await fs.readFile(`${folder}/actual-product-official-v3.jpg`)).digest('hex');
const proc=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless','--disable-gpu','--no-first-run','--remote-debugging-port=9339',`--user-data-dir=${root}/design-preview/creative-v3-check-profile`,'about:blank'],{windowsHide:true,stdio:'ignore'});
let ws;
try {
 let pages;
 for(let i=0;i<80;i++){try{pages=await (await fetch('http://127.0.0.1:9339/json')).json();if(pages.length)break;}catch{}await new Promise(r=>setTimeout(r,100));}
 if(!pages?.length)throw Error('Chrome unavailable');
 ws=new WebSocket(pages.find(p=>p.type==='page').webSocketDebuggerUrl);
 await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});
 let id=0;const pending=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result);}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const key=++id;pending.set(key,{resolve,reject});ws.send(JSON.stringify({id:key,method,params}));});
 const run=async expression=>{const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
 const pause=ms=>new Promise(r=>setTimeout(r,ms));
 const shot=async file=>{const r=await send('Page.captureScreenshot',{format:'png'});await fs.writeFile(file,Buffer.from(r.data,'base64'));};
 const navigate=async(url,selector)=>{await send('Page.navigate',{url});for(let i=0;i<80;i++){if(await run(`!!document.querySelector(${JSON.stringify(selector)})`))break;await pause(100);}await run("Promise.all([...document.images].map(i=>{i.loading='eager';return i.decode()})).then(()=>true)");};
 await send('Page.enable');await send('Runtime.enable');await send('Emulation.setDeviceMetricsOverride',{width:1080,height:1080,deviceScaleFactor:1,mobile:false});
 await navigate(`file:///${folder}/creative-source-${version}/index.html`,'.creative');
 const count=await run("document.querySelectorAll('.creative').length");
 const cleanIndex=Math.min(count-1,count>=10?8:7);
 for(let i=1;i<=count;i++){
  await run(`document.querySelectorAll('.creative').forEach((el,index)=>el.classList.toggle('active',index===${i-1}));true`);
  await pause(100);
  const issue=await run("(()=>{const el=document.querySelector('.creative.active');const product=el.querySelector('.actual-product');const p=product?product.getBoundingClientRect():null;const texts=[...el.querySelectorAll('h1,.support,.detail,li')];return texts.flatMap(t=>{const range=document.createRange();range.selectNodeContents(t);return [...range.getClientRects()]}).some(r=>{return r.bottom>1080||r.right>1080||(p&&r.left<p.right&&r.right>p.left&&r.top<p.bottom&&r.bottom>p.top)});})()");
  if(issue)throw Error(`Creative ${i} text/product bounds overlap`);
  await shot(`${folder}/product-${String(i).padStart(2,'0')}-minimal-${version}.png`);
 }
 console.log(`PASS: ${count} square creatives exported, no text/product overlap.`);
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1150,deviceScaleFactor:1,mobile:false});
 await navigate(`file:///${root}/design-preview/product-gallery-qa.html`,'.product-gallery');
 await pause(150);
 await shot(`${root}/design-preview/product-minimal-${version}-desktop.png`);
 await run("document.querySelector('[data-slide=\"1\"]').click()");await pause(700);
 if(await run("document.querySelector('.product-gallery__status').textContent")!==`02 / ${count}`)throw Error('Thumbnail navigation failed');
 await shot(`${root}/design-preview/product-minimal-${version}-second-desktop.png`);
 await send('Emulation.setDeviceMetricsOverride',{width:390,height:1050,deviceScaleFactor:1,mobile:true});
 await pause(150);
 await run(`document.querySelector('[data-slide="${cleanIndex}"]').click()`);await pause(700);
 await shot(`${root}/design-preview/product-minimal-${version}-clean-mobile.png`);
 const result=await run("({viewport:innerWidth,page:document.documentElement.scrollWidth,broken:[...document.querySelectorAll('.product-gallery img')].filter(i=>!i.complete||!i.naturalWidth).length,slides:document.querySelectorAll('.product-slide').length,oldOverlays:document.querySelectorAll('.product-original').length,status:document.querySelector('.product-gallery__status').textContent})");
 if(result.page>result.viewport||result.broken||result.slides!==count||result.oldOverlays||result.status!==`${String(cleanIndex+1).padStart(2,'0')} / ${count}`)throw Error(JSON.stringify(result));
 console.log('PASS: desktop/mobile gallery, image loading, original-product replacement and navigation.',JSON.stringify(result));
 await send('Browser.close');
}finally{if(ws)ws.close();proc.kill();}
const after=createHash('sha256').update(await fs.readFile(`${folder}/actual-product-official-v3.jpg`)).digest('hex');
if(before!==after)throw Error('Product master was modified');
console.log('PASS: actual product master unchanged:',after);
