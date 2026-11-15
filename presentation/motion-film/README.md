# QK norm — Türkçe jüri filmi

Son film **177 saniye (2:57)**, 1920×1080, 24 FPS, H.264/yuv420p MP4.
Kısa kalın amaç ve gerekçe metinleri, gerçek deney görüntüleri, benchmark sonuçları ve çalışan CLI örneği içerir.
Seslendirme ve müzik eklenmedi.

## Dosyalar

- deliverables/jury_animation.mp4 — tamamlanmış film
- deliverables/contact_sheet.jpg — sahne özeti
- deliverables/encoded_contact_sheet.jpg — MP4 içinden çıkarılan kontrol kareleri
- deliverables/verification.json — ffprobe, tam çözümleme ve biçim kontrolleri
- render.py — yeniden kullanılabilir tipografi, kartlar, zaman çizelgesi, parçacıklar ve geçişler
- build_flame.py — özgün Blender sahnesi üretimi
- assets/microgravity_chamber.blend — düzenlenebilir metre birimli 3B hazne
- assets/cli_*.json — gerçek CLI çalıştırma sonuçları

## Yeniden üretim

Proje kökünden çalıştırın.

```bash
blender -b -t 8 --python presentation/motion-film/build_flame.py
blender -b -t 8 --python presentation/motion-film/animate_camera.py
blender -b -t 8 --python presentation/motion-film/animate_event.py
.venv/bin/python presentation/motion-film/render.py --preview
.venv/bin/python presentation/motion-film/render.py
.venv/bin/python presentation/motion-film/verify.py
```

Mevcut 37 kamera karesi duruyorsa Blender adımları isteğe bağlıdır.
Gereksinimler Pillow, FFmpeg/libx264, Blender ve render.py içindeki yollarda Noto Sans fontlarıdır.
Tam render sırasında model çalıştırılmaz. CLI sonuçları ve görüntüler hazır dosyalardan okunur.

## Sahne akışı

| Süre | Amaç ve görsel |
|---|---|
| 0–12 | Tam ekran 3B olay, numune ısıtılması ve alev zarfının gelişimi |
| 12–30 | 3B duman taşınımı, ısı kaynağının kapatılması ve temsili sönüm |
| 30–48 | Gerçek NASA BASS fotoğrafı, ardından farklı deneylerin ayrımı |
| 48–68 | 3B olay yakın planı yanında Model A ve ayrı hesaplanan yayılma hızı |
| 68–88 | Model B, gerçek Saffire karesi ve sırt konumu |
| 88–108 | Model C, malzeme bazında kayıtlı 2,0 V sayımları |
| 108–127 | Üç uzman model, kaynaklı katalog ve WT4 metin aracı |
| 127–142 | Model A/B/C benchmark sonuçları ve sınırlamalar |
| 142–157 | Gerçek çalışan Türkçe dashboard kaydı |
| 157–169 | CLI ile tek girdi taraması, üç gerçek tahmin ve JSON dışa aktarımı |
| 169–177 | Projenin araştırma amacı ve 3B kapanış |

## Mevcut uygulamanın kısa özeti

Python API, A/B/C model sarmalayıcıları, hazır girdiler ve dashboard çalışır durumdadır.
A, BASS-II koşullarındaki PMMA alev yayılma hızını tahmin eder.
B, belirli Saffire-I kamera görüntüsünde parlak sırt konumunu ölçer.
C, kayıtlı ISS saçılmasının 2,0 V eşiğine erişmesinden türetilmiş etiketi tahmin eder.
WT4, ayrı bir metin üretim uç noktasıdır. Dashboard kısa açıklamaları deterministik şablonlardan gelir.
Katalog açık filtrelerle çalışır. RAG kaldırılmış, yeni bilimsel doğrulama ertelenmiştir.
CLI hesaplamalı model denemesi içindir.

## Teknik iddiaların kaydı

- A örnek çıktısı 0,09522 mm/s: outputs/ai_playground_tests.json ve assets/cli_sweep.json.
  18 numune/39 segment ve negatif iç içe CV R²: external/model_a/README.md.
