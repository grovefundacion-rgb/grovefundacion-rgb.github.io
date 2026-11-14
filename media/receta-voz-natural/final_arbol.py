import numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as nd
from collections import deque
W,H,FPS,DUR=1080,1920,30,7.0
CREMA=(246,238,223); VERDE=(47,93,52); CAFE=(74,44,23); TERRA=(180,83,42); OCRE=(211,154,44)
S=1.4; GROUND=1150
base=np.array(Image.open("logo/img2.png").convert("RGBA")); hojas=np.array(Image.open("logo/img3.png").convert("RGBA"))
def comps(img,minsize=500):
    al=img[...,3]>100; lab,n=nd.label(al,structure=np.ones((3,3)))
    out=[]
    for i in range(1,n+1):
        m=lab==i
        if m.sum()<minsize: continue
        # include antialias fringe: dilate
        md=nd.binary_dilation(m,iterations=2)&(img[...,3]>0)
        out.append(md)
    return out
bc=comps(base); bc.sort(key=lambda m:-m.sum())
trunk=bc[0]
others=bc[1:]
head=min(others,key=lambda m: abs(np.mean(np.where(m)[1])-330)+abs(np.mean(np.where(m)[0])-343))
gleaves=[m for m in others if m is not head]
oleaves=comps(hojas)
# geodesic distance on trunk from base point
ys,xs=np.where(trunk); yb=ys.max(); xb=int(np.mean(xs[ys>=yb-3]))
dist=np.full(trunk.shape,np.inf); q=deque([(yb,xb)]); dist[yb,xb]=0
# start from whole bottom row
for x in xs[ys>=yb-2]: 
    y=ys[ys>=yb-2][0]; 
for y,x in zip(ys[ys>=yb-2],xs[ys>=yb-2]): dist[y,x]=0; q.append((y,x))
while q:
    y,x=q.popleft(); d=dist[y,x]
    for dy,dx,c in ((1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414),(1,-1,1.414),(-1,1,1.414),(-1,-1,1.414)):
        Y,X=y+dy,x+dx
        if 0<=Y<640 and 0<=X<640 and trunk[Y,X] and dist[Y,X]>d+c+1e-6:
            dist[Y,X]=d+c; q.append((Y,X))
maxd=dist[np.isfinite(dist)].max()
def layer(img,mask): 
    a=img.copy(); a[...,3]=np.where(mask,a[...,3],0); return a
trunk_rgba=layer(base,trunk)
def sprite(img,m):
    ys,xs=np.where(m); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    crop=layer(img,m)[y0:y1,x0:x1]
    # pivot: point of sprite closest to trunk base direction (nearest trunk pixel)
    cy,cx=ys.mean(),xs.mean()
    return dict(im=Image.fromarray(crop),x0=x0,y0=y0,cx=cx,cy=cy,r=math.hypot(cx-xb,cy-yb))
gs=[sprite(base,m) for m in gleaves]; os_=[sprite(hojas,m) for m in oleaves]
hs=sprite(base,head)
gs.sort(key=lambda s:s['r']); os_.sort(key=lambda s:s['r'])
OX=540-320*S; OY=GROUND-yb*S
def ease_out_back(t,k=1.9): t=min(max(t,0),1); t-=1; return 1+(k+1)*t**3+k*t**2
def ease_out(t): t=min(max(t,0),1); return 1-(1-t)**3
def ease_in(t): t=min(max(t,0),1); return t*t
fb=ImageFont.truetype("Jost.ttf",86); fb.set_variation_by_name("Bold")
fs=ImageFont.truetype("Jost.ttf",48); fs.set_variation_by_name("Medium")
def paste_scaled(canvas,sp,sc,alpha=1.0):
    if sc<=0.01: return
    im=sp['im']; w,h=im.size
    tw,th=max(1,int(w*S*sc)),max(1,int(h*S*sc))
    im2=im.resize((tw,th),Image.LANCZOS)
    if alpha<1: 
        a=np.array(im2); a[...,3]=(a[...,3]*alpha).astype(np.uint8); im2=Image.fromarray(a)
    cx=OX+sp['cx']*S; cy=OY+sp['cy']*S
    # scale about sprite center
    px=cx+(OX+sp['x0']*S-cx)*sc; py=cy+(OY+sp['y0']*S-cy)*sc
    canvas.alpha_composite(im2,(int(round(px)),int(round(py))))
