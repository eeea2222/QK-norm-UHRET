"""Illustrated Turkish jury script aligned to the 177-second film."""
from pathlib import Path
import json, sys
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from PIL import Image
import render
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output/pdf/juri_konusma_rehberi.pdf'
pdfmetrics.registerFont(TTFont('Noto',render.FONT));pdfmetrics.registerFont(TTFont('NotoBold',render.BOLD))
pdfmetrics.registerFontFamily('Noto',normal='Noto',bold='NotoBold')
W,H=595.28,841.89
INK='#163238';MUTED='#526768';TEAL='#26796f';BG='#f7f6f1'
script=[
('00:00 - 00:12',9,'Uzayda alevi neden inceliyoruz?',
"Uzayda yangın, mürettebat güvenliği için kritik. Mikro yerçekiminde alev ve duman farklı davranabilir. Bu temsili sahne olayı gösteriyor. QK norm, NASA deneylerini anlaşılır ve karşılaştırılabilir araştırma çıktılarına dönüştürüyor.",
"Alevin gelişimini ve numune üzerindeki ısı kaynağını göster. Hazne ve olay akışının temsili olduğunu belirt.",
"NASA, Studying Combustion and Fire Safety, 26.12.2023. 3B geometri ve hareketler temsili."),
('00:12 - 00:30',15,'NASA hangi ihtiyacı tanımlıyor?',
"Bu sahnede dumanın akışla taşınmasını ve temsili sönümü görüyoruz. NASA, 2025 teknoloji çağrısında dumanı ortam tozundan ayırma ve farklı parçacık koşullarında algılama ihtiyacını tanımlıyor. Biz bu ihtiyaca, mevcut deneylerin malzeme, koşul ve ölçüm farklarını açıkça karşılaştıran çalışan bir araştırma aracıyla katkı veriyoruz.",
"Parçacıkların izlediği yolu işaret et. Isıtmanın kapanması, sahne kurgusudur; model tarafından verilen bir söndürme kararı değildir.",
"NASA FY2025 SBIR, S15.03 / Scope 2, PDF s. 258-259; basılı s. 250-251."),
('00:30 - 00:48',34,'Dayanağımız gerçek NASA deneyleri',
"Burada gerçek bir BASS alev fotoğrafı var. BASS yanma ve söndürme davranışlarını inceliyor. BASS-II, Saffire ve SAME ise farklı numune, donanım ve ölçümler içeriyor. Bu yüzden tek bir genel model kurmak yerine, her görevi kendi deney bağlamında ele alan uzman modeller geliştirdik.",
"Gerçek BASS fotoğrafını göster; onu temsili 3B sahneden ve Model A girdilerinden ayır.",
"NASA görüntüsü ISS040E023287; NASA, Studying Combustion and Fire Safety."),
('00:48 - 01:08',58,'Model A ne hesaplıyor?',
"Model A, PMMA levhanın kalınlığı, genişliği, hava akışı ve oksijen oranından alev yayılma hızını tahmin ediyor. Kayıtlı örnekte sonuç yaklaşık 0,09522 milimetre bölü saniye. Bu model, koşulların etkisini incelemeyi kolaylaştırıyor. Veri kapsamı sınırlı olduğu için sonucu deney alanı içinde yorumluyoruz.",
"Sağdaki sayı gerçek model çıktısıdır. 3B alevin büyüme hızını bu sayıdan üretmedik.",
"external/model_a/README.md; artifacts/model_a_v1/sample_request.json; assets/cli_sweep.json."),
('01:08 - 01:28',78,'Model B görüntüyü ölçüme dönüştürüyor',
"Model B, gerçek Saffire-I kamera karesindeki parlak alev sırtının yatay konumunu ölçüyor. Örnek sonuç yaklaşık 220,29 milimetre. Görüntüden tekrarlanabilir bir sayısal çıktı elde ediyoruz. Değerlendirmede basit yöntem daha düşük hata verdi; bu bulguyu da sunumda açıkça gösteriyoruz.",
"Dikey çizgiyi ve görüntünün sol kenarını göster. Konum hatasının alev yayılma hızıyla aynı nicelik olmadığını açıkla.",
"external/model_b/artifacts/sample_request_response.json; README.md; MAE 4,829 mm / temel yöntem 4,545 mm."),
('01:28 - 01:48',98,'Model C neden önemli?',
"Model C, malzeme ve kontrol girdileriyle kayıtlı saçılma sinyalinin 2 volt eşiğine ulaşıp ulaşmayacağını sınıflandırıyor. Tablodaki noktalar gerçek birincil koşulardan türetilmiş sayımlar. Malzemeler arasında belirgin farklar görülüyor. Buradaki hedef, gerçek operasyonel alarm kaydından farklı bir eşik etiketi; özellikle Kapton ve Teflon tahminlerinde sınırlamalar var.",
"Kapton 9/21 ve Teflon 4/15 sayımlarını işaret et. Bunlar birleşik SAME/SAME-R gözlemleridir; alarm olasılığı olarak sunma.",
"external/model_c/data/processed/dashboard_measured_only.csv; model kartı. Değer türü türetilmiş."),
('01:48 - 02:07',117,'Üç modelin ortak araştırma değeri',
"Çözdüğümüz parça, farklı deneylerin çıktısını tek arayüzde, birimi ve kaynak bağlamıyla anlaşılır hale getirmek. Katalog bulgulara ve koşullara erişim sağlıyor. WT4 ayrı bir metin üretim aracı olarak çalışıyor. Böylece kullanıcı model sonucuyla ölçümü karşılaştırabiliyor ve yeni araştırma sorularını daha açık kurabiliyor.",
"Üç ayrı görev kartını göster. Dashboard kısa açıklamaları şablonlardan gelir; WT4 bağımsız metin üretir.",
"Proje README.md; qk_norm_blindspot/api.py ve agent.py. RAG kaldırıldı; bilimsel doğrulama ertelendi."),
('02:07 - 02:22',135,'Benchmarkı nasıl savunuyoruz?',
"Her modeli kendi göreviyle karşılaştırıyoruz. Model A, altı yöntemin medyanından yüzde 12,4 düşük hata verdi; sonuç geriye dönük. Model B temel yöntemi geçmedi. Model C, yayımlanan kurala göre berabere. Güçlü tarafları ve sınırlamaları birlikte gösteriyoruz.",
"Farklı hata birimlerini ortak başarı yüzdesine dönüştürme. A'nın iç içe CV sonucu negatiftir; C'de malzeme-çoğunluk yaklaşımı güçlüdür.",
"assets/benchmarks.json; outputs/benchmarks.json. A/B/C sabit revizyon değerlendirme raporları."),
('02:22 - 02:37',150,'Jüri arayüzde neyi deneyebilir?',
"Arayüzde hazır bir malzeme ve koşul örneği seçiyoruz. Modeli çalıştırınca sayı, birim ve kısa yorum birlikte görünüyor. Model C, kapsam dışı girdileri ve en yakın ölçümü de gösteriyor. Böylece sonuç yalnızca ekranda bir skor olarak kalmıyor; deney koşuluyla birlikte incelenebiliyor.",
"Örnek seçimi, çalıştır düğmesi ve sonuç açıklamasını sırayla göster. Kayıtla uyuşmayan tahminlerin de görünür olduğunu belirt.",
"Gerçek dashboard kaydı; outputs/ai_playground_tests.json; Model C API çıktıları."),
('02:37 - 02:49',163,'CLI ile hızlı deneme',
"CLI ile tek girdiyi değiştirip sonuçları karşılaştırıyoruz. Hava hızını üç değerde taradık; gerçek çıktılar JSON dosyasına kaydedildi. Böylece araştırmacı aynı karşılaştırmayı kolayca tekrarlayabiliyor.",
"Komuttaki --values 6,8,9 bölümünü ve üç sonuç satırını göster. Bunlar hesaplamalı model sorgularıdır.",
"qk_norm_blindspot/experiment_cli.py; assets/cli_sweep.json. A/B/C/WT4 tek çalıştırmaları tamamlandı."),
('02:49 - 02:57',173,'Kapanış',
"NASA'nın belgelediği algılama ihtiyaçlarını, gerçek deney verisiyle çalışan açık bir araştırma aracına dönüştürüyoruz. Sonraki adımımız yeni koşullarda bağımsız doğrulama.",
"Kısa bitir. Doğrulanmamış fiziksel yangın önleme veya NASA resmî onayı iddiası ekleme.",
"NASA FY2025 SBIR S15.03; mevcut yazılım çıktıları ve proje sınırlamaları.")
]
styles={}
def paragraph(c,text,x,y,width,size=11.7,color=INK,bold=False):
    style=ParagraphStyle('body',fontName='NotoBold' if bold else 'Noto',fontSize=size,leading=size*1.48,textColor=HexColor(color))
    p=Paragraph(escape(text),style);_,height=p.wrap(width,800);p.drawOn(c,x,y-height);return y-height
