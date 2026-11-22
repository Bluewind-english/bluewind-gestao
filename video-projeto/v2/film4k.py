import json,base64,sys,subprocess,os
from playwright.sync_api import sync_playwright
exec(open('lines.py').read());dur=json.load(open('dur.json'))
start={'e1':3.6,'e2':11.6,'o2':18.6,'e8':21.0,'o3':28.6,'e9':31.0,'o4':35.0,'e10':36.8,'o1':43.0,'e3':45.6,'e4':58.2,'e5':69.4,'o5':82.6,'e11':85.0,'e12':104.6,'e13':113.4,'e14':120.0,'e15':134.2,'e16':145.6,'e7':159.8}
C={'intro':0,'asm':8,'daily':17.5,'prod':42,'feat':57,'net':68,'cam':81.5,'call':99.5,'safety':112.0,'ann':131.0,'emer':142.8,'close':157.8};END=168.3
voice=[{'id':k,'who':w,'t':start[k],'d':dur[k],'sub':sub} for k,w,_,sub in L]
order=['intro','asm','daily','prod','feat','net','cam','call','safety','ann','emer','close']
b64=lambda f:'data:image/webp;base64,'+base64.b64encode(open(f,'rb').read()).decode()
G='/home/claude/bluewind-gestao/video-projeto/img/'
img={k:b64(G+k+'.webp') for k in ['blades','logotext','horizons','connecting']};img['eolus']=b64('/home/claude/layers4k/clean.webp');img['head']=b64('/home/claude/layers4k/head.webp');img['body']=b64('/home/claude/layers4k/body.webp')
data={'C':C,'end':END,'voice':voice,'img':img,'specks':json.load(open('/home/claude/layers/specks.json'))}
json.dump({'voice':voice,'C':C,'end':END,'order':order},open('timeline.json','w'))
if __name__=='__main__':
    mode=sys.argv[1]
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=2)
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file:///home/claude/video2/page4k.html');pg.evaluate('d=>setup(d)',data)
        if mode=='stills':
            for t in map(float,sys.argv[2:]):
                pg.evaluate(f'render({t})');pg.screenshot(path=f'/tmp/k4_{t}.jpg',type='jpeg',quality=85)
        else:
            i=int(mode);a=C[order[i]];e=C[order[i+1]] if i+1<len(order) else END;n=round((e-a)*30);tmp=f'k4_scene{i}.tmp.mp4'
            ff=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-crf','18','-preset','veryfast','-threads','0','-pix_fmt','yuv420p','-r','30',tmp],stdin=subprocess.PIPE)
            for k in range(n):
                pg.evaluate(f'render({a+k/30})');ff.stdin.write(pg.screenshot(type='jpeg',quality=92))
            ff.stdin.close();rc=ff.wait()
            if rc==0:os.replace(tmp,f'k4_scene{i}.mp4')
            print('scene',i,n,'rc',rc)
        print('errors',errs);b.close()
