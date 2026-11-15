"""Deterministic 177-second QK norm film. Pillow raster animation → FFmpeg H.264."""
from pathlib import Path
import argparse, csv, json, math, random, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
W,H,FPS=1920,1080,24
BG=(18,17,15); WHITE=(242,234,222); MUTED=(177,164,147)
ACCENT=(215,184,147); AMBER=(194,132,83); PANEL=(31,29,26)
FONT='/usr/share/fonts/noto/NotoSans-Regular.ttf'
BOLD='/usr/share/fonts/noto/NotoSans-Bold.ttf'
fonts={}
def font(size,bold=False):
    key=(size,bold)
    if key not in fonts: fonts[key]=ImageFont.truetype(BOLD if bold else FONT,size)
    return fonts[key]
def text(d,xy,s,size=28,color=WHITE,bold=False):
    d.text(xy,s,font=font(size,bold),fill=color)
def ease(x): return (max(0,min(1,x)))**2*(3-2*max(0,min(1,x)))
def line(d,points,color=ACCENT,width=3): d.line(points,fill=color,width=width)
def card(d,xy,color=PANEL,outline=(78,68,57),radius=22):d.rounded_rectangle(xy,radius,fill=color,outline=outline,width=2)
def wrapped(d,s,x,y,width,size=29,color=MUTED):
    words=s.split(); row=''
    for word in words:
        if d.textlength(row+word,font=font(size))>width:
            text(d,(x,y),row,size,color,True);y+=size*1.5;row=''
        row+=word+' '
    text(d,(x,y),row,size,color,True)
def arrow(d,x,y,length=110,color=ACCENT):
    line(d,[(x,y),(x+length,y)],color);line(d,[(x+length-12,y-8),(x+length,y),(x+length-12,y+8)],color)
rng=random.Random(31)
stars=[(rng.randrange(W),rng.randrange(H),rng.choice([1,1,2])) for _ in range(150)]
base=Image.new('RGB',(W,H),BG)
bd=ImageDraw.Draw(base)
for y in range(H):
    c=int(8*(1-y/H))
    bd.line([(0,y),(W,y)],fill=(18+c,17+c,15+c))
for x,y,r in stars: bd.ellipse((x,y,x+r,y+r),fill=(67,58,49))
photo=Image.open(ROOT/'assets/saffire.jpeg').convert('RGB')
photo=photo.point([int(255*(i/255)**.38) for i in range(256)]*3)
dash=Image.open(ROOT/'assets/dashboard.png').convert('RGB')
runs=list(csv.DictReader(open(PROJECT/'external/model_c/data/processed/dashboard_measured_only.csv')))
runs=sorted(runs,key=lambda r:['Kapton','Teflon','Lampwick','Pyrell','Silicone'].index(r['material']))
def warm_scene(image):
    # Art-direction grade applies only to illustrative 3D renders, not NASA imagery.
    toned=ImageOps.colorize(ImageOps.grayscale(image),'#13110f','#e9decd')
    return Image.blend(toned,image,.15)

camera_paths=[ROOT/'assets/camera_frames'/f'camera_{i:04}.png' for i in range(1,38)]
camera_frames=None
def camera_image(progress):
    global camera_frames
    if camera_frames is None:
        camera_frames=[warm_scene(Image.open(p).convert('RGB')).resize((1120,630)) for p in camera_paths]
    position=max(0,min(1,progress))*36
    index=int(position)
    following=min(index+1,36)
    return Image.blend(camera_frames[index],camera_frames[following],position-index)
event_frames=None
def event_image(progress, size=(1920,1080)):
    global event_frames
    if event_frames is None:
        event_frames=[warm_scene(Image.open(ROOT/'assets/event_frames'/f'event_{i:04}.png').convert('RGB')) for i in range(1,38)]
    position=max(0,min(1,progress))*36
    idx=int(position)
    return Image.blend(event_frames[idx],event_frames[min(idx+1,36)],position-idx).resize(size)