def header(c,page,label):
    c.setFillColor(HexColor(BG));c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(HexColor(INK));c.setFont('NotoBold',11);c.drawString(42,803,'QK norm')
    c.setFillColor(HexColor(MUTED));c.setFont('Noto',9);c.drawRightString(W-42,803,label)
    c.setStrokeColor(HexColor('#d8dcd5'));c.line(42,788,W-42,788)
    c.setFont('Noto',8);c.drawString(42,25,'Jüri konuşma rehberi • Türkçe • video süresi 2:57')
    c.drawRightString(W-42,25,str(page))
ROOT.joinpath('tmp/pdfs').mkdir(parents=True,exist_ok=True)
c=canvas.Canvas(str(OUT),pagesize=(W,H));c.setTitle('QK norm - Resimli jüri konuşma rehberi');c.setAuthor('QK norm')
header(c,1,'SUNUM REHBERİ')
paragraph(c,'NASA verisinden araştırma kararına',42,752,W-84,27,INK,True)
paragraph(c,'177 saniyelik video için görselli konuşma metni',42,670,W-84,13,TEAL,True)
hero=ROOT/'tmp/pdfs/hero.jpg';render.frame(15).save(hero)
c.drawImage(str(hero),42,350,width=W-84,height=(W-84)*9/16)
y=paragraph(c,'Ana mesaj',42,324,W-84,13,TEAL,True)
y=paragraph(c,"NASA'nın belgelediği yangın algılama ihtiyacına, gerçek deney kayıtlarını koşulları ve kaynaklarıyla karşılaştıran çalışan bir yazılımla katkı veriyoruz.",42,y-10,W-84,14,INK,True)
y=paragraph(c,'Nasıl kullanılır',42,y-20,W-84,12,TEAL,True)
y=paragraph(c,'Sonraki sayfalarda yalnızca “Jüriye söyle” metinlerini okuyun. Görsel notları ve kaynakları prova veya soru-cevap için kullanın. Konuşma, video zamanlarına göre bölünmüştür; sahne geçişlerinde kısa nefes payı bırakın.',42,y-8,W-84,11)
y=paragraph(c,'İddia sınırı',42,y-18,W-84,12,TEAL,True)
paragraph(c,'Çalışan yazılım gösterildi. Bilimsel doğrulama ertelendi. Fiziksel yangını önleyen veya sertifikalı alarm veren bir sistem doğrulanmadı. “NASA acil sorununu tamamen çözdük” ifadesi mevcut kanıtı aşar.',42,y-8,W-84,10.5,MUTED)
c.showPage()
for idx,(timing,t,title,narration,note,source) in enumerate(script):
    header(c,idx+2,timing)
    paragraph(c,title,42,757,W-84,21,INK,True)
    image=ROOT/f'tmp/pdfs/scene_{idx+1:02}.jpg';render.frame(t).save(image)
    c.drawImage(str(image),42,423,width=W-84,height=(W-84)*9/16)
    y=paragraph(c,'Jüriye söyle',42,402,W-84,12,TEAL,True)
    y=paragraph(c,narration,42,y-10,W-84,12)
    y=paragraph(c,'Görselde işaret et',42,y-19,W-84,10.5,TEAL,True)
    y=paragraph(c,note,42,y-7,W-84,10.2,MUTED)
    y=paragraph(c,'Kaynak ve kapsam',42,y-16,W-84,10,TEAL,True)
    bottom=paragraph(c,source,42,y-6,W-84,9,MUTED)
    if bottom<48:raise RuntimeError(f'Sayfa taştı: {idx+2}, y={bottom}')
    c.showPage()
