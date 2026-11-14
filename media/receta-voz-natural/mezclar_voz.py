import numpy as np, subprocess, sys
SR=48000; v=sys.argv[1]
mus=np.load("mus.npy"); sfx=np.load("sfx.npy"); N=len(mus)
starts=[0.45,5.75,12.25,20.0,27.0,34.3,43.6,50.8]
voice=np.zeros(N,np.float32)
for i,s in enumerate(starts):
    x=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f"vo2/{v}_{i}.wav","-af","highpass=f=80,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120","-f","f32le","-ar","48000","-ac","1","-"],capture_output=True).stdout,np.float32)
    a=int(s*SR); b=min(N,a+len(x)); voice[a:b]+=x[:b-a]
rms=lambda x: np.sqrt(np.mean(x[np.abs(x)>1e-4]**2))
voice*=10**(-16/20)/rms(voice)
act=(np.abs(voice)>1e-3).astype(np.float32)
k=int(0.35*SR); env=np.convolve(act,np.ones(k)/k,mode="same"); env=np.clip(env*4,0,1)
k2=int(0.15*SR); env=np.convolve(env,np.ones(k2)/k2,mode="same")
duck=1-0.6*env   # ~ -8 dB bajo la voz
out=mus*duck+sfx*(1-0.35*env)+voice
out/=max(1,np.abs(out).max()/0.95)
np.stack([out,out],1).astype(np.float32).tofile(f"mix_vo_{v}.raw")
