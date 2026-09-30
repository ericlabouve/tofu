import {cameraAxes,projectPoint,pointOnViewPlane,measurement} from './measurement-math.js';
const canvas=document.getElementById('view'),status=document.getElementById('status'),overlay=document.getElementById('measure-overlay'),readout=document.getElementById('measure-result'),kind=document.getElementById('measure-kind');
const gl=canvas.getContext('webgl2',{antialias:true});
let yaw=-.9,pitch=.72,zoom=1,count=0,drag=null,mode='rotate',start=null,end=null,savedKind='surface',pickDirty=true,pickSize=[0,0],pickReady=false;
const $=id=>document.getElementById(id);
function message(){status.textContent=mode==='rotate'?'Drag to rotate · scroll to zoom':kind.value==='surface'?'Drag between two visible surfaces · Escape clears':'Drag anywhere to measure in the current view plane · Escape clears';}
function drawMeasurement(){
 overlay.replaceChildren();const w=canvas.clientWidth,h=canvas.clientHeight;overlay.setAttribute('viewBox',`0 0 ${w} ${h}`);
 if(!start){readout.textContent='No measurement';return;}
 const ns='http://www.w3.org/2000/svg',axes=cameraAxes(yaw,pitch),a=projectPoint(start,axes,w,h,zoom),b=end?projectPoint(end,axes,w,h,zoom):null;
 function el(name,attrs){const n=document.createElementNS(ns,name);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);overlay.append(n);return n;}
 if(b){el('line',{x1:a[0],y1:a[1],x2:b[0],y2:b[1],stroke:'#8b244b','stroke-width':2,'stroke-dasharray':'5 3'});const m=measurement(start,end),label=`${m.distance.toFixed(2)} mm`;const tx=Math.max(55,Math.min(w-55,(a[0]+b[0])/2)),ty=Math.max(24,Math.min(h-12,(a[1]+b[1])/2-12));el('rect',{x:tx-53,y:ty-18,width:106,height:25,rx:5,fill:'#fffdf8',stroke:'#8b244b'});el('text',{x:tx,y:ty,'text-anchor':'middle',fill:'#8b244b','font-size':14,'font-weight':700}).textContent=label;
 readout.textContent=`${label} · ${savedKind==='surface'?'3D straight-line distance':'View-plane distance'} · ΔX ${Math.abs(m.delta[0]).toFixed(2)} · ΔY ${Math.abs(m.delta[1]).toFixed(2)} · ΔZ ${Math.abs(m.delta[2]).toFixed(2)} mm`;
 }else readout.textContent='Start point selected — drag to the second point';
 for(const p of [a,b].filter(Boolean)){el('circle',{cx:p[0],cy:p[1],r:5,fill:'#fffdf8',stroke:'#8b244b','stroke-width':2});}
}
function clear(){start=end=null;drawMeasurement();message();}
if(!gl){status.textContent='Interactive preview unavailable. Use the rendered views below.';document.querySelectorAll('.measurement-controls button,.measurement-controls select').forEach(b=>b.disabled=true);}else{
 function shader(type,src){const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
 const vs=`#version 300 es
 layout(location=0) in vec3 position;layout(location=1) in vec3 normal;uniform mat3 camera;uniform vec2 scale;out vec3 n;out vec3 world;void main(){vec3 p=camera*(position-vec3(0,0,18));gl_Position=vec4(p.x*scale.x,p.y*scale.y,-p.z/250.,1);n=camera*normal;world=position;}`;
 function program(fragment){const p=gl.createProgram();gl.attachShader(p,shader(gl.VERTEX_SHADER,vs));gl.attachShader(p,shader(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));return p;}
 const prog=program(`#version 300 es
 precision highp float;in vec3 n;out vec4 color;void main(){float l=.40+.60*max(dot(normalize(n),normalize(vec3(-.5,.7,1))),0.);color=vec4(vec3(.40,.67,.55)*l,1);}`);
 const floatPicking=!!gl.getExtension('EXT_color_buffer_float');
 const pickProg=floatPicking?program(`#version 300 es
 precision highp float;in vec3 world;out vec4 color;void main(){color=vec4(world,1);}`):null;
 if(!floatPicking){kind.querySelector('[value=surface]').disabled=true;kind.value='plane';$('measure-help').textContent='Surface picking is unavailable in this browser. View-plane mode measures projected distances; use Top for plan dimensions.';}
 const fbo=gl.createFramebuffer(),tex=gl.createTexture(),depth=gl.createRenderbuffer();gl.enable(gl.DEPTH_TEST);
 function uniforms(p){gl.useProgram(p);const a=cameraAxes(yaw,pitch);gl.uniformMatrix3fv(gl.getUniformLocation(p,'camera'),false,new Float32Array([a.right[0],a.up[0],a.eye[0],a.right[1],a.up[1],a.eye[1],a.right[2],a.up[2],a.eye[2]]));gl.uniform2f(gl.getUniformLocation(p,'scale'),zoom/125,zoom*canvas.width/canvas.height/125);}
 function render(){const d=Math.min(devicePixelRatio,2),w=Math.round(canvas.clientWidth*d),h=Math.round(canvas.clientHeight*d);if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;pickDirty=true;}gl.bindFramebuffer(gl.FRAMEBUFFER,null);gl.viewport(0,0,w,h);gl.clearColor(250/255,247/255,240/255,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);uniforms(prog);gl.drawElements(gl.TRIANGLES,count,gl.UNSIGNED_INT,0);drawMeasurement();}
 function preparePick(){
  if(!pickProg||!count)return false;
  if(!pickDirty)return pickReady;
  gl.bindFramebuffer(gl.FRAMEBUFFER,fbo);
  if(pickSize[0]!==canvas.width||pickSize[1]!==canvas.height){gl.bindTexture(gl.TEXTURE_2D,tex);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA32F,canvas.width,canvas.height,0,gl.RGBA,gl.FLOAT,null);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,tex,0);gl.bindRenderbuffer(gl.RENDERBUFFER,depth);gl.renderbufferStorage(gl.RENDERBUFFER,gl.DEPTH_COMPONENT24,canvas.width,canvas.height);gl.framebufferRenderbuffer(gl.FRAMEBUFFER,gl.DEPTH_ATTACHMENT,gl.RENDERBUFFER,depth);pickSize=[canvas.width,canvas.height];}
  pickReady=gl.checkFramebufferStatus(gl.FRAMEBUFFER)===gl.FRAMEBUFFER_COMPLETE;
  if(pickReady){gl.viewport(0,0,canvas.width,canvas.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);uniforms(pickProg);gl.drawElements(gl.TRIANGLES,count,gl.UNSIGNED_INT,0);pickDirty=false;}
  gl.bindFramebuffer(gl.FRAMEBUFFER,null);return pickReady;
 }
 function pick(e){const r=canvas.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;if(x<0||y<0||x>=r.width||y>=r.height)return null;
  if(kind.value==='plane')return pointOnViewPlane(x,y,cameraAxes(yaw,pitch),r.width,r.height,zoom);
  if(!preparePick())return null;
  const pixel=new Float32Array(4);gl.bindFramebuffer(gl.FRAMEBUFFER,fbo);gl.readPixels(Math.floor(x/r.width*canvas.width),canvas.height-1-Math.floor(y/r.height*canvas.height),1,1,gl.RGBA,gl.FLOAT,pixel);gl.bindFramebuffer(gl.FRAMEBUFFER,null);return pixel[3]>.5?Array.from(pixel.slice(0,3)):null;
 }
 fetch('preview.bin').then(r=>{if(!r.ok)throw Error('Preview file missing');return r.arrayBuffer()}).then(b=>{const h=new Uint32Array(b,0,2),n=h[0];count=h[1]*3;for(const [loc,offset] of [[0,8],[1,8+n*12]]){gl.bindBuffer(gl.ARRAY_BUFFER,gl.createBuffer());gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(b,offset,n*3),gl.STATIC_DRAW);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,3,gl.FLOAT,false,0,0);}gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,gl.createBuffer());gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint32Array(b,8+n*24,count),gl.STATIC_DRAW);document.querySelectorAll('.measurement-controls button,.measurement-controls select').forEach(b=>b.disabled=false);message();render();}).catch(e=>status.textContent=e.message+' — rendered views are available below.');
 canvas.onpointerdown=e=>{if(e.button!==0||!count)return;if(mode==='measure'){const p=pick(e);if(!p){status.textContent='Start on a visible model surface, or choose View plane for gaps.';return;}start=p;end=null;savedKind=kind.value;drawMeasurement();}drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);e.preventDefault();};
 canvas.onpointermove=e=>{if(!drag)return;if(mode==='measure'){end=pick(e);drawMeasurement();status.textContent=end?'Release to keep this measurement':'End on a visible surface, or use View plane to measure across empty space.';}else{yaw-=(e.clientX-drag[0])*.008;pitch=Math.max(-Math.PI/2,Math.min(Math.PI/2,pitch+(e.clientY-drag[1])*.008));drag=[e.clientX,e.clientY];pickDirty=true;render();}};
 canvas.onpointerup=e=>{if(!drag)return;if(mode==='measure'){end=pick(e);drawMeasurement();if(!end)status.textContent='No endpoint selected. Drag again between visible surfaces.';else message();}drag=null;};canvas.onpointercancel=()=>{drag=null;if(mode==='measure')clear();};
 canvas.addEventListener('wheel',e=>{e.preventDefault();if(drag)return;zoom=Math.max(.5,Math.min(6,zoom*Math.exp(-e.deltaY*.001)));pickDirty=true;render();},{passive:false});
 window.addEventListener('resize',()=>{pickDirty=true;render();});document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{[yaw,pitch]={perspective:[-.9,.72],top:[-Math.PI/2,Math.PI/2],edge:[-.9,-.72],side:[-.9,.15]}[b.dataset.view];zoom=1;pickDirty=true;render();});
 document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.mode;drag=null;canvas.style.cursor=mode==='measure'?'crosshair':'grab';document.querySelectorAll('[data-mode]').forEach(v=>v.setAttribute('aria-pressed',String(v.dataset.mode===mode)));message();});
 kind.onchange=clear;$('clear-measurement').onclick=clear;window.addEventListener('keydown',e=>{if(e.key==='Escape'){drag=null;clear();}});
}