def event_scene(t):
    im=event_image(t/30).convert('RGBA')
    shade=Image.new('RGBA',(W,H))
    pixels=ImageDraw.Draw(shade)
    for x in range(W):
        alpha=int(215*(1-ease((x-420)/700)))
        pixels.line([(x,0),(x,H)],fill=(15,13,11,alpha))
    pixels.rectangle((0,930,W,H),fill=(15,13,11,215))
    im=Image.alpha_composite(im,shade).convert('RGB');d=ImageDraw.Draw(im)
    phases=[
        (0,6,'BAŞLANGIÇ / ISITMA','Her olayın\nbir başlangıcı var.','Numune ısınır.\nYakın plan, haznenin içini gösterir.'),
        (6,12,'YANMANIN GELİŞİMİ','Alevi gör.\nKoşulu sorgula.','Alev zarfı büyür ve biçim değiştirir.\nAkış ve malzeme araştırmanın parçasıdır.'),
        (12,20,'HAVALANDIRMA / TAŞINIM','Duman nereye\nulaşıyor?','Temsili parçacıklar akışla taşınır.\nSensörün gördüğü, taşınan dumanla ilişkilidir.'),
        (20,25,'SÖNÜM AŞAMASI','Isı kaynağı\nkapatılır.','Bu anlatımda ısıtma durdurulur.\nAlev zarfı küçülmeye başlar.'),
        (25,30,'ARAŞTIRMA SORUSU','Sönümü anla.\nKanıtı koru.','BASS, yanma ve söndürmeyi inceler.\nModellerimiz mevcut deney kayıtlarını analiz eder.')
    ]
    start,end,kicker,title,body=next(p for p in phases if p[0]<=t<p[1])
    text(d,(85,55),'QK norm',29,WHITE,True)
    text(d,(85,195),kicker,24,ACCENT,True)
    for j,row in enumerate(title.split('\n')):text(d,(85,260+j*85),row,64,WHITE,True)
    for j,row in enumerate(body.split('\n')):wrapped(d,row,85,500+j*75,690,27)
    context={
        0:('NEDEN ÖNEMLİ?','Mürettebat güvenliği, koşula uygun değerlendirme gerektirir.'),
        6:('ARAŞTIRMA DEĞİŞKENLERİ','Geometri, malzeme, hava akışı ve oksijen.'),
        12:('NASA 2025 TEKNOLOJİ İHTİYACI','Dumanı ortam tozundan seçici biçimde ayırmak.'),
        20:('BASS ARAŞTIRMA ODAĞI','Katı yakıtların yanma ve söndürülme davranışı.'),
        25:('QK norm KATKISI','Deney kayıtlarını karşılaştırıp yeni soruları görünür kılmak.')}
    label,detail=context[start]
    text(d,(85,675),label,21,ACCENT,True)
    wrapped(d,detail,85,715,700,24,WHITE)
    text(d,(85,957),'TEMSİLİ 3B OLAY • sahne süresi ve parçacık yolları ölçüm içermez',22,MUTED)
    text(d,(85,997),'Alev biçimi, sönüm ve sensör yanıtı bu sahnede bilimsel olarak hesaplanmaz.',21,MUTED)
    line(d,[(85,1045),(1835,1045)],(76,66,56),3)
    line(d,[(85,1045),(85+1750*t/177,1045)],ACCENT,3)
    if 10<t<12 or 28<t<30:
        card(d,(980,800,1835,900),(29,25,21))
        text(d,(1010,825),'ÖLÇ. KARŞILAŞTIR. ANLAMINI GÖR.',30,ACCENT,True)
    return im