header(c,13,'PROVA / SORU-CEVAP')
y=paragraph(c,'Üç dakikayı aşmadan savun',42,751,W-84,25,INK,True)
nwords=sum(len(x[3].split()) for x in script)
items=[
('Okuma temposu',f'Ana konuşma {nwords} sözcük içerir. 177 saniyeye yaymak için yaklaşık {round(nwords*60/177)} sözcük/dakika gerekir. Kendi kronometreli provanız belirleyicidir. Video 177 saniyedir; 180 saniye sınırına 3 saniye pay kalır.'),
('“Tam olarak ne çözdünüz?”','Deney kapsamlarını, model çıktısını ve kayıtlı gözlemi bir arada inceleme işini çalışan bir yazılım akışına dönüştürdük. Fiziksel yangını önlediğimizi gösteren bir test yapmadık.'),
('“NASA bu ihtiyacı nerede söylüyor?”','FY2025 SBIR, S15.03 / Scope 2, PDF sayfa 258-259; basılı 250-251. Seçici duman algılama, parçacık kapsamı ve ortam tozuyla karışma ihtiyaçları tanımlanıyor. Bunlar teknoloji ihtiyaçlarıdır; küresel başarısızlık oranı değildir.'),
('“Modelleriniz hep daha mı iyi?”','Hayır. A için belirtilen geriye dönük avantaj var. B, basit yöntemin gerisinde. C için sonuç berabere. WT4 için karşılaştırmalı kalite benchmarkı yapılmadı.'),
('“3B alev fizik simülasyonu mu?”','Hayır. Gerçek BASS fotoğrafı ayrı gösterilir. 3B sahne anlatım amaçlıdır; hareket ve sönüm süreleri ölçümden veya model tahmininden üretilmedi.'),
('“Jüri nasıl deneyebilir?”','Hazır dashboard örneğini çalıştırabilir veya CLI ile kayıtlı girdileri seçip tarama yapabilir. Örnek: python -m qk_norm_blindspot experiment sweep a --field velocity_cm_s --values 6,8,9 --output sonuc.json'),
]
for label,body in items:
    y=paragraph(c,label,42,y-18,W-84,12,TEAL,True)
    y=paragraph(c,body,42,y-6,W-84,10.5)
paragraph(c,'Kaynak bağlantıları',42,y-20,W-84,11,TEAL,True)
y-=50
for label,url in [
('NASA FY2025 SBIR PDF','https://www.nasa.gov/wp-content/uploads/2024/01/sbir80nsscfy25sbirphaseiamendment4signed.pdf'),
('NASA BASS ve yangın güvenliği','https://www.nasa.gov/missions/station/studying-combustion-and-fire-safety/'),
('2021 yangın algılama white paper','https://science.nasa.gov/wp-content/uploads/2023/05/154_33f28c6ef0c27b92cf1f526cef0c44b4_Fire_detection_white_paper_final_211031.pdf')]:
 c.setFont('Noto',9);c.setFillColor(HexColor(TEAL));c.drawString(42,y,label);c.linkURL(url,(42,y-2,W-42,y+12),relative=0);y-=21
if y<40:raise RuntimeError('Son sayfa taştı')
c.save()
(ROOT/'tmp/pdfs/narration.json').write_text(json.dumps({'word_count':nwords,'duration_s':177,'script':[{'time':x[0],'text':x[3]} for x in script]},ensure_ascii=False,indent=2))
print(OUT);print('words',nwords,'pages',13)
