// Execute dashboard render against a minimal DOM to catch missing fields and JS errors.
const fs = require('fs');
const vm = require('vm');
const html = fs.readFileSync('dashboard/index.html','utf8');
const context = {devicePixelRatio:1,ResizeObserver:class{observe(){}},document:{documentElement:{getAttribute:()=>null,setAttribute:()=>{}}},matchMedia:()=>({matches:false})};
const canvas={clientWidth:400,getContext:()=>null};
context.document.createElement=()=>({querySelector:q=>q==='canvas'?canvas:{},innerHTML:''});
context.document.getElementById=id=>id==='ai-playground'?null:({appendChild(){}});
for(const match of html.matchAll(/id="([^"]+)"/g)) context[match[1]]={innerHTML:'',textContent:''};
vm.runInNewContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context,{timeout:10000});
for(const id of ['flow','example','verified','chronology','comparisons','gaps','priorities','sources','side']) {
 if(!context[id].innerHTML) throw Error('Empty dashboard section: '+id);
}
console.log('Dashboard render passed (9 populated sections)');
