"""Seven-page, jury-facing Turkish presentation grounded in the rendered film."""
import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
OUT=ROOT/'output/pdf/QK_norm_Juri_Sunumu_7_Sayfa.pdf'
TEMP=ROOT/'tmp/pdfs/jury7';TEMP.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('Deck', '/usr/share/fonts/noto/NotoSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('DeckBold','/usr/share/fonts/noto/NotoSans-Bold.ttf'))
pdfmetrics.registerFontFamily('Deck',normal='Deck',bold='DeckBold')
W,H=841.89,595.28
BG='#f7f6f1';INK='#153139';MUTED='#546a6d';TEAL='#28796f';AMBER='#b77935';LINE='#d7dfd9'
c=canvas.Canvas(str(OUT),pagesize=(W,H))
c.setTitle('QK norm | NASA Space Apps 2026 | 7 sayfa')
c.setAuthor('QK norm')
NIST='https://www.nist.gov/news-events/news/2018/05/nistnasa-study-shows-one-detector-doesnt-fit-all-smoke-spacecraft'
SBIR='https://www.nasa.gov/wp-content/uploads/2024/01/sbir80nsscfy25sbirphaseiamendment4signed.pdf'
BASS='https://www.nasa.gov/missions/station/studying-combustion-and-fire-safety/'
def para(text,x,y,width,size=11,color=INK,bold=False):
    style=ParagraphStyle('p',fontName='DeckBold' if bold else 'Deck',fontSize=size,leading=size*1.42,textColor=HexColor(color))
    p=Paragraph(escape(text),style);_,height=p.wrap(width,1000);p.drawOn(c,x,y-height)
    if y-height<36:raise ValueError('Text exceeds page: '+text[:30])
    return y-height
def label(text,x,y,color=TEAL,size=9):
    c.setFont('DeckBold',size);c.setFillColor(HexColor(color));c.drawString(x,y,text)
def card(x,y,w,h,fill='#ffffff',stroke=LINE):
    c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke));c.roundRect(x,y,w,h,12,fill=1,stroke=1)