bass=Image.open(ROOT/'assets/bass_nasa.jpg').convert('RGB')
cli=json.loads((ROOT/'assets/cli_sweep.json').read_text())
benchmarks=json.loads((ROOT/'assets/benchmarks.json').read_text())
scenes=[
(0,12,'QK norm','Uzayda alev.\nYeni sorular.','Amacımız: NASA verisini anlaşılır kılmak.\nYangın araştırmasına açık bir başlangıç.','Temsili 3B hazne • metre birimi • fiziksel simülasyon içermez'),
(12,30,'NEDEN BU PROBLEM?','Duman nereye\ngidiyor?','Mikro yerçekiminde kaldırma akışı kaybolur.\nHavalandırma, dumanın sensöre taşınmasını etkiler.','NASA yangın algılama araştırma soruları • 2021 • s. 2'),
(30,48,'GERÇEK DENEYLER','Önce gözlem.\nSonra model.','BASS: yanma ve söndürme araştırması.\nHer deney, farklı bir bilimsel soruyu ele alır.','NASA • BASS alev fotoğrafı • ISS040E023287'),
(48,68,'MODEL A / BASS-II','Koşulları seç.\nYayılmayı incele.','Neden? Geometri ve akış birlikte etkilidir.\nPMMA levhada alev yayılma hızı tahmini.','18 fiziksel numune • 39 hava akışı segmenti • keşif amaçlı'),
(68,88,'MODEL B / SAFFIRE-I','Kareyi oku.\nKonumu ölç.','Neden? Görüntüyü sayısal ölçüme dönüştürmek.\nParlak alev sırtının yatay konumunu bulur.','NASA kamera C1 • tek numune • tek görüntü görevi'),
(88,108,'MODEL C / SAME + SAME-R','Malzemeyi tanı.\nYanıtı karşılaştır.','Neden? Farklı dumanlar farklı sinyal üretir.\nHedef: kayıtlı saçılmanın 2,0 V eşiğine erişmesi.','Birincil ısıtma koşuları • betimsel sayımlar • alarm olasılığı içermez'),
(108,127,'BİRLİKTE DAHA ANLAŞILIR','Üç uzman model.\nAçık bağlam.','Katalog, bulguyu kaynağına bağlar.\nWT4, ayrı bir metin üretim aracı sunar.','Yapılandırılmış katalog • bilimsel doğrulama ertelendi'),
(127,142,'KAYITLI KARŞILAŞTIRMALAR','Sonucu göster.\nSınırını açıkla.','Neden? Başarıyı ölçülebilir kılmak.\nHer model, kendi görevinin ölçütüyle karşılaştırılır.','Mevcut değerlendirme raporları • yeni bağımsız doğrulama yapılmadı'),
(142,157,'ÇALIŞAN ARAYÜZ','Seç. Çalıştır.\nAnla.','Hazır örneklerle hızlı bir başlangıç.\nSonuç, birimi ve kısa açıklamasıyla görünür.','Gerçek arayüz kaydı • çalışan yerel Python API'),
(157,169,'KOMUT SATIRIYLA KOLAY DENEME','Bir girdiyi değiştir.\nSonuçları karşılaştır.','Neden? Tekrarlı denemeleri kolaylaştırmak.\nHazır örnek seç; parametre tara; JSON kaydet.','Gerçek CLI çalıştırması • model girdisi denemesi • fiziksel deney yapılmaz'),
(169,177,'QK norm','Kanıttan soruya.\nSorudan araştırmaya.','NASA ihtiyacı belgeledi ve önceliklendirdi.\nQK norm, kanıttan araştırma kararına katkı sunar.','Bağımsız araştırma prototipi • NASA resmî onayı bulunmaz')
]
nist_materials=Image.open(ROOT/'assets/nist_2018_materials.webp').convert('RGB')
nasa_excerpt=Image.open(ROOT/'assets/nasa_251_detection.png').convert('RGB')
nasa_rank=Image.open(ROOT/'assets/nasa_251_rank.png').convert('RGB')

