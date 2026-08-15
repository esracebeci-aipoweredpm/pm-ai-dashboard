# AI x PM Haftalık Bülten — Çalışma Talimatı

Bu proje, Esra'nın haftalık "AI x PM" dashboard'unu yarı otomatik üretmek için kurulmuştur.
Esra bir kaynak linki verip hangi haftaya ekleneceğini söyler; bu talimatları izleyerek
kaynağı analiz et, `data.json`'a kart olarak ekle, gerekiyorsa detay sayfası oluştur ve
dashboard'u yeniden üret.

## Klasör yapısı

```
pm-ai-dashboard/
├── CLAUDE.md                     ← bu dosya
├── assets/
│   ├── style.css                 ← tüm index + detay sayfalarının ortak teması (değiştirme)
│   └── script.js                 ← sekme geçiş mantığı (değiştirme)
├── templates/
│   ├── index-template.html.j2    ← index.html'in Jinja2 şablonu
│   └── detail-template.html      ← yeni detay sayfası için başlangıç iskeleti
├── scripts/
│   └── build.py                  ← data.json'dan index.html üretir
└── weeks/
    ├── 2026-08-01_2026-08-07/
    │   ├── data.json             ← haftanın tüm kart verisi (tek doğruluk kaynağı)
    │   ├── index.html            ← build.py tarafından otomatik üretilir, elle düzenlenmez
    │   └── detaylar/
    │       └── <slug>.html       ← her "Detaylı analiz" kartı için ayrı sayfa
    ├── 2026-08-08_2026-08-14/
    │   └── ...
    └── ...
```

Her hafta klasör adı `YYYY-MM-DD_YYYY-MM-DD` formatındadır (haftanın ilk ve son günü).

## Yeni bir kaynak eklerken izlenecek adımlar

1. **Kaynağı oku/analiz et.** Verilen linki incele, ana argümanı ve PM açısından önemini çıkar.

