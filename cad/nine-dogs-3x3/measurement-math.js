// Model units are millimetres. Camera axes match the orthographic WebGL shader.
export function cameraAxes(yaw,pitch){
 const sy=Math.sin(yaw),cy=Math.cos(yaw),sp=Math.sin(pitch),cp=Math.cos(pitch);
 return {right:[-sy,cy,0],up:[-sp*cy,-sp*sy,cp],eye:[cp*cy,cp*sy,sp]};
}
export function projectPoint(p,axes,width,height,zoom){
 const q=[p[0],p[1],p[2]-18],dot=a=>q.reduce((s,v,i)=>s+v*a[i],0);
 return [(dot(axes.right)*zoom/125+1)*width/2,(1-dot(axes.up)*zoom*width/height/125)*height/2];
}
export function pointOnViewPlane(x,y,axes,width,height,zoom){
 const u=(x/width*2-1)*125/zoom,v=(1-y/height*2)*125/zoom*height/width;
 return axes.right.map((r,i)=>r*u+axes.up[i]*v+(i===2?18:0));
}
export function measurement(a,b){const delta=b.map((v,i)=>v-a[i]);return {delta,distance:Math.hypot(...delta)};}
