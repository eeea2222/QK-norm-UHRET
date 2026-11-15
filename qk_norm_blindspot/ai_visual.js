(()=>{
const host=document.getElementById('ai-playground'),model=document.getElementById('ai-model');if(!host||!model)return;
const panel=document.createElement('div');panel.className='ai-visual';panel.innerHTML='<div class="ai-vis-head"><span>SEÇİLEN ÖRNEK <small>Numune çizimleri temsili · değerler seçili girdiden</small></span><button type="button">Ⅱ Duraklat</button></div><canvas role="img" aria-label="Seçilen örneğin numunesi ve koşulları"></canvas><div class="ai-vis-foot"><span class="ai-vis-input"></span><span class="ai-vis-status"></span><span class="ai-vis-output"></span></div>';host.querySelector('.ai-tabs').after(panel);
const canvas=panel.querySelector('canvas'),ctx=canvas.getContext('2d');if(!ctx)return;
let w=900,h=235,t=0,last=0,paused=matchMedia('(prefers-reduced-motion: reduce)').matches;const btn=panel.querySelector('button');function button(){btn.textContent=paused?'▶ Oynat':'Ⅱ Duraklat'}button();btn.onclick=()=>{paused=!paused;button()};
const photo=new Image();photo.src='assets/3d/saffire_sample.jpeg';
new ResizeObserver(()=>{w=canvas.clientWidth;const ratio=Math.min(devicePixelRatio||1,2);canvas.width=w*ratio;canvas.height=h*ratio;ctx.setTransform(ratio,0,0,ratio,0,0)}).observe(canvas);
function txt(s,x,y,size=12,color='#d1dcd5'){ctx.font=`${size}px system-ui`;ctx.fillStyle=color;ctx.fillText(String(s),x,y)}
function line(points,color='#d9b59c',width=1){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.stroke()}
function box(x,y,bw,bh,color,r=7){ctx.fillStyle=color;ctx.beginPath();ctx.roundRect(x,y,bw,bh,r);ctx.fill()}
function sample(mat,x,y,sw,th=18){
const colors={PMMA:'#92dcf0',Kapton:'#d89424',Teflon:'#eef1ee',Silicone:'#d97771',Pyrell:'#697780',Lampwick:'#eee1b6'},c=colors[mat]||'#92dcf0';
ctx.save();ctx.translate(x,y);ctx.rotate(-.09);ctx.globalAlpha=mat==='PMMA'?.78:1;
box(-sw/2,0,sw,th,'#4b4c47',3);ctx.fillStyle=c;ctx.beginPath();ctx.moveTo(-sw/2,0);ctx.lineTo(-sw/2+23,-52);ctx.lineTo(sw/2+23,-52);ctx.lineTo(sw/2,0);ctx.closePath();ctx.fill();ctx.strokeStyle='#ffffff70';ctx.stroke();ctx.globalAlpha=1;
if(mat==='Pyrell'){for(let i=0;i<35;i++){const px=-sw/2+12+(i*23)%(sw-20),py=-5-((i*13)%40);ctx.fillStyle='#202e3a';ctx.beginPath();ctx.ellipse(px+15,py,3,2,0,0,Math.PI*2);ctx.fill()}}
if(mat==='Lampwick'){for(let i=0;i<12;i++)line([[-sw/2+8+i*(sw/12),-1],[-sw/2+30+i*(sw/12),-48]],'#a39777',2);for(let i=0;i<6;i++)line([[-sw/2+5+i*4,-i*9],[sw/2+5+i*4,-i*9]],'#b6a985',1)}
if(mat==='Kapton'){box(-sw/2+25,-43,sw*.5,6,'#ffe09870',2)}ctx.restore();
}
function draw(now){const dt=Math.min((now-last)/1000,.05)||0;last=now;const input=host.aiInput||{},res=host.aiResult,k=model.value,busy=host.getAttribute('aria-busy')==='true';if(!paused)t+=dt*(busy?1.6:1);
ctx.fillStyle='#15201f';ctx.fillRect(0,0,w,h);const narrow=w<600;const split=narrow?w*.50:w*.47;const lx=split*.5,rx=split+15;const mat=k==='a'?'PMMA':input.material;
const title=k==='a'?'PMMA levha':k==='c'?({Teflon:'Teflon · beyaz polimer levha',Kapton:'Kapton · amber film',Silicone:'Silicone · kauçuk',Pyrell:'Pyrell · gözenekli köpük',Lampwick:'Lampwick · dokuma fitil'}[mat]||mat):k==='b'?'Gerçek Saffire-I karesi':'Senin isteğin';
panel.querySelector('.ai-vis-input').textContent=title;
panel.querySelector('.ai-vis-status').textContent=busy?'● Hesaplanıyor':res?'✓ Sonuç alındı':'Örnek önizlemesi';panel.querySelector('.ai-vis-output').textContent=k==='b'?'NASA · C1 · SIBAL':k==='wt4'?'İstek → metin':'Temsili numune';
line([[split,18],[split,h-18]],'#ffffff15');
if(k==='a'||k==='c'){
const sw=Math.min(split*.6,190)*(k==='a'?Math.max(.45,Math.min(1.2,input.width_cm/2.2)):1);const thickness=k==='a'?Math.max(5,Math.min(32,input.thickness_mm*5)):15;
sample(mat,lx,133,sw,thickness);txt(mat,lx-sw/2,190,20,'#fff');
if(k==='a'){
 txt(`${input.width_cm} cm genişlik`,lx-sw/2,210,10);txt(`${input.thickness_mm} mm`,lx+sw/2-25,161,11,'#90dce9');
 const speed=Math.max(0,Number(input.velocity_cm_s)||0);for(let i=0;i<4;i++){const xx=25+((t*speed*7+i*32)%Math.max(80,split-65));line([[xx,58],[xx+20,58],[xx+15,54]],'#61dbd7',2)}
 txt(`Hava: ${input.velocity_cm_s} cm/s`,rx,42,14);txt(`O₂: %${input.initial_o2_vol_pct}`,rx,73,14);txt(`Levha: ${input.thickness_mm} mm × ${input.width_cm} cm`,rx,104,13);txt('Boyutlar görselde abartılmıştır',rx,137,10,'#a6b4ac');
 if(res)txt(`${res.response.predicted_flame_spread_rate.toFixed(5)} mm/s`,rx,184,narrow?18:26,'#a9e9e0');else txt('Tahmin için çalıştır →',rx,184,13,'#aec1b7');
}else{
 const volts=res?.nearest_measured_experiment?.iss_scatter_v;
 if(Number.isFinite(volts)){
   const start=16,end=split-16,scale=Math.max(2.5,volts*1.15),at=v=>start+(end-start)*Math.max(0,v)/scale;
   txt('En yakın test · ölçüm',start,25,11,'#d9b59c');
   line([[start,49],[end,49]],'#594538',3);
   line([[at(2),42],[at(2),56]],'#ffe2a7',2);
   box(at(volts)-4,45,8,8,'#94eee2',4);
   txt('2 V',at(2)-8,69,10,'#ffe2a7');
   txt(volts.toLocaleString('tr-TR',{maximumFractionDigits:3})+' V',start,69,10,'#94eee2');
 }
 const entries=[['Akış',input.airflow_cm_s,'cm/s',8.1],['Isıtma',input.heating_s,'s',120],['Yaşlandırma',input.aging_s,'s',720],['Karıştırma',input.mixing_s,'s',8],['Direnç oranı',input.resistance_ratio,'',1.6]];
 entries.forEach(([name,v,unit,max],i)=>{const yy=30+i*31;txt(`${name}: ${v} ${unit}`,rx,yy,11);box(rx,yy+7,Math.max(30,w-split-40),4,'#594538',2);box(rx,yy+7,Math.max(2,Math.min(1,Math.max(0,Number(v)/max))*(w-split-40)),4,mat==='Teflon'?'#d8e3ed':mat==='Kapton'?'#d69b3b':'#8eb4a8',2)});
 txt(res?`Tahmin: 2.0 V ${res.predicted_alarm_level_reached?'ulaşır':'ulaşmaz'}`:'Koşullar → eşik tahmini',rx,213,narrow?10:14,res?'#9ee7da':'#aec1b7');
}
}else if(k==='b'){
if(photo.complete&&photo.naturalWidth){const iw=Math.min(split-28,190*photo.width/photo.height),ih=iw*photo.height/photo.width,ix=(split-iw)/2,iy=(h-ih)/2;ctx.drawImage(photo,ix,iy,iw,ih);const px=res?.response.position_px;if(Number.isFinite(px)){const x=ix+iw*px/photo.naturalWidth;line([[x,iy],[x,iy+ih]],'#ffe2a7',2);box(x-3,iy,6,6,'#ffe2a7',3)}else{const scan=ix+((t*.12)%1)*iw;line([[scan,iy],[scan,iy+ih]],'#6de4db',1)}}else txt('Görüntü yükleniyor…',20,100);
txt('SIBAL · kamera C1',rx,45,16,'#fff');txt('Mapped_S1C1',rx,75,11);txt('1465937331457.jpeg',rx,96,11);txt(res?'Çizgi: tahmini sırt konumu':'Tarama önizlemesi',rx,132,10,'#a6b4ac');if(Number.isFinite(res?.response.value))txt(`${res.response.value.toFixed(2)} mm`,rx,183,narrow?18:28,'#96e7dc');else txt('Gerçek kareyi işle →',rx,183,13);
}else{
const prompt=String(input.prompt||''),tokens=prompt.split(/\s+/).filter(Boolean).slice(0,22);let x=18,y=43;
ctx.font='12px system-ui';for(let i=0;i<tokens.length;i++){const word=tokens[i],bw=Math.min(split-35,ctx.measureText(word).width+18);if(x+bw>split-12){x=18;y+=32}if(y>195)break;box(x,y-18,bw,25,i===Math.floor(t*2)%tokens.length?'#396b60':'#293c37');ctx.save();ctx.beginPath();ctx.rect(x,y-18,bw,25);ctx.clip();txt(word,x+8,y,12,'#ecf1ea');ctx.restore();x+=bw+7}
txt('İstek önizlemesi',18,219,10,'#aec1b7');txt(`En fazla ${input.max_new_tokens} yeni token`,rx,36,12);const output=res?res.generation.text:'Çalıştırdığında gerçek yanıt burada görünür.';const words=output.split(/\s+/);let ln='',yy=76;ctx.font='13px system-ui';for(const word of words){if(ctx.measureText(ln+word).width>w-split-40){txt(ln,rx,yy,13,res?'#bceee3':'#aec1b7');ln='';yy+=22;if(yy>190)break}ln+=word+' '}if(yy<=190)txt(ln,rx,yy,13,res?'#bceee3':'#aec1b7');
}
canvas.dataset.inputSignature=JSON.stringify({model:k,input});requestAnimationFrame(draw);
}
requestAnimationFrame(draw);
})();
