"""Inspect the encoded output, including every frame during decoding."""
from pathlib import Path
import json, subprocess
from PIL import Image, ImageStat
root=Path(__file__).resolve().parent
out=root/'deliverables'
video=out/'jury_animation.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)]))
decode=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
times=[1,6,13,21,27,11.8,12.2,22,29.8,30.2,34,39,47.8,48.2,58,67.8,68.2,78,87.8,88.2,98,107.8,108.2,117,126.8,127.2,135,141.8,142.2,150,156.8,157.2,163,168.8,169.2,173]
sheet=Image.new('RGB',(1600,((len(times)+4)//5)*180))
samples=[]
for i,t in enumerate(times):
    path=out/f'encoded_{i:02}.jpg'
    subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-vf','scale=320:180',str(path)],check=True)
    im=Image.open(path).convert('RGB')
    samples.append({'seconds':t,'luma_mean':ImageStat.Stat(im.convert('L')).mean[0]})
    sheet.paste(im,((i%5)*320,(i//5)*180))
sheet.save(out/'encoded_contact_sheet.jpg')
stream=probe['streams'][0]
checks={'duration_177s':abs(float(probe['format']['duration'])-177)<.1,'resolution_1080p':(stream['width'],stream['height'])==(1920,1080),'h264':stream['codec_name']=='h264','24fps':stream['r_frame_rate']=='24/1','yuv420p':stream['pix_fmt']=='yuv420p','full_decode_clean':decode.returncode==0 and not decode.stderr.strip(),'4248_frames':int(stream['nb_frames'])==4248}
chapters=json.loads((out/'video_chapters.json').read_text())
checks['seven_pages']=len(chapters)==7 and [c['page'] for c in chapters]==list(range(1,8))
checks['continuous_page_timeline']=chapters[0]['start_s']==0 and chapters[-1]['end_s']==177 and all(a['end_s']==b['start_s'] for a,b in zip(chapters,chapters[1:]))
(out/'verification.json').write_text(json.dumps({'checks':checks,'probe':probe,'pages':chapters,'decode_stderr':decode.stderr,'encoded_samples':samples},indent=2))
print(json.dumps(checks,indent=2))
if not all(checks.values()):raise SystemExit(1)