def chronology_scene(t):
    stage=min(2,int(t/15))
    if t<30:
        background=event_image(t/30)
    else:
        background=base.copy()
        background.paste(camera_image((t-30)/15),(800,250))
    im=background.convert('RGBA')
    shade=Image.new('RGBA',(W,H));sd=ImageDraw.Draw(shade)
    for x in range(W):
        alpha=int(220*(1-ease((x-430)/750)))
        sd.line([(x,0),(x,H)],fill=(15,13,11,alpha))
    sd.rectangle((0,0,W,230),fill=(15,13,11,225))
    sd.rectangle((0,925,W,H),fill=(15,13,11,230))
    im=Image.alpha_composite(im,shade).convert('RGB');d=ImageDraw.Draw(im)
    text(d,(85,40),'QK norm',30,WHITE,True)
    text(d,(1340,47),'NASA SPACE APPS / 2026',21,MUTED)
    stages=[('2018','DISCOVERED'),('2025','PRIORITIZED'),('2026','QK norm')]
    for j,(year,word) in enumerate(stages):
        x=85+j*585
        card(d,(x,100,x+550,206),(46,37,29) if j==stage else (27,24,20),
             ACCENT if j==stage else (74,62,49),12)
        text(d,(x+22,113),year,39,ACCENT if j==stage else MUTED,True)
        text(d,(x+175,127),word,26,WHITE if j==stage else MUTED,True)
    if stage==0:
        title='Algılama sınırı\nbelgelendi.'
        kicker='2018 / NASA + NIST'
        body=['Kapton ve Teflon dumanları,','belirli koşullarda zor algılandı.']
        detail='Kontrollü SAME deneyleri: ISS fotoelektrik dedektörü.'
        im.paste(nist_materials.resize((570,int(570*nist_materials.height/nist_materials.width))),(1250,340));d=ImageDraw.Draw(im)
        text(d,(1250,315),'GERÇEK SAME NUMUNELERİ / NIST',21,ACCENT,True)
        foot='NIST, 01.05.2018 • Meyer ve ark., Fire Safety Journal 98, s. 74–81'
        foot2='DOI 10.1016/j.firesaf.2018.04.004 • belirli deney koşullarına ait sonuç'
    elif stage==1:
        title='Daha iyi algılama\nresmî bir ihtiyaç.'
        kicker='2025 / NASA SBIR'
        body=['Seçici duman algılama, parçacık kapsamı','ve toz kaynaklı yanlış alarmlar.']
        detail='Fire Safety for Habitation / ID 1520 / 10. sıra'
        card(d,(1125,335,1835,620),(235,227,211),(128,107,84),12)
        im.paste(nasa_excerpt.resize((670,117)),(1145,365))
        im.paste(nasa_rank.resize((670,56)),(1145,525));d=ImageDraw.Draw(im)
        text(d,(1125,293),'GERÇEK NASA BELGESİ / BASILI SAYFA 251',21,ACCENT,True)
        foot='NASA FY2025 SBIR • S15.03, Fire Detection Sensing for Space Research'
        foot2='PDF s. 258–259 / basılı s. 250–251 • 10. sıra: belgedeki Civil Space Shortfall ID 1520'
    else:
        title='Kanıttan araştırma\nkararına.'
        kicker='2026 / QK norm KATKISI'
        body=['Çözdüğümüz parça: deneyleri kaynaklı,','karşılaştırılabilir ve anlaşılır incelemek.']
        detail='Üç bilimsel ML modülü + katalog + çalışan dashboard.'
        shot=dash.resize((690,int(690*dash.height/dash.width)))
        im.paste(shot,(1140,300));d=ImageDraw.Draw(im)
        foot='NASA yeni sensör teknolojileri talep ediyor. QK norm bilimsel karar desteği sunuyor.'
        foot2='Mevcut çalışan prototip • fiziksel yangın önleme başarısı doğrulanmadı'
    text(d,(85,278),kicker,24,ACCENT,True)
    for j,row in enumerate(title.split('\n')):text(d,(85,332+j*81),row,60,WHITE,True)
    for j,row in enumerate(body):text(d,(85,535+j*48),row,29,WHITE,True)
    wrapped(d,detail,85,671,775,25,ACCENT)
    if stage==0:
        wrapped(d,'Ana problem: dumanın her koşulda aynı biçimde algılanmaması.',85,756,760,25)
    elif stage==1:
        wrapped(d,'Bu ihtiyaç NASA’nın bilimsel bulgularına ve teknoloji çağrısına dayanıyor.',85,756,760,25)
    else:
        wrapped(d,'Bulguyu, ölçümü ve eksik kanıtı aynı bağlamda görünür kılıyoruz.',85,756,760,25)
    if t<30:
        event_label=('Isıtma' if t<6 else 'Alev gelişimi' if t<12 else
                     'Duman taşınımı' if t<20 else 'Isı kaynağı kapanır' if t<25 else 'Sönüm')
        text(d,(1145,855),'TEMSİLİ 3B OLAY / '+event_label,23,ACCENT,True)
    text(d,(85,947),foot,21,MUTED)
    text(d,(85,985),foot2,20,MUTED)
    line(d,[(85,1045),(1835,1045)],(76,66,56),3)
    line(d,[(85,1045),(85+1750*t/177,1045)],ACCENT,3)
    return im

