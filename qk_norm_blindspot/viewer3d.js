(()=>{
 const models=DATA.models_3d||[];if(!models.length)return;
 const root=document.getElementById('models3d');
 for(const m of models){
 const card=document.createElement('article');card.className='card';
 card.innerHTML=`<h3>${m.title}</h3><p class="small">${m.description}</p><canvas style="width:100%;height:420px;background:#101c2b;border-radius:12px;touch-action:none" tabindex="0" role="img" aria-label="${m.title}. Drag to rotate; use arrow keys to rotate and plus or minus to zoom."></canvas><p class="small">Drag to rotate · scroll to zoom · arrow keys / + / − · <button type="button">Reset view</button></p><p class="small">${m.legend}</p><p class="small muted">Conceptual geometry · arbitrary scale · no CFD or particle simulation.</p><p class="small">Related catalog records: ${m.evidence_ids.join(' · ')}</p><a href="assets/3d/${m.key}.glb" download>Download GLB</a>`;
 root.appendChild(card);const c=card.querySelector('canvas'),gl=c.getContext('webgl',{antialias:true});let yaw=-.5,pitch=.65,zoom=1,drag=null;
 if(!gl){c.outerHTML=`<img src="assets/3d/${m.key}.png" alt="${m.title}" style="width:100%">`;continue;}
 function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
 const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,'attribute vec3 position;attribute vec3 color;varying vec3 tint;void main(){gl_Position=vec4(position,1.0);tint=color;}'));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,'precision mediump float;varying vec3 tint;void main(){gl_FragColor=vec4(tint,1.0);}'));gl.linkProgram(program);gl.useProgram(program);gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);
 const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
 for(const [name,offset] of [['position',0],['color',12]]){const loc=gl.getAttribLocation(program,name);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,3,gl.FLOAT,false,24,offset);}
 function draw(){
 const ratio=Math.min(globalThis.devicePixelRatio||1,2);c.width=Math.max(280,c.clientWidth)*ratio;c.height=420*ratio;
 const w=c.width,h=c.height;
 const rotated=m.mesh.vertices.map(([x,y,z])=>{
   const a=x*Math.cos(yaw)-y*Math.sin(yaw), b=x*Math.sin(yaw)+y*Math.cos(yaw);
   return [a,-(z*Math.cos(pitch)+b*Math.sin(pitch)),b*Math.cos(pitch)-z*Math.sin(pitch)];
 });
 const xs=rotated.map(p=>p[0]),ys=rotated.map(p=>p[1]);
 const left=Math.min(...xs),right=Math.max(...xs),top=Math.min(...ys),bottom=Math.max(...ys);
 const scale=Math.min(w*.86/(right-left||1),h*.82/(bottom-top||1))*zoom;
 const vs=rotated.map(([x,y,z])=>[w/2+(x-(left+right)/2)*scale,h/2+(y-(top+bottom)/2)*scale,z]);
 gl.viewport(0,0,w,h);gl.clearColor(.063,.11,.17,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);const vertices=[];const depths=vs.map(p=>p[2]),near=Math.min(...depths),far=Math.max(...depths);
 const fs=m.mesh.faces.map(f=>({f,d:(vs[f[0]][2]+vs[f[1]][2]+vs[f[2]][2])/3})).sort((a,b)=>b.d-a.d);
 for(const {f} of fs){
   const p=f.slice(0,3).map(i=>vs[i]);
   const [a,b,d]=f.slice(0,3).map(i=>m.mesh.vertices[i]);
   const u=b.map((x,i)=>x-a[i]),v=d.map((x,i)=>x-a[i]);
   const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
   const len=Math.hypot(...n)||1,light=.68+.32*Math.max(0,(n[0]*.3-n[1]*.5+n[2]*.81)/len);
   const color=f[3].map(x=>Math.min(1,Math.pow(x,.7)*light+.03));
   for(const v of p)vertices.push(v[0]/w*2-1,1-v[1]/h*2,((v[2]-near)/(far-near||1)*2-1)*.9,...color);

 }
 gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(vertices),gl.DYNAMIC_DRAW);gl.drawArrays(gl.TRIANGLES,0,vertices.length/6);
 }
 c.onpointerdown=e=>{drag=[e.clientX,e.clientY];c.setPointerCapture(e.pointerId)};c.onpointermove=e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.009;pitch=Math.max(-1.4,Math.min(1.4,pitch+(e.clientY-drag[1])*.009));drag=[e.clientX,e.clientY];draw()};c.onpointerup=c.onpointercancel=()=>drag=null;
 c.onwheel=e=>{e.preventDefault();zoom=Math.max(.5,Math.min(2.5,zoom*Math.exp(-e.deltaY*.001)));draw()};
 c.onkeydown=e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','-','='].includes(e.key))return;e.preventDefault();yaw+=e.key==='ArrowLeft'?-.12:e.key==='ArrowRight'?.12:0;pitch+=e.key==='ArrowUp'?.12:e.key==='ArrowDown'?-.12:0;zoom=Math.max(.5,Math.min(2.5,zoom*(e.key==='-'?.9:['+','='].includes(e.key)?1.1:1)));draw()};card.querySelector('button').onclick=()=>{yaw=-.5;pitch=.65;zoom=1;draw()};new ResizeObserver(draw).observe(c);draw();
 }
})();
