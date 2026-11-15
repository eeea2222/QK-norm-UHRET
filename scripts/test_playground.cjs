// Exercise the served dashboard controls against actual model endpoints in headless Chrome.
(async()=>{
const fs=require('fs');const pages=await(await fetch('http://localhost:9223/json')).json();const page=pages.find(x=>x.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);let id=0;const pending=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)(m);pending.delete(m.id)}};const send=(method,params={})=>new Promise(r=>{pending.set(++id,r);ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)throw Error(JSON.stringify(r.result.exceptionDetails));return r.result.result.value};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));await send('Page.navigate',{url:'http://127.0.0.1:8005/?ai='+Date.now()+'#ai-test'});await sleep(1200);
await send('Emulation.setDeviceMetricsOverride',{width:1500,height:1000,deviceScaleFactor:1,mobile:false});
const results=[];
for(const model of ['a','b','c','wt4']){
 await evaluate(`document.getElementById('ai-model').value='${model}';document.getElementById('ai-model').dispatchEvent(new Event('change'));document.getElementById('ai-form').requestSubmit();`);
 let state='';for(let i=0;i<180;i++){await sleep(500);state=await evaluate("document.getElementById('ai-state').textContent");if(state!=='Çalışıyor…')break}
 const result=await evaluate("document.getElementById('ai-result').innerText");results.push({model,state,result,passed:state==='Tamamlandı'&&result.length>0});
}
await evaluate("document.getElementById('ai-test').scrollIntoView()");await sleep(200);const shot=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync('outputs/ai_playground.png',Buffer.from(shot.result.data,'base64'));fs.writeFileSync('outputs/ai_playground_tests.json',JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));ws.close();process.exitCode=results.every(x=>x.passed)?0:1;
})().catch(e=>{console.error(e);process.exit(1)});
