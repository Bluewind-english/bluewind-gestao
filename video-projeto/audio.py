import numpy as np, json, wave
SR=44100;tl=json.load(open('timeline.json'));END=tl['end'];sc=tl['sc'];V=tl['voice']
N=int(END*SR);t=np.arange(N)/SR;mix=np.zeros(N)
def env(n,a,r):
    e=np.ones(n);ai=min(int(a*SR),n//2);ri=min(int(r*SR),n//2)
    if ai:e[:ai]=np.linspace(0,1,ai)
    if ri:e[-ri:]=np.minimum(e[-ri:],np.linspace(1,0,ri))
    return e
drone=0.5*np.sin(2*np.pi*55*t)+0.3*np.sin(2*np.pi*82.41*t+.3)+0.15*np.sin(2*np.pi*110.3*t)
drone*=0.6+0.4*np.sin(2*np.pi*0.07*t)
chords=[[220,261.63,329.63],[174.61,220,261.63],[261.63,329.63,392],[196,246.94,293.66]]
pad=np.zeros(N);seg=8
for k in range(int(END/seg)+1):
    a=int(k*seg*SR);b=min(N,int((k+1)*seg*SR+SR*2));n=b-a
    if n<=0:break
    tt=np.arange(n)/SR;s=sum(np.sin(2*np.pi*f*tt)+.5*np.sin(2*np.pi*f*1.003*tt)+.25*np.sin(2*np.pi*f*2.001*tt) for f in chords[k%4])
    pad[a:b]+=s*env(n,2.5,2.5)
pad*=0.09
arp=np.zeros(N);step=60/100/2;notes=[440,523.25,659.25,880,659.25,523.25]
for i in range(int(END/step)):
    st=int(i*step*SR);n=int(.18*SR)
    if st+n>N:break
    f=notes[i%6]*(1 if (i//24)%2==0 else 0.89);tt=np.arange(n)/SR
    arp[st:st+n]+=np.sin(2*np.pi*f*tt)*np.exp(-tt*22)*0.06
music=drone*0.10+pad+arp
duck=np.ones(N)
for v in V:
    a=int((v['t']-.3)*SR);b=int((v['t']+v['d']+.3)*SR);duck[a:b]=0.45
duck=np.convolve(duck,np.ones(4410)/4410,mode='same')
music*=duck*np.clip(t/2,0,1)*np.clip((END-t)/3,0,1)
mix+=music
rng=np.random.default_rng(1)
def add(sig,at,g=1.0):
    a=int(at*SR);b=min(N,a+len(sig));mix[a:b]+=sig[:b-a]*g
def whoosh(d=1.4):
    n=int(d*SR);x=rng.standard_normal(n);tt=np.arange(n)/SR;c=np.cumsum(x);y=(c-np.roll(c,30))/30
    return y*np.sin(np.pi*tt/d)**2*0.35*(0.5+0.5*np.sin(2*np.pi*tt*3))
def beep(f=1400,d=.12):
    tt=np.arange(int(d*SR))/SR;return (np.sin(2*np.pi*f*tt)+.4*np.sin(2*np.pi*f*1.5*tt))*np.exp(-tt*25)*0.18
def boom():
    tt=np.arange(int(2.5*SR))/SR;f=60*np.exp(-tt*1.2)+30;return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*1.6)*0.6
add(boom(),0.2);add(boom(),sc[6]+1.1,0.8)
for s in sc[1:]:add(whoosh(),s-.7)
for i in range(18):add(beep(1800+rng.integers(0,1600),.08),sc[1]+0.3+i*0.2,0.5)
add(beep(900,.25),sc[1]+4.0,1.2)
def wordT(v,word):
    ws=v['sub'].split(' ');i=next(j for j,w in enumerate(ws) if w.lower().startswith(word.lower()));return v['t']+v['d']*.92*(i/len(ws))
vv={v['id']:v for v in V}
for w in ['Schedule','Production','Alerts','Messages','Daily','History','team']:add(beep(1500,.12),wordT(vv['e4'],w)-.15)
for w in ['Recruitment','Resin','Gel','vacuum','production','screens']:add(beep(1150,.14),wordT(vv['e5'],w)-.1)
add(beep(2000,.3),wordT(vv['e3'],'recommend'),1.2)
for i in range(6):add(beep(880 if i%2==0 else 660,.28),sc[5]+.6+i*.32,1.6)
add(beep(1760,.4),wordT(vv['e6'],'supervisor')+.3,1.2)
add(beep(1200,.1),vv['o1']['t']-.4);add(beep(1600,.1),vv['o1']['t']-.28)
def readwav(p):
    w=wave.open(p);return np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768
for v in V:add(readwav(f"aud/{v['id']}.wav"),v['t'],1.0 if v['who']=='e' else 0.9)
mix=np.tanh(mix*1.1)*0.92
st=np.stack([mix,np.roll(mix,int(.012*SR))*0.96],1)
w=wave.open('track.wav','wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((st*32767).astype(np.int16).tobytes());w.close()
print('peak',np.abs(mix).max())
