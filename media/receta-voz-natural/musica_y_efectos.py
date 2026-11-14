import numpy as np
from scipy.signal import butter, sosfilt
SR=48000; TOTAL=62.6; N=int(TOTAL*SR)
rng=np.random.default_rng(7)
def bp(x,lo,hi,o=2): return sosfilt(butter(o,[lo,hi],'band',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def lp(x,f,o=2): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def tt(d): return np.arange(int(d*SR))/SR
def add(buf,t0,x,g=1.0):
    a=int(t0*SR); 
    if a<0: x=x[-a:]; a=0
    b=min(len(buf),a+len(x)); buf[a:b]+=g*x[:b-a]
def mtof(m): return 440*2**((m-69)/12)
def pluck(f,d=1.6,bright=1.0):
    t=tt(d); x=np.zeros_like(t)
    for k in range(1,9):
        if f*k>12000: break
        x+=np.sin(2*np.pi*f*k*t)*np.exp(-t*(2.2+k*1.8/bright))/k**1.2
    return x*np.minimum(t/0.004,1)
# ---------------- MUSIC (reflexiva, tono menor) ----------------
mus=np.zeros(N)
BPM=70; beat=60/BPM; bar=4*beat
def felt(f,d=4.0,vel=1.0):
    t=tt(d); x=np.zeros_like(t)
    for k,a in zip(range(1,8),[1,.5,.28,.14,.08,.05,.03]):
        x+=a*np.sin(2*np.pi*f*k*(1+0.0003*k*k)*t+rng.uniform(0,6))*np.exp(-t*(0.55+k*0.45))
    x=lp(x,2600)*np.minimum(t/0.012,1)
    return x*vel
def strings(fs,d,att=1.2,rel=1.2,cut=1400):
    t=tt(d); x=np.zeros_like(t)
    vib=1+0.0025*np.sin(2*np.pi*5.2*t)
    for f in fs:
        for det in (-0.08,0.0,0.09):
            ff=f*2**(det/12); ph=2*np.pi*np.cumsum(ff*vib)/SR+rng.uniform(0,6)
            for k in range(1,9): x+=np.sin(k*ph)/k
    env=np.minimum(t/att,1)*np.minimum(np.maximum(d-t,0)/rel,1)
    return lp(x,cut,4)*env/(len(fs)*3)
def heartbeat():
    t=tt(0.6); out=np.zeros(len(t))
    for off,g in ((0,1),(0.22,0.7)):
        tt2=t[t>=off]-off; f=40+40*np.exp(-tt2*35)
        out[t>=off]+=g*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt2*10)
    return out
Am=(57,[0,3,7]); F=(53,[0,4,7]); C=(48,[0,4,7]); G=(55,[0,4,7]); Em=(52,[0,3,7]); Dm=(50,[0,3,7]); E=(52,[0,4,7])
plan=[]  # (start, chord, section)
t=0.0
for ch in [Am,F,C,Em,Am,F,C,G]:                 # A: solo piano + strings suaves
    if t>=26.4: break
    plan.append((t,ch,'A')); t+=bar
# ajustar inicio de B a 26.53 (la caída)
plan=[p for p in plan if p[0]<26.4]
t=26.53
for ch in [Dm,Am]:
    plan.append((t,ch,'B')); t+=bar*1.05
t=33.53
for ch in [F,C,G,Am,F,C,G]:
    if t>=55.5: break
    plan.append((t,ch,'C')); t+=bar
plan.append((55.6,(53,[0,4,7,11]),'O'))   # Fmaj7 -> C al final
plan.append((55.6+3.3,(48,[0,4,7,14]),'O'))
for i,(t0,(root,iv),sec) in enumerate(plan):
    nxt=plan[i+1][0] if i+1<len(plan) else TOTAL
    d=nxt-t0
    tones=[root+x for x in iv]
    # cuerdas
    lvl={'A':0.09,'B':0.13,'C':0.16,'O':0.14}[sec]
    add(mus,t0,strings([mtof(n) for n in tones],d+1.0,att=1.5 if sec!='C' else 0.8,cut=1100 if sec!='C' else 1700),lvl)
    # bajo / cello
    add(mus,t0,strings([mtof(root-12)],d+0.8,att=0.6,cut=500),0.20 if sec!='A' else 0.12)
    # piano
    if sec=='A':
        pat=[(0,tones[0]+12,0.9),(1.5,tones[2]+12,0.55),(2,tones[1]+12,0.6),(3,tones[2]+12,0.5)]
        if i%2==1: pat=[(0,tones[0]+12,0.8),(2,tones[1]+24,0.6),(3,tones[2]+12,0.45)]
        for b,n,v in pat: add(mus,t0+b*beat,felt(mtof(n),4,v),0.16)
    elif sec=='B':
        for b,n in ((0,tones[0]+12),(2.5,tones[1]+12)): add(mus,t0+b*beat,felt(mtof(n),5,0.7),0.13)
        for b in (0,2): add(mus,t0+b*beat,heartbeat(),0.35)
    elif sec=='C':
        seq=[tones[0]+12,tones[2]+12,tones[1]+24,tones[2]+12]*2
        for s,n in enumerate(seq): add(mus,t0+s*beat/2,felt(mtof(n),2.5,0.55 if s%2 else 0.75),0.13)
        add(mus,t0,felt(mtof(tones[1]+24),4,0.6),0.10)
        for b in (0,2): add(mus,t0+b*beat,heartbeat(),0.28)
    else:
        for s,n in enumerate([tones[0]+12,tones[2]+12,tones[1]+24,tones[-1]+24]):
            add(mus,t0+s*0.45,felt(mtof(n),4,0.6),0.13)
fe=int(2.2*SR); mus[-fe:]*=np.linspace(1,0,fe)**1.5
mus[:int(1.0*SR)]*=np.linspace(0,1,int(1.0*SR))

# ---------------- SFX ----------------
sfx=np.zeros(N)
def env_ad(t,a,dcy): return np.minimum(t/a,1)*np.exp(-np.maximum(t-a,0)*dcy)
def pop(f=900,g=1.0):
    t=tt(0.12); fr=f*(1+1.2*np.exp(-t*60)); ph=2*np.pi*np.cumsum(fr)/SR
    return np.sin(ph)*np.exp(-t*38)*g
def tick(f=2600):
    t=tt(0.05); return np.sin(2*np.pi*f*t)*np.exp(-t*90)
def slam():
    t=tt(0.5); f=45+120*np.exp(-t*25); body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*8)
    n=bp(rng.standard_normal(len(t)),300,3500)*np.exp(-t*30)*0.6
    return body+n
