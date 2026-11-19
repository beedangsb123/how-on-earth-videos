import numpy as np, soundfile as sf, json
sr=44100; m=json.load(open("meta.json")); T=sum(x["dur"]+0.45 for x in m)+0.5
t=np.arange(int(T*sr))/sr; out=np.zeros_like(t)
def note(f): return 440*2**((f-69)/12)
chords=[[45,52,57,60,64],[41,48,53,57,60],[48,55,60,64,67],[43,50,55,59,62]]  # Am F C G
L=8.0
for i in range(int(T/L)+1):
    ch=chords[i%4]; s=int(i*L*sr); e=min(len(t),int((i*L+L+2)*sr))
    tt=t[s:e]-i*L; env=np.clip(tt/2.0,0,1)*np.clip((L+2-tt)/2.5,0,1)
    for n in ch:
        f=note(n); out[s:e]+=env*(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt+0.5)+0.15*np.sin(2*np.pi*f*1.003*tt))/len(ch)
# soft pulse
beat=0.5
for k in range(int(T/beat)):
    s=int(k*beat*sr); e=min(len(t),s+int(0.25*sr)); tt=t[s:e]-k*beat
    out[s:e]+=0.25*np.exp(-tt*18)*np.sin(2*np.pi*note(81+[0,3,7,12][k%4])*tt)
out=out/np.max(np.abs(out))*0.9
fade=np.clip((T-t)/2.0,0,1); out*=fade
sf.write("music.wav",np.stack([out,out],1),sr)