def image(path,x,y,w,h):
    im=Image.open(path).convert('RGB')
    im.thumbnail((int(w*3),int(h*3)))
    p=TEMP/(Path(path).stem+'_display.jpg');im.save(p,quality=95)
    c.drawImage(str(p),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c')
def header(page,section,title,subtitle):
    c.setFillColor(HexColor(BG));c.rect(0,0,W,H,fill=1,stroke=0)
    label('QK norm',42,H-34,INK,12)
    c.setFont('Deck',9);c.setFillColor(HexColor(MUTED));c.drawRightString(W-42,H-34,'NASA SPACE APPS 2026')
    c.setStrokeColor(HexColor(LINE));c.line(42,H-48,W-42,H-48)
    label(section.upper(),42,H-71)
    title_size=min(27,27*(W-84)/pdfmetrics.stringWidth(title,'DeckBold',27))
    para(title,42,H-84,W-84,title_size-.2,INK,True)
    para(subtitle,42,H-128,W-84,10.5,MUTED)
    c.setFont('Deck',8);c.drawString(42,23,'QK norm / araştırma ve bilimsel karar desteği')
    c.drawRightString(W-42,23,f'{page} / 7')
def source(text,url=None):
    para(text,42,53,W-84,7.8,MUTED)
    if url:c.linkURL(url,(42,37,W-42,55),relative=0)
def end():c.showPage()
frames=ROOT/'deliverables'
# 1
header(1,'Ana problem','NASA’nın belgelediği ihtiyaç. Veriden araştırma kararına.','Uzay aracı yangın algılamasını deney, koşul ve kaynak bağlamında anlamak.')
image(frames/'scene_01.jpg',428,238,372,209)
para('Mikro yerçekiminde dumanın taşınması ve parçacık özellikleri, sensörün yanıtını etkiler. Aynı algılama yaklaşımının bütün malzemelerde aynı sonucu vermesi beklenemez.',42,439,355,14,INK,True)
para('Çözdüğümüz parça, farklı deney kayıtlarını kaynaklı, karşılaştırılabilir ve anlaşılır inceleme işidir. Çalışan yazılımımız sensör geliştirme araştırmalarına bilimsel karar desteği sunar.',42,332,355,11.3)
for x,year,word,body in [
(42,'2018','DISCOVERED','NASA/NIST, belirli dumanlarda algılama sınırlamalarını raporladı.'),
(300,'2025','PRIORITIZED','NASA yeni algılama teknolojileri için resmî ihtiyaç tanımladı.'),
(558,'2026','QK norm','Üç bilimsel ML modülü ve kaynaklı araştırma bağlamı.')]:
    card(x,93,242,126)
    label(year,x+16,190,AMBER,21);label(word,x+16,169,TEAL,11)
    para(body,x+16,154,210,10.3)
source('2018: NIST, 01.05.2018; DOI 10.1016/j.firesaf.2018.04.004. 2025: NASA SBIR S15.03, PDF s. 258-259 / basılı s. 250-251.',NIST)
end()
# 2
header(2,'Bilimsel dayanak','Sorun deneyle belgelendi. İhtiyaç resmî çağrıda tanımlandı.','2018 deneysel bulgu ile 2025 teknoloji ihtiyacı farklı kanıt türleridir.')
card(42,315,366,129)
label('2018 / NASA + NIST',58,422)
para('ISS fotoelektrik dedektörü, belirli koşullarda Teflon ve Kapton kaynaklı küçük duman parçacıklarını algılamakta zorlandı. Bulgular kontrollü deneylerin kapsamıyla sınırlıdır.',58,404,334,11.2)
para('Kaynak: NIST araştırma özeti; Fire Safety Journal 98 (2018), s. 74-81.',58,337,334,8.2,MUTED)
c.linkURL(NIST,(58,324,390,350),relative=0)
card(426,315,374,129)
label('2025 / NASA SBIR S15.03',442,422)
para('Dumanın ortam tozundan seçici ayrımı, geniş parçacık kapsamı ve birden çok fiziksel özelliğin ölçülmesi talep ediliyor. Toz kaynaklı yanlış alarm, alarm verilmemesinden ayrı bir sorundur.',442,404,342,11.2)
label('Fire Safety for Habitation / ID 1520 / 10. sıra',442,333,AMBER,9.3)
# Authentic NASA page crops preserve exact wording.
page=Image.open(ROOT/'assets/sbir_251.png')
page.crop((160,770,1245,960)).save(TEMP/'nasa_excerpt.png')
page.crop((160,1455,1245,1545)).save(TEMP/'nasa_rank.png')
label('GERÇEK BELGE GÖRÜNTÜSÜ / BASILI SAYFA 251',42,294)
image(TEMP/'nasa_excerpt.png',42,143,758,133)
image(TEMP/'nasa_rank.png',42,71,758,63)
source('NASA FY2025 SBIR, S15.03 / Fire Detection Sensing for Space Research, PDF s. 259, basılı s. 251. “10. sıra” belgedeki Civil Space Shortfall ID 1520 içindir.',SBIR)
end()
# 3
header(3,'Çözüm mimarisi','Üç deney. Üç uzman görev. Ortak açıklama katmanı.','Deneyleri tek bir yangın senaryosuna veya ortak tehlike puanına birleştirmiyoruz.')
columns=[
(42,'MODEL A / BASS-II','scene_04.jpg','PMMA alev yayılma hızı',
'Girdi: kalınlık, genişlik, hava hızı, başlangıç oksijeni.','Çıktı: mm/s cinsinden tahmin.',
'18 numune / 39 hava akışı segmenti. İç içe çapraz doğrulama R² negatif; keşif amaçlı.'),
(300,'MODEL B / SAFFIRE-I','scene_05.jpg','Görüntüden parlak sırt konumu',
'Girdi: NASA tarafından haritalanmış kamera C1 karesi.','Çıktı: sol kenardan yatay konum, mm.',
'Tek görev ve tek fiziksel numune. Etiketler agent anotasyonu; bağımsız yangın tahmini sağlamaz.'),
(558,'MODEL C / SAME + SAME-R','scene_06.jpg','Saçılma eşiği sınıflandırması',
'Girdi: malzeme ve beş kontrol değişkeni.','Hedef: kayıtlı sinyalin 2,0 V eşiğine erişmesi.',
'Gerçek operasyonel alarm etiketi içermez. Tahmin, ölçümden ayrı sunulur; Kapton/Teflon için sınırlıdır.')
]
for x,title,filename,task,a,b,limit in columns:
    card(x,105,242,340)
    label(title,x+14,425)
    image(frames/filename,x+12,283,218,123)
    y=para(task,x+14,271,214,12,INK,True)
    y=para(a,x+14,y-9,214,9.6)
    y=para(b,x+14,y-6,214,9.6,TEAL,True)
    bottom=para(limit,x+14,y-10,214,9,MUTED)
    examples={42:'Örnek tahmin: 0,09522 mm/s.',300:'Örnek konum: 220,29 mm.',558:'Örnek: Kapton için eşiğe ulaşmaz tahmini.'}
    para(examples[x],x+14,bottom-9,214,8.7,TEAL,True)
para('WT4 + katalog',42,95,160,11,TEAL,True)
para('WT4 bağımsız metin üretir. Yapılandırılmış katalog, bulguları kaynak ve koşullarıyla sunar. Dashboard kısa açıklamaları deterministik şablonlarla üretilir.',200,95,600,10)
source('NASA PSI-25, PSI-98, PSI-102 ve PSI-101; sabit revizyonlu ekip model kartları ve mevcut proje README dosyası.')
end()
# 4
header(4,'Model C / gerçek kayıtlar','Malzeme farkı, algılama sorusunun merkezinde.','Grafik birincil koşularda 2,0 V’a ulaşan kayıtları gösterir; alarm olasılığı değildir.')
rows=list(csv.DictReader(open(PROJECT/'external/model_c/data/processed/dashboard_measured_only.csv')))
order=['Kapton','Teflon','Lampwick','Pyrell','Silicone']
rows=sorted(rows,key=lambda r:order.index(r['material']))
card(42,138,470,306)
label('BİRİNCİL KOŞU SAYIMI / TÜRETİLMİŞ DEĞER',58,422)
label('Malzeme',58,392,MUTED);label('Eşiğe erişen / koşu',287,392,MUTED);label('Grup',448,392,MUTED)
for i,r in enumerate(rows):
    y=354-i*43;n=int(r['n_runs']);k=int(r['n_reaching_2v'])
    label(r['material'],58,y,INK,11)
    c.setFillColor(HexColor('#e2e7e1'));c.roundRect(155,y-1,117,10,5,fill=1,stroke=0)
    c.setFillColor(HexColor(TEAL));c.roundRect(155,y-1,117*k/n,10,5,fill=1,stroke=0)
    label(f'{k} / {n}',302,y,INK,12);label(r['n_groups'],460,y,INK,10)
para('Aynı deneye ait ikincil yaşlandırma kayıtları bağımsız koşu olarak sayılmaz. Grup sayıları, koşular arası bağımlılığı görünür kılar.',58,165,438,9.5,MUTED)
card(532,138,268,306)
label('GERÇEK ÖRNEK / KAPTON',548,422)
para('Tahmin ve ölçüm birlikte görünür.',548,396,236,17,INK,True)
para('Model C tahmini',548,335,236,10,MUTED)
para('2,0 V eşiğine ulaşmaz',548,315,236,14,TEAL,True)
para('En yakın kayıt: SAME:29',548,273,236,10,MUTED)
para('3,663712 V ölçüldü',548,252,236,15,INK,True)
para('Bu örnekte tahmin ölçümle uyuşmuyor. Saydam karşılaştırma, modelin sınırlamasını da gösteriyor.',548,218,236,10.3)
para('Bilimsel ayrım',42,113,140,11,TEAL,True)
para('2021 white paper alarm sonuçları, burada kullanılan SAME + SAME-R 2,0 V sayımlarıyla birleştirilmez. Tanım ve test kümeleri farklıdır.',200,113,600,10)
source('dashboard_measured_only.csv; dashboard_table.csv; PSI-102 / PSI-101; gerçek Model C çalıştırması: outputs/ai_playground_tests.json.')
end()
# 5
header(5,'BlindSpot Discovery','Eksik kanıtı görünür kıl. Sonraki araştırma sorusunu kur.','Gerçek katalog çıktısı; araştırma boşlukları yalnızca incelenen kaynaklar kapsamında yorumlanır.')
card(42,244,365,200)
label('ÖRNEK SORU',58,422)
para('PMMA dumanı ISS dedektörünü tetikler mi?',58,399,333,21,INK,True)
label('KATALOG SONUCU',58,329)
para('Yetersiz bilgi / INSUFFICIENT_INFORMATION',58,311,333,12,TEAL,True)
para('İncelenen kaynaklarda PMMA için mikro yerçekimi alarm ölçümü yetersiz. İlgili 1 g test sinyal-kütle ilişkisini ölçüyor.',58,279,333,10.1)
card(426,244,374,200)
label('KAYNAK İZİ',442,422)
para('GAP-MATERIAL-PMMA',442,398,342,17,INK,True)
para('FU-EV-003 / FU-EV-001 / FU-EV-009 / FU-EV-010',442,365,342,10,MUTED)
para('Gerekçeli sonraki soru',442,327,342,11,TEAL,True)
para('Aynı malzeme ve dedektör için, yerçekimi ve deney koşulları eşleştirilmiş ölçümler ne gösterir?',442,304,342,13,INK,True)
label('SINIFLARIN ANLAMI',42,220)
labels=[
('Belgelenmiş sınırlama','Belirli koşullarda raporlanan algılama sorunu.'),
('Kanıt boşluğu','Kapsanan kaynaklarda yeterli ölçüm veya karşılaştırma yok.'),
('Çelişen kanıt','Koşullar ve tanımlar ayrıca incelenmeli.'),
('Yetersiz bilgi','Güvenilir sonuç için mevcut veri yetmiyor.')]
for j,(name,body) in enumerate(labels):
 x=42+(j%2)*384;y=172-(j//2)*52
 label(name,x,y,INK,10.5);para(body,x,y-8,360,9.6,MUTED)
source('Gerçek çağrı: analyze_blindspots(..., filters={"material":"PMMA"}); assets/jury_blindspot.json. Katalog ve araştırma önerileri için yeni bilimsel doğrulama ertelendi.')
end()
# 6
header(6,'Çalışan yazılım / değerlendirme','Örnek seç. Modeli çalıştır. Sonucu açıklamasıyla incele.','Dashboard, gerçek model endpoint’leri ve CLI ile hesaplamalı denemeler.')
image(ROOT/'assets/dashboard.png',42,181,371,247)
label('ARAYÜZDEN VEYA CLI’DEN DENE',42,158)
card(42,82,371,59,fill='#183239',stroke='#183239')
c.setFillColor(HexColor('#eff5ee'));c.setFont('Deck',8.3)
for j,line in enumerate(['python -m qk_norm_blindspot experiment sweep a','  --field velocity_cm_s --values 6,8,9','  --output sonuc.json']):c.drawString(54,123-j*13,line)
label('KAYITLI BENCHMARKLAR',437,429)
results=[
('A / MAE (mm/s, düşük daha iyi)','0,01497 / 0,01710','Bizim model / altı yöntemin medyanı. %12,4 fark; geriye dönük karşılaştırma.','5 gruplu kat; iç içe CV R² -0,444; dış test yok.'),
('B / MAE (mm, düşük daha iyi)','4,829 / 4,545','Öğrenilmiş düzeltme / temel yöntem. Temel yöntem üstün.','Tek numune, aynı yanmadan 6 kare; etiketler agent anotasyonu.'),
('C / dengeli doğruluk','0,90043 / 0,89134','Sabit orman / malzeme-çoğunluk yöntemi. Yayımlanan kurala göre beraberlik.','5 dış kat; 84 birincil koşu / 81 grup; fark oynaklık sınırında.')
]
for j,(name,score,note,caveat) in enumerate(results):
 y=311-j*105;card(426,y,374,96)
 label(name,440,y+77,TEAL,9.6)
 label(score,440,y+54,INK,16)
 para(note,440,y+42,346,9.1)
 para(caveat,440,y+14,346,7.7,MUTED)
para('WT4 için eşleştirilmiş kalite benchmarkı bulunmuyor. Model yükleme ve üretim testleri kalite puanı olarak sunulmaz.',437,86,350,8.3,MUTED)
source('Gerçek arayüz ve A/B/C/WT4 çalıştırmaları; assets/cli_sweep.json; outputs/benchmarks.json. Farklı görevler için ortak başarı puanı üretilmez.')
end()
# 7
header(7,'Araştırma etkisi / kapanış','NASA’nın ihtiyacından daha açık araştırma kararlarına.','QK norm, sensör geliştirme ihtiyacını kaynaklı bilimsel karar desteğiyle tamamlar.')
card(42,294,366,150)
label('BUGÜN ÇALIŞAN KATKI',58,423)
para('Deneyleri koşullarıyla karşılaştırmak; model sonucunu ölçümden ayırmak; belgelenmiş sınırlamaları ve eksik kanıtı görünür kılmak.',58,401,334,14,INK,True)
para('A/B/C modelleri, dashboard, yapılandırılmış katalog ve tekrar edilebilir CLI denemeleri.',58,326,334,10.3)
card(426,294,374,150)
label('SONRAKİ ARAŞTIRMA ADIMI',442,423)
para('Öncelikler görev ilgisi, belgelenmiş sınırlama ve kanıt kalitesiyle gerekçelendirilir.',442,401,342,14,INK,True)
para('Koşul kapsamı, karşılaştırılabilirlik ve yeni bilgi katkısı da değerlendirilir. Yeni bilimsel doğrulama ertelendi.',442,326,342,10.3,MUTED)
para('NASA ihtiyacı belgeledi. Daha iyi algılamayı önceliklendirdi. QK norm, deneysel kanıtları daha açık araştırma kararlarına dönüştürmeye yardımcı olur.',42,271,758,17,TEAL,True)
para('Kapsam',42,196,90,10.5,INK,True)
para('Fiziksel dedektör geliştirilmedi. Operasyonel alarm veya yangın önleme başarısı doğrulanmadı. 3B olay anlatımı temsili; ölçülmüş alev/sönüm dinamikleri veya CFD çözümü içermez. NASA resmî onayı iddiası bulunmaz.',137,196,663,9.8,MUTED)
label('SEÇİLİ KAYNAKLAR / BAĞLANTILAR',42,135)
refs=[
('2018 NASA/NIST - Fire Safety Journal 98, s. 74-81; DOI 10.1016/j.firesaf.2018.04.004',NIST),
('2025 NASA SBIR S15.03 - PDF s. 258-259, basılı s. 250-251; ID 1520 / 10. sıra',SBIR),
('NASA BASS araştırma görseli - ISS040E023287',BASS),
('Model kartları ve sabit revizyonlar - mevcut proje kayıtları','https://huggingface.co/efe-T')
]
for j,(name,url) in enumerate(refs):
 y=115-j*16;para(name,42,y,758,8.3,TEAL);c.linkURL(url,(42,y-12,800,y+2),relative=0)
source('Bu sunum, 177 saniyelik film ve mevcut çalışan proje çıktılarından hazırlanmıştır. Filmdeki görseller kullanılmış, belge kanıtı ayrıca eklenmiştir.')
end()
c.save()
print(OUT)