def slap():
    t=tt(0.18); n=bp(rng.standard_normal(len(t)),900,5000)*np.exp(-t*45)
    thump=np.sin(2*np.pi*180*t)*np.exp(-t*40)*0.5
    return n*0.8+thump
def whoosh(d=0.7,peak=0.62,lo=250,hi=4000):
    t=tt(d); x=rng.standard_normal(len(t)); out=np.zeros_like(t)
    seg=int(0.02*SR)
    for i in range(0,len(t),seg):
        u=t[i]/d; c=lo*(hi/lo)**(np.sin(np.pi*min(u/peak,1)/2) if u<peak else 1-(u-peak)/(1-peak)*0.6)
        out[i:i+seg]=bp(x[max(0,i-2000):i+seg],c*0.6,min(c*1.6,20000))[-len(out[i:i+seg]):]
    e=np.where(t<peak*d,(t/(peak*d))**2,np.exp(-(t-peak*d)*9))
    return out*e*2.2
def zip_(d=0.35,f0=500,f1=2200):
    t=tt(d); f=f0*(f1/f0)**(t/d); s=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))
    return lp(s,5000)*np.minimum(t/0.01,1)*np.exp(-t*4)*0.35+pluck(220,d)*0.5
def slide_down(d=0.7,f0=1400,f1=300):
    t=tt(d); f=f0*(f1/f0)**(t/d); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.minimum(t/0.03,1)*np.minimum((d-t)/0.1,1)*0.6
def chime(notes,gap=0.07,d=2.5):
    out=np.zeros(int((d+gap*len(notes))*SR))
    for i,n in enumerate(notes):
        t=tt(d); f=mtof(n); x=(np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*3)+0.2*np.sin(2*np.pi*f*5.4*t)*np.exp(-t*6))*np.exp(-t*1.8)
        a=int(i*gap*SR); out[a:a+len(x)]+=x*np.minimum(t/0.002,1)
    return out*0.5
def marimba(n,d=0.5):
    t=tt(d); f=mtof(n); return (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*f*4*t)*np.exp(-t*30))*np.exp(-t*9)*np.minimum(t/0.002,1)
def bell():
    t=tt(1.2); x=sum(a*np.sin(2*np.pi*2800*r*t)*np.exp(-t*(4+r)) for r,a in [(1,1),(1.51,.6),(2.3,.3)]); 
    return np.concatenate([x[:int(0.14*SR)]*0.6,np.zeros(0)]) if False else x*0.35
def swell(d=1.6):
    t=tt(d); x=bp(rng.standard_normal(len(t)),400,3000)
    return x*np.sin(np.pi*t/d)**2*0.5
def creak(d=0.25,f=140):
    t=tt(d); pulses=(np.sin(2*np.pi*f*(1+0.3*t/d)*t)>0.97).astype(float)
    return bp(pulses,300,2500)*np.sin(np.pi*t/d)*1.5