- B 220,289791 mm ve yatay 484,63754 piksel: external/model_b/artifacts/sample_request_response.json.
  Overlay özgün 1702 piksel genişliği korur. Hareketli çizgi grafik geçişidir.
  MAE 4,829 mm ve temel yöntem 4,545 mm: external/model_b/README.md.
- Kapton 9/21, Teflon 4/15, Lampwick 17/17, Pyrell 12/12, Silicone 19/19:
  external/model_c/data/processed/dashboard_measured_only.csv. Bunlar birincil koşu sayımlarıdır.
- Benchmarklar: assets/benchmarks.json, outputs/benchmarks.json dosyasından dondurulmuştur.
  A'nın %12,4 farkı geriye dönük sabit aday karşılaştırmasıdır; medyan altı karşılaştırma yönteminden türetilmiştir.
  B'de temel yöntem üstündür. C yayımlanan değişkenlik kuralına göre beraberedir.
  WT4 kalite benchmarkı mevcut değildir.
- Taşınım bağlamı: 2021 NASA yangın algılama white paper PDF s. 2, sources/extracted/wp2021.json.
- Hazne, alev, kablolar, lens ve paneller özgün temsili geometridir. Metre birimi kullanılır.
  NASA donanımının ölçülü rekonstrüksiyonu veya CFD çözümü değildir.
  Filmde kamera dönüşü ve yaklaşma/uzaklaşma Blender içinde anahtar karelerle üretilir.
  Ön/sağ kesit açık tutulur. 37 kamera karesi 1280×720 üretilir ve 1120×630 görsel alanda
  24 FPS kareler arasında harmanlanır. Açılışta genel görünümden numuneye yaklaşılır, sonra
  düzenek yeniden açılır. Finalde kamera yolu ters oynatılır.
- Kaynak görüntülerinin ve model dosyalarının mevcut lisans/atıf koşulları external altındaki kayıtlarda korunur.

## Görüntü kaynakları

NASA BASS: ISS040E023287, kredi NASA.
https://www.nasa.gov/missions/station/studying-combustion-and-fire-safety/
https://www.nasa.gov/wp-content/uploads/2019/09/iss040e023287medium.jpg

BASS görseli Model A'nın BASS-II girdisi veya çıktısı olarak kullanılmaz.
Gerçek Saffire karesi NASA PSI-98 kaynaklıdır; external/model_b/NOTICE ve kaynak manifestine bakın.
Görüntüleme için gamma parlaklığı yükseltilmiştir ve filmde etiketlenmiştir.
Dashboard görseli, Model C gerçek endpoint çalıştırması sonrasında alınmıştır.

## CLI ile hızlı deneme

```bash
.venv/bin/python -m qk_norm_blindspot experiment list
.venv/bin/python -m qk_norm_blindspot experiment run c --preset 1 --output sonuc_c.json
.venv/bin/python -m qk_norm_blindspot experiment sweep a --field velocity_cm_s --values 6,8,9 --output sonuc_a.json
```

Kaynak qk_norm_blindspot/experiment_cli.py dosyasındadır.
A/B/C/WT4 tek çalıştırma, A/C sayısal girdi taraması sağlar.
Girdiler, sürümler, kapsam dışı bayrakları ve çıktılar JSON'a kaydedilir.
Hata durumunda tamamlanan koşular korunur, PARTIAL/FAILED durumu ve çıkış kodu 1 döner.
A/B/C/WT4 gerçek CLI çalıştırmaları assets/cli_*.json dosyalarındadır.

## Claude Motion araştırması

Resmî belgeler 8 Ekim 2026 tarihli özelliği, kodla düzenlenebilir metin, grafik, şekil ve görüntü animasyonu
ile MP4 dışa aktarımı olarak tanımlar. Bağımsız üretimimiz bu düzenlenebilirlik ve tekrarlanabilir render
yaklaşımını kullanır. Zaman çizelgesi ve easing üretim tercihleridir.

https://support.claude.com/en/articles/17454997-get-started-with-claude-motion
https://claude.com/resources/articles/dashboards-and-motion

Kamera hareketinin düzenlenebilir Blender dosyası assets/microgravity_camera_animation.blend dosyasıdır.