chapters=[
    (0,45,'Problem ve 2018–2025–2026 kronolojisi'),
    (45,68,'Deney bağlamı ve Model A'),
    (68,88,'Model B / görüntüden ölçüm'),
    (88,108,'Model C / gerçek SAME kayıtları'),
    (108,142,'Kaynaklı analiz ve benchmark'),
    (142,169,'Dashboard ve CLI'),
    (169,177,'Araştırma katkısı ve kapanış')
]

def draw_scene(index,t):
    if index==2:
        index=3
    start,end,kicker,title,body,source=scenes[index]
    if index==3:
        start=45
    if index in (6,7):
        kicker='KAYNAKLI ANALİZ VE DEĞERLENDİRME'
        title='Ölçümü açıkla.\nSınırı göster.'
    if index in (8,9):
        kicker='ÇALIŞAN SİSTEM / DASHBOARD + CLI'
        title='Seç. Çalıştır.\nKarşılaştır.'
    local=t-start;p=ease(local/1.3)
    if index in (7,9):
        p=1
    if t<45:
        return chronology_scene(t)
    im=base.copy();d=ImageDraw.Draw(im)
    text(d,(96,55),'QK norm',26,WHITE,True)
    text(d,(1550,58),'ARAŞTIRMA / 2026',19,MUTED)
    line(d,[(96,106),(1824,106)],(74,66,56),1)
    offset=int((1-p)*28)
    text(d,(96,195+offset),kicker,23,ACCENT,True)
    yy=255+offset
    for row in title.split('\n'):text(d,(96,yy),row,60,WHITE,True);yy+=80
    if local>1.6 and index not in (0,10):
        yy=max(465,yy+38)
        for row in body.split('\n'):
            wrapped(d,row,96,yy,710,29);yy+=83
    text(d,(96,972),source,19,MUTED)
    line(d,[(96,1025),(1824,1025)],(65,57,49),3)
    line(d,[(96,1025),(96+1728*t/scenes[-1][1],1025)],ACCENT,3)
    # Dedicated dimensional visual stage, with continuously moving details.
    cx,cy=1400,530
    if index in (0,10):
        progress=local/(end-start)
        art=camera_image(progress if index==0 else 1-progress)
        im.paste(art,(800,240));d=ImageDraw.Draw(im)
        # Retain readable typography over the dark left margin.
        for j,row in enumerate(body.split('\n')):
            if local>(1.6+j*4 if index==0 else .8):
                wrapped(d,row,96,490+j*83,660,27)
        text(d,(1000,905),'SCÈNE 3B / TEMSİLİ MİKRO YERÇEKİMİ ALEVİ'.replace('SCÈNE','SAHNE'),22,ACCENT)
    elif index==1:
        card(d,(1000,285,1800,795))
        for y in [340,730]:line(d,[(1050,y),(1740,y)],(72,99,104),2)
        card(d,(1660,430,1760,590),(29,60,62),ACCENT)
        text(d,(1635,615),'SENSÖR',22,ACCENT)
        card(d,(1060,595,1170,640),(107,68,38),AMBER)
        text(d,(1040,670),'KAYNAK',22,AMBER)
        for j in range(40):
            phase=(local*.07+j/40)%1
            x=1120+580*phase;y=575-70*math.sin(phase*math.pi)+18*math.sin(j*3)
            rr=3+j%4;d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=AMBER)
        arrow(d,1260,365,230)
        text(d,(1250,315),'HAVALANDIRMA',23,ACCENT)
    elif index==2:
        art=bass.resize((800,int(800*bass.height/bass.width)))
        im.paste(art,(1000,285));d=ImageDraw.Draw(im)
        text(d,(1000,860),'GERÇEK BASS DENEYİ / NASA',25,AMBER,True)
    elif index in (2,6):
        labels=[('A','BASS-II','Yayılma hızı / mm/s'),('B','Saffire-I','Sırt konumu / mm'),('C','SAME + SAME-R','Eşik etiketi')]
        for j,(letter,name,unit) in enumerate(labels):
            y=275+j*170
            card(d,(1000,y,1775,y+135))
            text(d,(1030,y+23),letter,55,AMBER,True)
            text(d,(1130,y+20),name,31,WHITE,True)
            text(d,(1130,y+73),unit,24,MUTED)
            x=1000+((local*.12+j*.21)%1)*775
            d.ellipse((x-5,y+130,x+5,y+140),fill=ACCENT)
        if index==6:
            text(d,(1010,820),'ÖLÇÜM  /  TÜRETİLMİŞ DEĞER  /  TAHMİN',24,ACCENT)
            text(d,(1010,865),'Kaynaklı katalog + WT4 metin aracı',24,MUTED)
    elif index==3:
        if local<3:
            art=bass.resize((800,int(800*bass.height/bass.width)))
            im.paste(art,(1000,285));d=ImageDraw.Draw(im)
            text(d,(1000,860),'BASS / yanma ve söndürme araştırması',24,ACCENT,True)
            text(d,(1000,905),'NASA arşiv görüntüsü / ISS040E023287',20,MUTED)
        else:
            art=event_image(.18+.45*ease((local-3)/20),(1120,630))
            im.paste(art,(800,235));d=ImageDraw.Draw(im)
            card(d,(1000,760,1810,870),(31,27,22))
            text(d,(1030,775),'0,09522 mm/s',43,WHITE,True)
            text(d,(1030,835),'Model A tahmini / temsili 3B olaydan ayrı hesaplanır',20,MUTED)
            text(d,(1000,900),'18 numune • iç içe çapraz doğrulama R² negatif',21,MUTED)
    elif index==4:
        iw=780;ih=int(iw*photo.height/photo.width);x=1000;y=255
        im.paste(photo.resize((iw,ih)),(x,y));d=ImageDraw.Draw(im)
        text(d,(1000,225),'NASA görüntüsü • gösterim parlaklığı artırıldı',20,MUTED)
        progress=ease((local-2)/4);px=x+iw*(.8+(.28475-.8)*progress)
        line(d,[(px,y),(px,y+ih)],AMBER,4)
        card(d,(1010,835,1790,925))
        text(d,(1030,849),'220,29 mm',38,WHITE,True)
        text(d,(1400,861),'TAHMİNİ SIRT KONUMU',22,AMBER)
        if local>10:
            text(d,(1000,185),'Konum hatası: 4,829 mm • temel yöntem: 4,545 mm',21,MUTED)
    elif index==5:
        card(d,(970,245,1825,875))
        text(d,(1000,265),'2,0 V EŞİĞİNE ULAŞAN BİRİNCİL KOŞULAR',24,ACCENT,True)
        for j,r in enumerate(runs):
            y=350+j*92;n=int(r['n_runs']);yes=int(r['n_reaching_2v'])
            text(d,(1005,y),r['material'],26,WHITE)
            for c in range(n):
                x=1180+c*22;filled=c<yes and local>1+c*.13+j*.3
                d.ellipse((x,y+8,x+13,y+21),fill=AMBER if filled else (72,63,52))
            text(d,(1685,y),f'{yes}/{n}',27,AMBER,True)
        text(d,(1000,820),'TÜRETİLMİŞ • deney sayımları • alarm olasılığı içermez',21,MUTED)
    elif index==7:
        for j,group in enumerate(benchmarks['groups'][:3]):
            rows=group['rows']
            ours=next(r for r in rows if r['ours'])
            ref=rows[-1] if j==0 else rows[1]
            y=245+j*208
            card(d,(970,y,1825,y+188))
            name=['A / Alev yayılması','B / Sırt konumu','C / 2,0 V etiketi'][j]
            metric=['Hata mm/s (düşük iyi)','Hata mm (düşük iyi)','Dengeli doğruluk'][j]
            text(d,(995,y+14),name,26,ACCENT,True)
            text(d,(1485,y+20),metric,20,MUTED)
            text(d,(995,y+58),'QK norm',23,WHITE)
            text(d,(1200,y+54),(f"{ours['score']:.5f}" if j!=1 else f"{ours['score']:.3f}").replace('.',','),31,AMBER,True)
            text(d,(1455,y+58),'/',22,MUTED)
            text(d,(1530,y+54),(f"{ref['score']:.5f}" if j!=1 else f"{ref['score']:.3f}").replace('.',','),31,WHITE,True)
            reference=['Altı yöntemin medyanı • türetilmiş','İkili eşik-medyan temel yöntemi','Malzeme-çoğunluk temel yöntemi'][j]
            text(d,(995,y+106),reference,22,MUTED)
            conclusions=['%12,4 düşük hata • geriye dönük karşılaştırma','Temel yöntem üstün • aynı yanmadan 6 kare','Yayımlanan değişkenlik kuralına göre beraberlik']
            text(d,(995,y+146),conclusions[j],23,ACCENT)
        text(d,(980,900),'A: iç içe CV R² −0,444 • WT4: kalite karşılaştırması yok',21,MUTED)
    elif index==8:
        # Genuine rendered UI capture with a slow controlled dolly.
        z=1+.025*ease(local/15)
        shot=dash.resize((int(830*z),int(830*dash.height/dash.width*z)))
        im.paste(shot,(980,265));d=ImageDraw.Draw(im)
        line(d,[(980,245),(1810,245)],ACCENT,3)
        text(d,(990,895),'Çalışan Python API + etkileşimli arayüz',23,ACCENT)
    elif index==9:
        card(d,(970,260,1825,855))
        text(d,(1000,285),'TERMINAL / GERÇEK ÇALIŞTIRMA',24,ACCENT,True)
        commands=['$ python -m qk_norm_blindspot','  experiment sweep a','  --field velocity_cm_s','  --values 6,8,9 --output sonuc.json']
        for j,row in enumerate(commands):
            if local>j*.5:text(d,(1000,350+j*44),row,24,WHITE,True)
        if local>3:
            text(d,(1000,565),'Hava hızı → tahmini yayılma hızı',24,AMBER,True)
            for j,run in enumerate(cli['runs']):
                v=run['input']['velocity_cm_s'];rate=run['output']['response']['predicted_flame_spread_rate']
                text(d,(1020,620+j*52),f"{v:g} cm/s  →  {rate:.5f} mm/s".replace('.',','),28,WHITE,True)
            text(d,(1000,805),'3 deneme tamamlandı • JSON kaydedildi',22,ACCENT)
    context_details={
        2:['BASS / BASS-II, Saffire ve SAME farklı soruları inceler.','Sistem bu deneyleri kendi bağlamında açıklar.'],
        3:['Dört girdiyle, deney kapsamı içinde tahmin üretir.','Diğer malzeme veya geometri için doğrulanmadı.'],
        4:['Konum, görüntünün sol kenarından ölçülür.','Öğrenilmiş düzeltme temel yöntemi iyileştirmedi.'],
        5:['Eşik etiketi, kayıtlı voltajdan türetilir.','Kapton ve Teflon için tahmin gücü sınırlıdır.'],
        6:['NASA 2025 ihtiyacı: seçici algılama ve toz ayrımı.','Katkımız: koşul, sonuç ve kaynak bağlamını birleştirmek.'],
        7:['A karşılaştırması geriye dönük; C sonucu berabere.','Bu sonuçlar görevler arasında ortak puan oluşturmaz.'],
        8:['Örnek seçimiyle malzeme ve koşullar görünür olur.','Sayısal sonuç kısa bir açıklamayla birlikte sunulur.'],
        9:['Tekrarlanabilir model denemeleri ve kayıtlı girdiler.','Sonuçlar JSON dosyasına kaydedilir.'],
        10:['Hedefimiz: algılama sınırlamalarını görünür kılmak.','Sonraki adım: yeni koşullarda bağımsız doğrulama.']}
    if index in context_details and local>3:
        for j,item in enumerate(context_details[index]):
            text(d,(100,(695 if index==10 else 610)+j*34),item,20,MUTED,True)
    features={
        3:['Kalınlık / genişlik / hava akışı / O₂','Çıktı: yayılma hızı (mm/s)','PMMA levha / karşı akış koşulları'],
        4:['Gerçek NASA kamera karesi','Parlak sırt → yatay konum (mm)','Tek görev / tek fiziksel numune'],
        5:['Malzeme + beş kontrol girdisi','Hedef: 2,0 V eşik etiketi','En yakın ölçüm + kapsam uyarısı'],
        6:['A/B/C: farklı deneyler, farklı görevler','Katalog: kaynak ve koşul bağlamı','WT4: bağımsız metin üretimi']}
    if index in features and local>3:
        for j,item in enumerate(features[index]):
            text(d,(100,690+j*44),item,23,ACCENT,True)
    messages={2:'NASA VERİSİYLE BAŞLA.',3:'KOŞULU DEĞİŞTİR. TAHMİNİ İNCELE.',
              4:'GÖRÜNTÜYÜ ÖLÇÜME DÖNÜŞTÜR.',5:'ÖLÇÜMÜ VE TAHMİNİ BİRLİKTE GÖR.',
              6:'KAYNAĞIYLA AÇIKLA.',8:'HAZIR ÖRNEKLE HEMEN DENE.',9:'TEK KOMUTLA KARŞILAŞTIR.'}
    if index in messages and end-t<3 and end-t>.65:
        card(d,(90,825,825,915),(35,29,23))
        wrapped(d,messages[index],115,845,680,25,ACCENT)
    # Brief cross-dissolve through consistent background at scene boundaries.
    chapter=next(c for c in chapters if c[0]<=t<c[1])
    fade=min(ease((t-chapter[0])/.6),ease((chapter[1]-t)/.6))
    if fade<1:im=Image.blend(base,im,fade)
    return im

