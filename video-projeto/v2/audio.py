import numpy as np, json, wave
SR=44100;tl=json.load(open('timeline.json'));END=tl['end'];C=tl['C'];V=tl['voice']
N=int(END*SR);t=np.arange(N)/SR;mix=np.zeros(N)
def env(n,a,r):
    e=np.ones(n);ai=min(int(a*SR),n//2);ri=min(int(r*SR),n//2)
    if ai:e[:ai]=np.linspace(0,1,ai)
    if ri:e[-ri:]=np.minimum(e[-ri:],np.linspace(1,0,ri))
    return e
drone=(0.5*np.sin(2*np.pi*55*t)+0.3*np.sin(2*np.pi*82.41*t+.3)+0.15*np.sin(2*np.pi*110.3*t))*(0.6+0.4*np.sin(2*np.pi*0.07*t))
chords=[[220,261.63,329.63],[174.61,220,261.63],[261.63,329.63,392],[196,246.94,293.66]]
pad=np.zeros(N);seg=8
for k in range(int(END/seg)+1):
    a=int(k*seg*SR);b=min(N,int((k+1)*seg*SR+SR*2));n=b-a
    if n<=0:break
    tt=np.arange(n)/SR;pad[a:b]+=sum(np.sin(2*np.pi*f*tt)+.5*np.sin(2*np.pi*f*1.003*tt)+.25*np.sin(2*np.pi*f*2.001*tt) for f in chords[k%4])*env(n,2.5,2.5)
pad*=0.08
arp=np.zeros(N);step=60/100/2;notes=[440,523.25,659.25,880,659.25,523.25]
for i in range(int(END/step)):
    st=int(i*step*SR);n=int(.18*SR)
    if st+n>N:break
    tt=np.arange(n)/SR;arp[st:st+n]+=np.sin(2*np.pi*notes[i%6]*(1 if (i//24)%2==0 else 0.89)*tt)*np.exp(-tt*22)*0.05
music=drone*0.09+pad+arp
duck=np.ones(N)
for v in V:duck[int((v['t']-.3)*SR):int((v['t']+v['d']+.3)*SR)]=0.35
music*=np.convolve(duck,np.ones(4410)/4410,mode='same')*np.clip(t/2,0,1)*np.clip((END-t)/3,0,1)
mix+=music
rng=np.random.default_rng(1)
def add(sig,at,g=1.0):
    a=int(at*SR);b=min(N,a+len(sig));mix[a:b]+=sig[:b-a]*g
def whoosh(d=1.4):
    n=int(d*SR);x=rng.standard_normal(n);tt=np.arange(n)/SR;c=np.cumsum(x);y=(c-np.roll(c,30))/30
    return y*np.sin(np.pi*tt/d)**2*0.3*(0.5+0.5*np.sin(2*np.pi*tt*3))
def beep(f=1400,d=.12):
    tt=np.arange(int(d*SR))/SR;return (np.sin(2*np.pi*f*tt)+.4*np.sin(2*np.pi*f*1.5*tt))*np.exp(-tt*25)*0.15
def boom():
    tt=np.arange(int(2.5*SR))/SR;f=60*np.exp(-tt*1.2)+30;return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*1.6)*0.5
def ring(d=0.9):
    tt=np.arange(int(d*SR))/SR;return (np.sin(2*np.pi*440*tt)+np.sin(2*np.pi*480*tt))*0.09*env(len(tt),.02,.05)
def wordT(v,word):
    ws=v['sub'].split(' ');i=next(j for j,w in enumerate(ws) if w.lower().startswith(word.lower()));return v['t']+v['d']*.92*(i/len(ws))
vv={v['id']:v for v in V}
add(boom(),0.2);add(boom(),C['close']+1.1,0.8)
for k in ['asm','daily','prod','feat','net','cam','call','safety','close']:add(whoosh(),C[k]-.7)
for i in range(18):add(beep(1800+rng.integers(0,1600),.08),C['asm']+0.3+i*0.2,0.5)
add(beep(900,.25),C['asm']+4.0,1.2)
for k in ['e8','e9','e10']:add(beep(1300,.12),vv[k]['t']-.1)
for k in ['o1','o2','o3','o4','o5']:add(beep(1200,.08),vv[k]['t']-.4);add(beep(1600,.08),vv[k]['t']-.28)
add(beep(2000,.3),wordT(vv['e3'],'recommend'),1.2)
for w in ['Schedule','Production','Alerts','Messages','Daily','History','team']:add(beep(1500,.12),wordT(vv['e4'],w)-.15)
for w in ['Recruitment','Resin','Gel','vacuum','production','screens']:add(beep(1150,.14),wordT(vv['e5'],w)-.1)
for w in ['infusion','assembly','parking']:add(beep(700,.25),wordT(vv['e11'],w),1.3)
for i in range(6):add(beep(880 if i%2==0 else 660,.28),C['call']+.6+i*.32,1.6)
for v,k in [('e12',2),('e14',2)]:
    s=vv[v]['t']-2.7
    for r in range(k):add(ring(),s+r*1.2)
for i in range(4):add(beep(1000 if i%2==0 else 760,.3),C['safety']+.5+i*.35,1.6)
def readwav(p):
    w=wave.open(p);return np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768
for v in V:add(readwav(f"aud/{v['id']}.wav"),v['t'],1.15 if v['who']=='e' else 1.05)
mix=np.tanh(mix*1.05)*0.95
st=np.stack([mix,np.roll(mix,int(.01*SR))*0.97],1)
w=wave.open('track.wav','wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((st*32767).astype(np.int16).tobytes());w.close()
print('peak',round(np.abs(mix).max(),3))
