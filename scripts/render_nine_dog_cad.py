"""Headless CPU depth-buffer renders of the exported mesh; no display server."""
from pathlib import Path
import numpy as np
import trimesh
from numba import njit
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'cad/nine-dogs-3x3'
@njit
def raster(v,faces,colors,width,height):
    image=np.empty((height,width,3),dtype=np.uint8);image[:]=np.array([250,247,240],dtype=np.uint8)
    depth=np.full((height,width),-1e30)
    for k in range(len(faces)):
        a,b,c=v[faces[k,0]],v[faces[k,1]],v[faces[k,2]]
        xmin=max(0,int(np.floor(min(a[0],b[0],c[0]))));xmax=min(width-1,int(np.ceil(max(a[0],b[0],c[0]))))
        ymin=max(0,int(np.floor(min(a[1],b[1],c[1]))));ymax=min(height-1,int(np.ceil(max(a[1],b[1],c[1]))))
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-12:continue
        for y in range(ymin,ymax+1):
            for x in range(xmin,xmax+1):
                u=((b[1]-c[1])*(x+.5-c[0])+(c[0]-b[0])*(y+.5-c[1]))/den
                w=((c[1]-a[1])*(x+.5-c[0])+(a[0]-c[0])*(y+.5-c[1]))/den
                t=1-u-w
                if u>=0 and w>=0 and t>=0:
                    z=u*a[2]+w*b[2]+t*c[2]
                    if z>depth[y,x]:depth[y,x]=z;image[y,x]=colors[k]
    return image
mesh=trimesh.load(OUT/'nine-dogs-3x3.stl',force='mesh')
vertices=mesh.vertices-np.array([0,0,18]);normals=mesh.face_normals
views=[('perspective',[1,-1.5,1.3],[0,0,1]),('top',[0,0,1],[0,1,0]),('cutting-edge',[1,-1.5,-1.2],[0,0,-1]),('side',[1,-1.5,.32],[0,0,1])]
for name,eye,up in views:
    eye=np.array(eye,dtype=float);eye/=np.linalg.norm(eye)
    right=np.cross(up,eye);right/=np.linalg.norm(right);vertical=np.cross(eye,right)
    v=vertices@np.stack([right,vertical,eye],axis=1)
    scale=min(1300/np.ptp(v[:,0]),900/np.ptp(v[:,1]));v[:,:2]*=scale;v[:,0]+=750;v[:,1]=550-v[:,1]
    light=eye+.4*vertical-.5*right;light/=np.linalg.norm(light)
    brightness=.4+.6*np.maximum(0,normals@light)
    colors=np.clip(brightness[:,None]*np.array([104,171,143])[None,:],0,255).astype(np.uint8)
    img=raster(v,mesh.faces,colors,1500,1100)
    Image.fromarray(img).save(OUT/(name+'.png'));print('Rendered',name,flush=True)
# GPU preview data: positions and smooth normals followed by triangle indices.
n=len(mesh.vertices);f=len(mesh.faces)
with open(OUT/'preview.bin','wb') as out:
    out.write(np.array([n,f],dtype='<u4').tobytes());out.write(mesh.vertices.astype('<f4').tobytes());out.write(mesh.vertex_normals.astype('<f4').tobytes());out.write(mesh.faces.astype('<u4').tobytes())
print('Preview binary exported.')