# cuts
for c in [5.07,11.53,19.53,26.53,33.53,43.07]: add(sfx,c-0.43,whoosh(),0.55)
add(sfx,50.07-0.5,whoosh(1.0,0.5,150,6000),0.75); add(sfx,50.07,slam(),0.45)
# scene 1
add(sfx,0.15,pop(700),0.35); add(sfx,1.43,slam(),0.6); add(sfx,4.2,pop(1200),0.4)
# scene 2
for t0 in (5.25,5.6,5.92): add(sfx,t0,slam(),0.5)
for i in range(7): add(sfx,6.25+i*0.11,tick(3200),0.12)   # text typing
for i,t0 in enumerate(np.arange(7.5,9.45,0.13)): add(sfx,t0,pop(600+i*45),0.22)
add(sfx,9.47,slap(),0.5)
# scene 3
add(sfx,11.9,slam(),0.55); add(sfx,12.3,pop(500),0.35)
for t0,f in ((12.7,800),(13.5,950),(14.3,1100)): add(sfx,t0,pop(f),0.45)
add(sfx,13.55,bell(),0.35)
for t0 in (12.95,13.75,14.85): add(sfx,t0,slap(),0.3)
add(sfx,16.3,pop(900),0.3)
# scene 4
add(sfx,20.2,pop(700),0.4)
for t0 in (20.83,21.9,23.1,24.2): add(sfx,t0,slap(),0.6)
# scene 5
add(sfx,26.95,pop(700),0.3)
for t0,f in ((27.93,900),(28.6,1000),(29.3,1150)): add(sfx,t0,pop(f),0.45)
add(sfx,30.75,creak(0.3),0.4); add(sfx,30.9,slide_down(0.9),0.45); add(sfx,31.75,creak(0.35,110),0.35)
# scene 6
for i,t0 in enumerate((34.0,34.15,34.3,34.45)): add(sfx,t0,pop(700+i*120),0.4)
add(sfx,34.9,zip_(),0.4); add(sfx,35.07,slap(),0.5); add(sfx,35.55,zip_(0.3,400,1500),0.35)
add(sfx,36.6,zip_(),0.35); add(sfx,36.97,slap(),0.5)
add(sfx,38.5,slap(),0.5); add(sfx,38.83,zip_(0.4,600,2600),0.35)
add(sfx,40.53,slap(),0.5); add(sfx,40.93,zip_(0.4,600,2600),0.35)
for i in range(10): add(sfx,41.6+i*0.1,tick(3000),0.1)
# scene 7
add(sfx,43.63,pop(800),0.35); add(sfx,44.93,slam(),0.55); add(sfx,45.30,slam(),0.6)
add(sfx,45.45,chime([72,76,79],0.06,1.5),0.25)
# scene 8
add(sfx,51.1,slam(),0.5); add(sfx,52.33,pop(900),0.3); add(sfx,53.0,slap(),0.45); add(sfx,53.2,chime([79,84,88,91],0.08,2.0),0.25)
# outro (O = 55.6)
O=55.6
add(sfx,O+0.45,slide_down(0.9,2200,700),0.25)
add(sfx,O+1.35,slam(),0.35); add(sfx,O+1.35,pop(300),0.3)
add(sfx,O+1.35,whoosh(0.5,0.4,200,1500),0.2)
add(sfx,O+1.75,swell(1.7),0.35)
for t0 in (O+2.0,O+2.5,O+2.95): add(sfx,t0,creak(0.22,120+rng.integers(0,40)),0.25)
add(sfx,O+3.15,pop(600),0.45)
pent=[72,74,76,79,81,84,86,88,91,93,96]
for i in range(10): add(sfx,O+3.25+i*0.11,marimba(pent[i%len(pent)]),0.28)
for i in range(11): add(sfx,O+4.0+i*0.09,marimba(pent[min(i+2,10)]+0),0.22)
add(sfx,O+4.95,chime([72,79,84,88],0.09,2.6),0.35)
# ---------------- MIX ----------------
def rms(x): return np.sqrt(np.mean(x**2))
mus*=10**(-25/20)/rms(mus[:int(55*SR)])     # background song, quiet
sfx*=10**(-6/20)/np.abs(sfx).max()          # effects up front
np.save("mus.npy",mus.astype(np.float32)); np.save("sfx.npy",sfx.astype(np.float32))
out=mus+sfx
out/=max(1,np.abs(out).max()/0.95)
st=np.stack([out,out],1).astype(np.float32)
# slight stereo width for music
st[:,0]+= (0.0); st.tofile("newmix.raw")
print("music rms dB",20*np.log10(rms(mus)),"peak",np.abs(out).max())
