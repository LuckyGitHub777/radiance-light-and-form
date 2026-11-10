'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const html=fs.readFileSync(path.resolve(__dirname,'../light-room.html'),'utf8');
const homepage=fs.readFileSync(path.resolve(__dirname,'../index.html'),'utf8');
assert.equal(homepage,html,'Shareable homepage must be the full Light Room, not a redirect');
const match=html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match,'Inline script required');
class E {
 constructor(id='',attrs={}){this.id=id;this.attrs={...attrs};this.events={};this.children=[];this.css={};this.style={setProperty:(k,v)=>this.css[k]=v};this.classes=new Set();this.hidden=false;this.disabled=false;this.textContent='';}
 get classList(){return {add:(...a)=>a.forEach(v=>this.classes.add(v)),remove:(...a)=>a.forEach(v=>this.classes.delete(v)),contains:v=>this.classes.has(v),toggle:(v,f)=>{const next=f===undefined?!this.classes.has(v):f;next?this.classes.add(v):this.classes.delete(v);return next;}}}
 setAttribute(k,v){this.attrs[k]=String(v);if(k==='class')this.classes=new Set(String(v).split(' '))}
 getAttribute(k){return this.attrs[k]??null}
 addEventListener(k,f){(this.events[k]??=[]).push(f)}
 dispatch(k,arg){for(const fn of this.events[k]??[])fn.call(this,arg)}
 click(){this.dispatch('click')}
 focus(){this.ownerDocument.activeElement=this;this.dispatch('focus')}
 appendChild(el){this.children.push(el)}
}
function check(fullscreen,protocol){
 const els={},btns=[],frames=new Map(),timers=new Map();let fid=0,tid=0;
 const make=(name='',attrs={})=>{const e=new E(name,attrs);if(name)els[name]=e;return e};
 const room=make('room');
 const groups=[
  ['scene',['pyramid','halo','bloom','flower','cube','prism'],'pyramid'],
  ['color',['spectrum','aurum','aurora','ocean','violet','rose'],'spectrum'],
  ['power',['soft','balanced','radiant'],'radiant'],
  ['pattern',['linear','organic'],'linear'],
  ['speed',['flow','vivid','surge'],'surge']
 ];
 const ids=['motion','hide-ui','restore-ui','fullscreen','offline-download',
 ...groups[0][1].map(v=>'scene-'+v),
 ...['pyramid-left','pyramid-right','halo','bloom','flower','cube-top','cube-left','cube-right','prism'].map(v=>'field-'+v)];
 ids.forEach(v=>make(v));
 for(const [type,values,selected] of groups)
  for(const value of values)btns.push(make('',{['data-'+type]:value,'aria-pressed':String(value===selected)}));
 const doc={hidden:false,activeElement:null,fullscreenElement:null,events:{},
  getElementById:id=>els[id]??null,createElementNS:()=>new E(),
  querySelectorAll:selector=>{const keys=[...selector.matchAll(/\[data-([a-z]+)\]/g)].map(m=>'data-'+m[1]);return btns.filter(b=>keys.some(k=>b.getAttribute(k)!==null))},
  addEventListener(k,f){(this.events[k]??=[]).push(f)},
  dispatch(k,p){for(const f of this.events[k]??[])f(p)}
 };
 Object.values(els).forEach(el=>el.ownerDocument=doc);
 const media={matches:false,addEventListener(k,f){this.change=f}};
 const win={location:{protocol},matchMedia:()=>media,
  requestAnimationFrame(f){const n=++fid;frames.set(n,f);return n},
  cancelAnimationFrame(n){frames.delete(n)},
  setTimeout(f,delay){const n=++tid;timers.set(n,{f,delay});return n},
  clearTimeout(n){timers.delete(n)}
 };
 if(fullscreen)room.requestFullscreen=()=>{doc.fullscreenElement=room;doc.dispatch('fullscreenchange');return {catch(){}}};
 vm.runInNewContext(match[1],{document:doc,window:win},{timeout:5000,filename:'radiance-inline.js'});
 const choose=(k,v)=>{const b=btns.find(e=>e.getAttribute('data-'+k)===v);assert.ok(b);b.click();assert.equal(b.getAttribute('aria-pressed'),'true')};
 assert.ok(room.classes.has('moving')&&room.classes.has('speed-surge')&&room.classes.has('power-radiant'));
 assert.equal(els['field-flower'].children.length,43);
 for(const face of ['top','left','right'])assert.equal(els['field-cube-'+face].children.length,33);

 // The field has continuous vertical coverage at every phase, even on smaller forms.
 const bounds={
  'pyramid-left':[74,423,20],'pyramid-right':[74,423,20],
  'halo':[77,463,23],'bloom':[56,484,22],'flower':[34,506,23],
  'cube-top':[132,310,6],'cube-left':[221,470,8],
  'cube-right':[221,470,8],'prism':[74,450,20]
 };
 for(const [name,[low,high,minimum]] of Object.entries(bounds)){
  const children=els['field-'+name].children;
  assert.equal(children[0].getAttribute('class'),'light-carrier',name+' persistent carrier');
  assert.equal(children[1].getAttribute('class'),'light-carrier');
  assert.equal(children[2].getAttribute('class'),'light-carrier');
  const count=children.length-3;
  const spacing=690/count;
  assert.ok(count>0);
  for(let phase=0;phase<690;phase+=2.5){
    let active=0;
    for(let i=0;i<count;i++){
      const y=((i*spacing+phase)%690)-92;
      if(y>=low&&y<=high)active++;
    }
    assert.ok(active>=minimum,name+' continuous rows at phase '+phase);
  }
 }
 for(const name of groups[0][1]){choose('scene',name);assert.equal(els['scene-'+name].getAttribute('class'),'scene active')}
 choose('pattern','organic');assert.ok(room.classes.has('pattern-organic'));choose('pattern','linear');
 choose('color','violet');assert.equal(room.css['--hue-a'],'#cfb8f7');choose('color','spectrum');
 choose('power','soft');choose('power','radiant');
 for(const v of ['flow','vivid','surge'])choose('speed',v);
 assert.equal(els.fullscreen.disabled,!fullscreen);
 if(fullscreen){els.fullscreen.click();assert.ok(room.classes.has('full-visual'))}
 els['hide-ui'].click();assert.ok(room.classes.has('quiet-mode')&&!room.classes.has('ui-awake'));
 room.dispatch('pointermove');assert.ok(room.classes.has('ui-awake'));
 const timer=[...timers.values()].at(-1);assert.equal(timer.delay,1800);timer.f();assert.ok(!room.classes.has('ui-awake'));
 room.dispatch('pointermove');els['restore-ui'].click();assert.ok(!room.classes.has('quiet-mode'));
 els['hide-ui'].click();doc.dispatch('keydown',{key:'Escape'});assert.ok(!room.classes.has('quiet-mode'));
 els.motion.click();assert.ok(!room.classes.has('moving')&&!frames.size);
 els.motion.click();assert.ok(room.classes.has('moving')&&frames.size);
 doc.hidden=true;doc.dispatch('visibilitychange');assert.ok(!room.classes.has('moving')&&!frames.size);
 doc.hidden=false;doc.dispatch('visibilitychange');assert.ok(room.classes.has('moving'));
 media.matches=true;media.change();assert.ok(!room.classes.has('moving')&&!frames.size);
 media.matches=false;media.change();assert.ok(room.classes.has('moving'));
 if(protocol==='file:')assert.equal(els['offline-download'].hidden,true);
 else assert.equal(els['offline-download'].hidden,false);
 return {fullscreen,protocol,status:'PASS'};
}
console.log(JSON.stringify({smoke:[check(true,'https:'),check(false,'https:'),check(true,'file:')],externalDependencies:0}));