def frame(t):
    idx=next((i for i,s in enumerate(scenes) if s[0]<=t<s[1]),10)
    im=draw_scene(idx,t)
    chapter_index=next(i for i,c in enumerate(chapters) if c[0]<=t<c[1])
    d=ImageDraw.Draw(im)
    card(d,(1720,985,1840,1023),(31,27,22),(78,68,57),8)
    text(d,(1740,991),f'{chapter_index+1:02} / 07',19,ACCENT,True)
    return im
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');args=parser.parse_args()
    out=ROOT/'deliverables';out.mkdir(exist_ok=True)
    duration=8 if args.preview else scenes[-1][1]
    path=out/('preview.mp4' if args.preview else 'jury_animation.mp4')
    command=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(path)]
    proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    for n in range(duration*FPS):
        proc.stdin.write(frame(n/FPS).tobytes())
        if n%240==0:print(f'{n/FPS:.0f}/{duration}s',flush=True)
    proc.stdin.close()
    if proc.wait():raise SystemExit('FFmpeg failed')
    times=[22,58,78,98,135,163,173]
    sheet=Image.new('RGB',(1440,810),BG)
    (out/'video_chapters.json').write_text(json.dumps([{'page':i+1,'start_s':c[0],'end_s':c[1],'title':c[2]} for i,c in enumerate(chapters)],ensure_ascii=False,indent=2))
    for j,t in enumerate(times):
        still=frame(t);still.save(out/f'page_{j+1:02}.jpg')
        sheet.paste(still.resize((480,270)),((j%3)*480,(j//3)*270))
    sheet.save(out/'contact_sheet.jpg')
    # Preserve the asset names used by the separate PDF producer.
    for j,t in enumerate([8,22,37,58,78,98,117,135,150,163,173]):
        frame(t).save(out/f'scene_{j+1:02}.jpg')
    print(path,flush=True)
if __name__=='__main__':main()
