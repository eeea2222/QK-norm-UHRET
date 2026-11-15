(()=>{
 const host=document.getElementById('ai-playground');
 const presets=DATA.ai_presets;if(!host||!presets)return;
 host.innerHTML=`<div class="ai-shell"><div class="ai-tabs" role="group" aria-label="Model seçimi"><button type="button" data-model="a"><span class="ai-icon">A</span><b>Alev hızı</b><small>PMMA · mm/s</small></button><button type="button" data-model="b"><span class="ai-icon">B</span><b>Görüntü analizi</b><small>Saffire-I · mm</small></button><button type="button" data-model="c"><span class="ai-icon">C</span><b>Dedektör yanıtı</b><small>SAME · 2.0 V</small></button><button type="button" data-model="wt4"><span class="ai-icon">✦</span><b>Metin üret</b><small>WeightSeek WT4</small></button></div><select id="ai-model" hidden aria-label="Model"><option value="a">Model A</option><option value="b">Model B</option><option value="c">Model C</option><option value="wt4">WT4</option></select><div class="ai-workspace"><div class="ai-input-side"><div class="ai-step">01 <b>Bir örnek seç</b></div><div id="ai-chips" class="ai-chips"></div><select id="ai-preset" hidden aria-label="Hazır deneme"></select><button id="ai-fill" type="button" hidden>Örneği yükle</button><p id="ai-description" class="small muted"></p><form id="ai-form"><div id="ai-primary"></div><details id="ai-settings"><summary>Girdileri düzenle</summary><div id="ai-fields" class="ai-fields"></div></details><div class="ai-action"><button id="ai-run" type="submit"><span>▶</span> Modeli çalıştır</button><span id="ai-state" role="status" aria-live="polite"></span></div></form></div><div class="ai-output-side"><div class="ai-step">02 <b>Model sonucu</b></div><div id="ai-result" aria-live="polite"><div class="ai-empty"><span>✦</span><p>İlk denemeni başlat</p><small>Sonuç burada görünecek</small></div></div><details id="ai-raw" hidden><summary>Teknik yanıt · JSON</summary><pre id="ai-json"></pre></details></div></div></div>`;
 const $=id=>document.getElementById(id), model=$('ai-model'),preset=$('ai-preset'),fields=$('ai-fields'),form=$('ai-form');let current,busy=false;
 const descriptions={a:'PMMA levhanın alev yayılma hızını tahmin et.',b:'Hazır Saffire-I karesinde alev sırtını ölç.',c:'Saçılma sinyali 2.0 V eşiğine ulaşır mı?',wt4:'Bir istek yaz veya hazır örnekle başla.'};
 const labels={thickness_mm:'Kalınlık (mm)',width_cm:'Genişlik (cm)',velocity_cm_s:'Hava hızı (cm/s)',initial_o2_vol_pct:'Başlangıç O₂ (hacim %)',airflow_cm_s:'Hava akışı (cm/s)',resistance_ratio:'Direnç oranı',heating_s:'Isıtma (s)',aging_s:'Yaşlandırma (s)',mixing_s:'Karıştırma (s)',max_new_tokens:'En fazla yeni token'};
 function load(){host.aiResult=null;current=structuredClone(presets[model.value][Number(preset.value)||0].input);host.aiInput=current;fields.replaceChildren();$('ai-primary').replaceChildren();$('ai-result').innerHTML='<div class="ai-empty"><span>✦</span><p>İlk denemeni başlat</p><small>Sonuç burada görünecek</small></div>';$('ai-raw').hidden=true;$('ai-state').textContent='';$('ai-description').textContent=descriptions[model.value];host.querySelectorAll('[data-model]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.model===model.value?'true':'false'));host.querySelectorAll('[data-preset]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.preset===preset.value?'true':'false'));$('ai-settings').open=false;
 for(const [k,v] of Object.entries(current)){
 if(k==='units'||(model.value==='a'&&k==='material'))continue;
 const label=document.createElement('label');label.textContent=labels[k]||(k==='prompt'?'İstek':k==='material'?'Malzeme':k);
 let input;if(k==='prompt'){input=document.createElement('textarea');input.rows=3;input.maxLength=6000;label.style.gridColumn='1 / -1'}else if(k==='material'){input=document.createElement('select');for(const mat of ['Kapton','Teflon','Lampwick','Pyrell','Silicone']){const o=document.createElement('option');o.value=o.textContent=mat;input.appendChild(o)}}else{input=document.createElement('input');input.type='number';input.step='any';if(k==='max_new_tokens'){input.min='1';input.max='512';input.step='1'}}input.name=k;input.value=v;input.required=true;input.addEventListener('input',()=>{host.aiInput[k]=input.type==='number'?Number(input.value):input.value;host.aiResult=null;$('ai-result').replaceChildren();$('ai-state').textContent='';$('ai-raw').hidden=true});label.appendChild(input);(k==='prompt'?$('ai-primary'):fields).appendChild(label);
 }
 if(model.value==='b'){const note=document.createElement('p');note.textContent='NASA mapped C1 · SIBAL · gerçek örnek kare';fields.appendChild(note)}
 }
 function choose(){$('ai-chips').replaceChildren();preset.replaceChildren();presets[model.value].forEach((p,i)=>{const o=document.createElement('option');o.value=i;o.textContent=p.label;preset.appendChild(o);const chip=document.createElement('button');chip.type='button';chip.dataset.preset=i;chip.textContent=p.label.replace(' · kayıtlı koşul','').replace(' · düzenlenmiş deneme','').replace(' · hızlı test','');chip.onclick=()=>{preset.value=i;load()};$('ai-chips').appendChild(chip)});load()}
 host.querySelectorAll('[data-model]').forEach(button=>button.onclick=()=>{model.value=button.dataset.model;choose()});
 model.onchange=choose;preset.onchange=load;$('ai-fill').onclick=load;
 form.onsubmit=async e=>{e.preventDefault();if(busy)return;if(location.protocol==='file:'){$('ai-state').textContent='Canlı test için http://127.0.0.1:8005/ adresini açın.';return}
 const selected=model.value,payload=structuredClone(current);for(const el of form.querySelectorAll('[name]'))payload[el.name]=el.type==='number'?Number(el.value):el.value;
 const controls=[...host.querySelectorAll('button,select,input,textarea')];controls.forEach(el=>el.disabled=true);busy=true;host.setAttribute('aria-busy','true');$('ai-run').innerHTML='<span class="ai-spinner"></span> Çalışıyor';$('ai-state').textContent='Çalışıyor…';$('ai-result').replaceChildren();$('ai-raw').hidden=true;
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),180000);
 try{const url=selected==='b'?'/models/b/sample':selected==='wt4'?'/models/wt4/generate':'/models/'+selected;const response=await fetch(url,{method:selected==='b'?'GET':'POST',headers:{'Content-Type':'application/json'},body:selected==='b'?undefined:JSON.stringify(payload),signal:controller.signal});const data=await response.json();if(!response.ok)throw Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail||data));
 host.aiResult=data;$('ai-json').textContent=JSON.stringify(data,null,2);$('ai-raw').hidden=false;const output=document.createElement('div');output.className='ai-answer';
 const number=(value,digits=2)=>value.toLocaleString('tr-TR',{maximumFractionDigits:digits});
 const headline=document.createElement('strong'),note=document.createElement('p'),kind=document.createElement('small');
 kind.textContent='Model tahmini · predicted';
 if(selected==='a'){
   const rate=data.response.predicted_flame_spread_rate;
   headline.textContent=number(rate,5)+' mm/s';
   note.textContent=`Model, seçilen PMMA levhada alevin bu hız sabit kalırsa 10 saniyede yaklaşık ${number(rate*10,3)} mm ilerleyeceğini tahmin ediyor.`;
   if(data.response.out_of_distribution)note.textContent+=' Girdi, modelin çalışma aralığı dışında.';
 }else if(selected==='b'){
   const pos=data.response.value;
   headline.textContent=Number.isFinite(pos)?number(pos)+' mm':'Konum hesaplanamadı';
   note.textContent=Number.isFinite(pos)?'Çizgi, modelin bu karede alevin parlak sırtını görüntünün sol kenarından ne kadar uzakta bulduğunu gösteriyor.':'Bu kareden geçerli bir konum elde edilemedi.';
 }else if(selected==='c'){
   const reached=data.predicted_alarm_level_reached,near=data.nearest_measured_experiment;
   headline.textContent='2,0 V eşiğine '+(reached?'ulaşır':'ulaşmaz');
   note.textContent=`Model ${payload.material} dumanı için ışık saçılma sinyalini sınıflandırıyor. `;
   if(Number.isFinite(near?.iss_scatter_v))note.textContent+=`En yakın testte (${near.test_id}) ${number(near.iss_scatter_v,3)} V ölçüldü. Ölçüm eşiğin ${near.iss_scatter_v>=2?(near.iss_scatter_v===2?'tam üzerinde':'üzerinde'):'altında'} ve tahminle ${(near.iss_scatter_v>=2)===reached?'uyumlu':'uyumsuz'}.`;
   kind.textContent='Eşik tahmini · predicted · Gerçek alarm kaydı içermez'+(data.ood?' · Girdi kapsam dışında':'');
 }else{
   headline.textContent=data.generation.text;
   headline.style.whiteSpace='pre-wrap';
   kind.textContent='Üretilen metin';
   note.textContent='WT4, yazdığınız isteğe bir yanıt üretti. Bilimsel iddialar ayrıca kaynak kontrolü gerektirir.';
 }
 output.append(kind,headline,note);$('ai-result').appendChild(output);$('ai-state').textContent='Tamamlandı';
 }catch(err){$('ai-state').textContent='Hata: '+(err.name==='AbortError'?'İstek zaman aşımına uğradı.':err.message)}finally{clearTimeout(timer);controls.forEach(el=>el.disabled=false);busy=false;host.setAttribute('aria-busy','false');$('ai-run').innerHTML='<span>▶</span> Modeli çalıştır'}
 };const query=new URLSearchParams(location.search);if(Object.hasOwn(presets,query.get('model')))model.value=query.get('model');choose();const requested=Number(query.get('sample'));if(query.has('sample')&&Number.isInteger(requested)&&requested>=0&&requested<presets[model.value].length){preset.value=requested;load()}

})();