T_SEED0,T_LAND=0.45,1.35; T_G0,T_G1=1.75,3.35
def frame(t):
    c=Image.new("RGBA",(W,H),CREMA+(255,))
    d=ImageDraw.Draw(c)
    # ground line
    gw=ease_out((t-T_LAND)/0.45)*230
    if gw>1: d.rounded_rectangle((540-gw,GROUND+2,540+gw,GROUND+12),radius=6,fill=VERDE)
    # seed
    if t>=T_SEED0 and t<T_G0+0.35:
        if t<T_LAND:
            p=ease_in((t-T_SEED0)/(T_LAND-T_SEED0)); y=-60+(GROUND-14+60)*p; ang=200*(1-p)+15; sq=1
        else:
            u=t-T_LAND; y=GROUND-14-30*max(0,math.sin(min(u/0.25,1)*math.pi))*(u<0.25); ang=15; sq=1
        sink=min(max((t-T_G0+0.1)/0.4,0),1)
        sw,sh=22*(1-0.6*sink),32*(1-0.6*sink)
        seed=Image.new("RGBA",(120,120),(0,0,0,0)); sd=ImageDraw.Draw(seed)
        sd.ellipse((60-sw,60-sh,60+sw,60+sh),fill=CAFE+(255,)); sd.ellipse((60-sw*0.45,60-sh*0.6,60-sw*0.05,60-sh*0.1),fill=(120,80,45,255))
        seed=seed.rotate(ang,resample=Image.BICUBIC)
        c.alpha_composite(seed,(480,int(y-60+sh*0.6*sink)))
    # trunk growth
    if t>T_G0:
        u=min(max((t-T_G0)/(T_G1-T_G0),0),1); p=(u*u*(3-2*u))*(maxd+14)
        a=np.clip((p-dist)/12.0,0,1); a[~np.isfinite(dist)]=0
        tr=trunk_rgba.copy(); tr[...,3]=(tr[...,3]*a).astype(np.uint8)
        im=Image.fromarray(tr).resize((int(640*S),int(640*S)),Image.LANCZOS)
        c.alpha_composite(im,(int(OX),int(OY)))
    # head
    paste_scaled(c,hs,ease_out_back((t-3.15)/0.45,2.4))
    for i,s in enumerate(gs): paste_scaled(c,s,ease_out_back((t-(3.25+i*0.11))/0.5))
    for i,s in enumerate(os_): paste_scaled(c,s,ease_out_back((t-(4.0+i*0.09))/0.5))
    # text
    a=ease_out((t-4.95)/0.6)
    if a>0:
        txt=Image.new("RGBA",(W,H),(0,0,0,0)); td=ImageDraw.Draw(txt)
        dy=int(30*(1-a))
        td.text((540,GROUND+120+dy),"FUNDACIÓN GROVE",font=fb,fill=VERDE+(255,),anchor="mm")
        td.text((540,GROUND+215+dy),"@fundacion.grove",font=fs,fill=TERRA+(255,),anchor="mm")
        arr=np.array(txt); arr[...,3]=(arr[...,3]*a).astype(np.uint8); c.alpha_composite(Image.fromarray(arr))
    return c.convert("RGB")
if len(sys.argv)>1:
    for t in map(float,sys.argv[1:]): frame(t).save(f"outro_{t}.png")
else:
    out=sys.stdout.buffer
    for i in range(int(DUR*FPS)): out.write(frame(i/FPS).tobytes())