2. **Skor belirle (1-5, "PM × AI ilişki" skoru):**
   - **5** — doğrudan PM yöntemi/sistemi (ör. bir PM workflow'unu doğrudan değiştirecek pratik).
   - **4** — PM araç kutusu/yatırım sinyali (ör. bir aracın yeni özelliği, vendor stratejisine girdi).
   - **3** — sektörel sinyal/takip değeri var ama doğrudan aksiyon gerektirmiyor.
   - **1-2** — PM-AI ilişkisi zayıf. **Bu skordaki kaynaklar dashboard'a eklenmez.**

3. **Detay sayfası gerekip gerekmediğine karar ver:**
   - Skor **5** → her zaman detay sayfası oluştur.
   - Skor **4** → genellikle detay sayfası oluştur (istisna: tekrarlayan/rutin duyurular).
   - Skor **3** → detay sayfası oluşturma, sadece kart özeti yeterli (Esra özellikle isterse oluştur).

4. **`weeks/<hafta>/data.json` dosyasını güncelle** — ilgili kanalın `cards` dizisine yeni bir
   obje ekle. Sabit bir kanal listesi yoktur; kanal `id`/`name`'i kaynağın gerçek platformuna
   bakılarak dinamik belirlenir:
   - `youtube.com` / `youtu.be` → `id: youtube`, `name: "YouTube"`
   - `*.substack.com` veya `substack.com/...` → `id: substack`, `name: "Substack"`
   - `twitter.com` / `x.com` → `id: twitter`, `name: "X (Twitter)"`
   - `linkedin.com` → `id: linkedin`, `name: "LinkedIn"`
   - Bunların dışında kalan haber sitesi/blog/makale → `id: haber`, `name: "Haber & Makale"`
     (ya da o hafta o kanaldaki kaynaklar tek bir platformda yoğunlaşıyorsa, ismi o platforma
     göre daha spesifik seç — ör. tüm kaynaklar Substack ise kanalı "Newsletter & Substack"
     gibi genel bir şemsiye yerine doğrudan "Substack" olarak adlandır).

   Bir kanal, ilk kaynağı eklendiğinde var olur: o hafta için `channels` dizisinde ilgili kanal
   henüz yoksa, yukarıdaki kurala göre `id`/`name` ile yeni bir kanal objesi oluşturup `cards`
   dizisine kartı ekle. Var olan bir kanalın altındaki kaynaklar zamanla tek bir platforma
   daraldıysa (ör. "Newsletter & Substack" altında yalnızca Substack kaynakları birikmişse),
   kanalın `id`/`name`'ini kaynaklarla tutarlı hale getirecek şekilde yeniden adlandır. Kaynağı
   olmayan (boş `cards: []`) kanallar dashboard'da hiç gösterilmez — bir hafta yalnızca o hafta
   gerçekten kaynak gelen kanalları içermeli, henüz kaynak gelmemiş kanalları boş obje olarak
   önceden eklemeye gerek yok. Şema:

   ```json
   {
     "source": "Kaynak adı (ör. Lenny's Podcast)",
     "date": "05.08.2026",
     "score": 5,
     "title": "İçerik başlığı",
     "url": "https://...",
     "url_label": "isteğe bağlı — boş bırakılırsa https:// ve www. otomatik silinir",
     "summary": "1-2 cümlelik özet; PM açısından önemini belirt (Sahibinden'e özgü atıf yapılmaz, genel PM bağlamında kalınır).",
     "tags": [
       { "label": "Strateji", "color": "amber" },
       { "label": "Kültür", "color": "blue" }
     ],
     "has_detail": true,
     "detail_slug": "kaynak-konu-kisa-slug",
     "no_detail_note": null
   }
   ```

   - `tags[].color` seçenekleri: `blue`, `green`, `red`, `amber` veya boş bırak (nötr gri).
   - `has_detail: false` ise `detail_slug` yerine `no_detail_note` doldurulur
     (ör. `"araç tanıtımı"`, `"webinar"`, `"meta-derleme"`) — bu not kartta italik gösterilir.
   - `detail_slug`: kebab-case, kısa, konuyu anlatan bir isim (ör. `lenny-eric-ries-incorruptible`).

5. **Detay sayfası gerekiyorsa** `templates/detail-template.html` dosyasını
   `weeks/<hafta>/detaylar/<detail_slug>.html` olarak kopyala ve doldur:
   - **İçerik Özeti** sekmesi: temel argüman + 1-2 destek kartı + "PM için asıl çıkarım".
   - **Anahtar Noktalar** sekmesi: 3-5 adet Neden/Sonuç bloğu (`ce-block`), her biri genel bir PM
     çıkarımına bağlanmalı (Sahibinden'e özgü atıf yapılmaz).
   - **Kullanım Senaryoları** sekmesi: 3-4 somut, uygulanabilir senaryo (`.card` başına bir
     senaryo), genel PM ekipleri için yazılır — Sahibinden'e özgü atıf yapılmaz.
   - Sayfa başlığı (`<title>`), `eyebrow`, `h1` ve `meta` alanlarını kaynağa göre doldur.

6. **Haftanın temasına eklenmesi gerekiyorsa** `data.json > themes` dizisine kısa bir madde ekle
   (Genel Bakış sekmesindeki "Bu haftanın baskın temaları" kartını besler). Her madde
   `"<strong>Başlık.</strong> açıklama"` formatında bir string olmalı.

7. **Dashboard'u yeniden üret:**
   ```
   python3 scripts/build.py weeks/<hafta-klasörü>
   ```
   Bu komut `index.html`'i `data.json`'dan yeniden oluşturur. `index.html` elle düzenlenmez —
   her değişiklik `data.json` üzerinden yapılır, sonra script çalıştırılır.

8. **Arşiv (ana) sayfasını güncelle:**
   ```
   python3 scripts/build_archive.py
   ```
   Proje kökündeki `index.html` — tüm haftaları listeleyen arşiv/ana sayfa — bu script ile
   `weeks/` altındaki her `data.json`'dan otomatik üretilir. Bir haftanın `data.json`'u her
   değiştiğinde (yeni kaynak eklendiğinde, tema güncellendiğinde) veya yeni bir hafta
   başlatıldığında bu adım da çalıştırılmalı; aksi halde arşiv sayfası güncel görünmez.
   Bu dosya da elle düzenlenmez.

## Yeni bir hafta başlatma

```
mkdir -p weeks/2026-08-08_2026-08-14/detaylar
```
`weeks/2026-08-01_2026-08-07/data.json` dosyasını kopyalayıp `themes` alanını boşalt,
`channels` dizisini tamamen boşalt (`"channels": []`), `week_label`, `date_range_title`,
`date_range_pill` alanlarını güncelle. Yeni haftaya ilk kaynak eklendiğinde o kaynağın kanalı
`channels` dizisine eklenir (bkz. "Yeni bir kaynak eklerken izlenecek adımlar" adım 4) — hafta
henüz kaynaksız kanalları önceden içermez. Yeni haftanın `index.html`'i üretildikten sonra
`python3 scripts/build_archive.py` ile arşiv sayfası da güncellenmeli ki yeni hafta orada
görünsün.

## Genel kurallar

- `assets/style.css` ve `assets/script.js` tüm haftalar arasında paylaşılır, hafta bazlı
  kopyalanmaz.
- Detay sayfalarında **bölüm başlıkları / zaman damgaları listesi** (video chapters, "0:00
  Giriş · 1:31 ..." gibi) asla yer almaz. İçerik Özeti doğrudan Temel Argüman, destek
  kartları ve "PM için asıl çıkarım" ile devam eder.
- Skor ≥3 olmayan kaynaklar dashboard'a hiç eklenmez (geçmiş haftalardaki "skor ≥3 filtreli"
  mantığı korunur, sadece arayüzde artık ayrıca belirtilmiyor).
- Kaynak doğrulanamıyorsa (örn. yayın tarihi/yazar teyit edilemiyorsa) kart eklenmez; Esra'ya
  durum bildirilir.
- Dashboard içeriğinde (kart özetleri, detay sayfaları) Sahibinden'e özgü atıf, örnek veya
  tavsiye yer almaz; tüm değerlendirmeler genel PM süreçleri perspektifinden yazılır.
- Teknik jargon Türkçeleştirilmez, orijinal İngilizce haliyle kullanılır (ör. "artefakt" değil
  "artifact", "orkestrasyon" değil "orchestration", "yönetişim" değil "governance"). Türkçe
  ek gerektiğinde kesme işaretiyle bağlanır (ör. "artifact'lar", "governance'ı").
