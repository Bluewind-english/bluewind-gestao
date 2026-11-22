import json,base64,sys,subprocess,os
from playwright.sync_api import sync_playwright
dur=json.load(open('dur.json'));exec(open('lines.py').read())
subs={'e1':"Welcome to BlueWind HORIZONS.",'e2':"I am Eolus, the artificial intelligence of BlueWind Technology. I connect processes and people.",
'o1':"Eolus, how is tomorrow's production?",'e3':"Good morning. Tomorrow, 6 nacelles are in the line. Nacelle N-105 is 2 days behind schedule. I recommend moving one team from Finishing to Lamination.",
'e4':"Schedule. Production. Alerts. Messages. Daily dashboard. History. And team. Everything in one place, live from the cloud.",
'e5':"I am connected to every system in the factory: Recruitment and safety training. Resin dosing. Gel coat and vacuum monitoring. The production line. And the factory screens. Everything flows to me.",
'e6':"Attention. Vacuum loss detected on infusion mold 2. The supervisor has been notified.",'e7':"BlueWind. Connecting processes and people. The next phase starts now."}
subs['e5']=subs['e5'].replace(' Everything flows to me.','')
start={'e1':4.2,'e2':12.8,'o1':22.8,'e3':26.6,'e4':43.2,'e5':58.4,'e6':76.0,'e7':87.5}
sc=[0,9,21,42,57,75,86];END=97
who={k:w for k,w,_ in L}
voice=[{'id':k,'who':who[k],'t':start[k],'d':dur[k],'sub':subs[k]} for k in start]
b64=lambda f,m:f'data:image/{m};base64,'+base64.b64encode(open(f,'rb').read()).decode()
img={'eolus':b64('/tmp/eolus_a.webp','webp'),'blades':b64('/home/claude/cover/blades.webp','webp'),'logotext':b64('/home/claude/cover/logotext.webp','webp'),'horizons':b64('/home/claude/cover/horizons.webp','webp'),'connecting':b64('/home/claude/cover/connecting.webp','webp')}
data={'sc':sc,'end':END,'voice':voice,'img':img}
json.dump({'voice':voice,'sc':sc,'end':END},open('timeline.json','w'))
def page(p):
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page(viewport={'width':1920,'height':1080})
    pg.goto('file:///home/claude/video/page.html');pg.evaluate('d=>setup(d)',data);return b,pg
if __name__=='__main__':
    mode=sys.argv[1]
    with sync_playwright() as p:
        b,pg=page(p)
        if mode=='stills':
            for t in map(float,sys.argv[2:]):
                pg.evaluate(f'render({t})');pg.screenshot(path=f'/tmp/st_{t}.jpg',type='jpeg',quality=85)
        else:
            i=int(mode);a=sc[i];e=sc[i+1] if i+1<len(sc) else END;n=round((e-a)*30)
            tmp=f'scene{i}.tmp.mp4'
            ff=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-crf','18','-preset','veryfast','-pix_fmt','yuv420p','-r','30',tmp],stdin=subprocess.PIPE)
            for k in range(n):
                pg.evaluate(f'render({a+k/30})');ff.stdin.write(pg.screenshot(type='jpeg',quality=92))
            ff.stdin.close();rc=ff.wait()
            if rc==0:os.replace(tmp,f'scene{i}.mp4')
            print('scene',i,n,'frames rc',rc)
        b.close()