## Olay anlatımı güncellemesi

animate_event.py, büyüyüp sönümlenen düzensiz hacimsel alev zarfı, iç sıcak bölge,
ısınan numune, kapatılan temsili ısı kaynağı ve hareketli aerosol kümeleri üretir.
37 ana kare 1280×720 render edilir, 24 FPS filmde ara görüntüler harmanlanır.
Açılışın ilk 30 saniyesi tam ekran olay anlatımıdır. Reklam ritminde kısa eylem mesajları
deney, model ve CLI sahnelerinin sonlarına yerleştirilmiştir.

Bunlar BASS'tan esinlenen temsili aşamalardır. Özgün BASS donanım geometrisi,
ölçülmüş olay süreleri, gerçek parçacık yörüngeleri veya deneyden yeniden üretilmiş
alev/sönüm dinamikleri iddia edilmez. Isı kaynağının kapanması yönetmenlik seçimidir,
Model A/B/C'nin kararı veya doğrulanmış bir söndürme işlemi değildir.
Alev ve duman hareketi görselleştirme içindir. Model çıktıları ayrı kayıtlarla gösterilir.

Mevcut modellerin fiziksel yangını önlediği veya sertifikalı koruma sağladığı gösterilmemiştir.
Film araştırma katkısını koşulları karşılaştırma, görüntüyü ölçüme dönüştürme ve
malzeme/sensör yanıtını inceleme üzerinden açıklar. Kamera ve olay geometrisi kaynakları
assets/microgravity_event.blend içinde düzenlenebilir.

 
## Son kurgu: QK norm / sıcak palet / 2018-2025-2026

İsim QK norm olarak korunur. Film 177 saniye ve 4248 karedir.
İlk 45 saniye 2018 DISCOVERED, 2025 PRIORITIZED, 2026 QK norm aşamalarını gösterir.
İlk 30 saniyedeki 3B olay arka planda kesintisiz ilerler; Model A ve final 3B bölümleri de korunur.
Temsili 3B sahnelere kömür, bej ve bakır tonlaması uygulanır. NASA/NIST kaynak görüntülerinin
renkleri bilimsel kanıt sunumunda korunur. İlk bölümde gerçek NIST numune fotoğrafı,
2025 bölümünde NASA basılı sayfa 251'in gerçek algılama ve sıralama kesitleri kullanılır.
10. sıra, 2025 belgesinde belirtilen Civil Space Shortfall ID 1520 bağlamındadır.
2026 aşaması çalışan yazılımın kaynaklı deney karşılaştırma katkısını açıklar.

7 sayfalık yoğun jüri PDF'i output/pdf/QK_norm_Juri_Sunumu_7_Sayfa.pdf dosyasıdır.
Üretim komutu: .venv/bin/python presentation/motion-film/make_jury_deck.py

 
## Yedi ana sayfalık video

Video 177 saniye içinde yedi ana sayfaya ayrılır. Sayfa numarası 01/07–07/07 olarak gösterilir.
Her sayfanın içindeki alt içerik animasyonla değişir; ana sayfa değişimi dışındaki kararmalar kaldırılmıştır.

1. 00:00–00:45 / Problem ve 2018–2025–2026 kronolojisi
2. 00:45–01:08 / BASS araştırma bağlamı ve Model A
3. 01:08–01:28 / Model B
4. 01:28–01:48 / Model C ve gerçek SAME sayımları
5. 01:48–02:22 / Kaynaklı analiz, WT4 rolü ve benchmarklar
6. 02:22–02:49 / Dashboard ve CLI
7. 02:49–02:57 / Araştırma katkısı ve kapanış

3B olay, kamera hareketleri, arşiv BASS görseli, kaynak kanıtları, modeller ve sonuçlar bu yedi
sayfaya dağıtılmıştır. Makine tarafından okunabilir zaman çizelgesi deliverables/video_chapters.json
dosyasındadır. contact_sheet.jpg yedi ana sayfayı, scene_*.jpg dosyaları ise PDF üreticisinin
beklediği ayrıntı karelerini sağlar.
