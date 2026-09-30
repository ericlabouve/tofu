import fs from 'node:fs';
import assert from 'node:assert/strict';
const source=new URL('../cad/nine-dogs-3x3/measurement-math.js',import.meta.url);
const m=await import('data:text/javascript;base64,'+fs.readFileSync(source).toString('base64'));
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-9,`${a} != ${b}`);
for(const [yaw,pitch] of [[-.9,.72],[-Math.PI/2,Math.PI/2],[0,0],[2,-.7]]){
 for(const [w,h,zoom] of [[1200,650,1],[700,430,2.5],[1000,800,.5]]){
  const axes=m.cameraAxes(yaw,pitch);
  for(const p of [[100,100],[w*.5,h*.5],[w-10,h-20]]){
   const q=m.pointOnViewPlane(...p,axes,w,h,zoom),r=m.projectPoint(q,axes,w,h,zoom);
   close(r[0],p[0]);close(r[1],p[1]);
  }
  const a=m.pointOnViewPlane(10,10,axes,w,h,zoom),b=m.pointOnViewPlane(110,10,axes,w,h,zoom);
  close(m.measurement(a,b).distance,100*250/w/zoom);
 }
}
close(m.measurement([0,0,0],[3,4,12]).distance,13);
const top=m.cameraAxes(-Math.PI/2,Math.PI/2),a=m.projectPoint([-60,0,0],top,1000,650,1),b=m.projectPoint([60,0,0],top,1000,650,1);
close(b[0]-a[0],480);
console.log('Measurement projection, zoom scaling, known 120 mm span, and 3D distance checks passed.');
