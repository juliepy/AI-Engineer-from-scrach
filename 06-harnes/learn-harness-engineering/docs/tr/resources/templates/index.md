# Şablon Rehberi

Bu şablonlar kendi projenize kopyalanmaya hazırdır. Her biri, ajanın iş akışında belirli bir amaca hizmet eder. İçerikleri projenizin komutlarına, yollarına, özellik adlarına ve doğrulama adımlarına uyacak şekilde düzenleyin.

## Nasıl Başlanır

Önce şu dört dosyayı projenizin kök dizinine kopyalayın:

1. `AGENTS.md` veya `CLAUDE.md`
2. `init.sh`
3. `claude-progress.md`
4. `feature_list.json`

Projeniz büyüdükçe geri kalan dosyaları ekleyin.

---

## AGENTS.md

Kök talimat dosyası. Ajan bir oturum başlattığında okuduğu ilk şey budur. Çalışma kurallarını tanımlar: kod yazmadan önce ne yapılmalı, nasıl çalışılmalı ve nasıl tamamlanmalı.

**Nasıl kullanılır:**

- Projenizin kök dizinine kopyalayın
- Başlatma iş akışı adımlarındaki yolları ve komutları kendi projenizinkilerle değiştirin
- Çalışma kurallarını ekibinizin alışkanlıklarına uyacak şekilde uyarlayın
- "Bitti tanımı" bölümünü mutlaka koruyun — en önemli kısım odur

**Ajan için ne işe yarar:**

- İşe başlamadan önce ilerleme ve özellik durumunu okumasını söyler
- Aynı anda yalnızca bir özellik üzerinde çalışmasını sağlar
- Herhangi bir şeyi tamamlandı olarak işaretlemeden önce kanıt ister
- Temiz bir oturum sonunun nasıl göründüğünü tanımlar

Codex veya diğer ajanlar için `AGENTS.md` kullanın. Claude Code ile çalışıyorsanız `CLAUDE.md` kullanın — yapı aynıdır, sadece Claude'un talimat stiline göre biçimlendirilmiştir.

## init.sh

Başlangıç betiği. Bağımlılık kurulumunu, doğrulamayı çalıştırır ve başlatma komutunu yazdırır — hepsi tek seferde.

**Nasıl kullanılır:**

- Projenizin köküne kopyalayın
- Üstteki şu üç değişkeni düzenleyin:
  - `INSTALL_CMD` — bağımlılık kurulum komutunuz (örn. `npm install`, `pip install -r requirements.txt`)
  - `VERIFY_CMD` — temel doğrulama komutunuz (örn. `npm test`, `pytest`)
  - `START_CMD` — geliştirme sunucusu başlatma komutunuz (örn. `npm run dev`)
- Çalıştırılabilir hale getirin: `chmod +x init.sh`

**Ne yapar:**

1. Geçerli dizini yazdırır (doğru yerde çalıştığından emin olabilesiniz diye)
2. Bağımlılıkları kurar
3. Doğrulama komutunu çalıştırır
4. Başlatma komutunu yazdırır (veya `RUN_START_COMMAND=1` ayarlıysa çalıştırır)

Doğrulama başarısız olursa, ajan başka herhangi bir şey yapmadan önce durmalı ve temel başlangıç durumunu düzeltmelidir.

## claude-progress.md

İlerleme günlüğü. Her oturum bu dosyaya yazar ve her yeni oturum önce onu okur.

**Nasıl kullanılır:**

- Projenizin köküne kopyalayın
- "Mevcut Doğrulanmış Durum" bölümünü projenizin bilgileriyle doldurun
- Her oturumdan sonra oturum kaydını güncelleyin

**Her alanın anlamı:**

- **Mevcut Doğrulanmış Durum** — projenin nerede olduğunun tek doğru kaynağı
  - `Repository root directory` — projenin bulunduğu yer
  - `Standard startup path` — projeyi çalıştırmak için kullanılan komut
  - `Standard verification path` — testleri çalıştıran komut
  - `Highest priority unfinished feature` — sıradaki oturumun üzerinde çalışacağı şey
  - `Current blocker` — engellenen herhangi bir şey
- **Oturum Kaydı** — her oturum için bir giriş
  - `Goal` — yapmayı planladığınız şey
  - `Completed` — gerçekten yapılan şey
  - `Verification run` — hangi testlerin çalıştırıldığı
  - `Evidence recorded` — hangi kanıtın yakalandığı
  - `Commits` — neyin commit edildiği
  - `Known risks` — bozulmuş olabilecek şeyler
  - `Next best action` — sıradaki oturumun nereden başlaması gerektiği

## feature_list.json

Özellik takipçisi. Ajanın uygulaması gereken her özelliğin, durumunun, doğrulama adımlarının ve kanıtlarının makine tarafından okunabilir bir listesi.

**Nasıl kullanılır:**

- Projenizin köküne kopyalayın
- Örnek özellikleri kendi özelliklerinizle değiştirin
- Her özelliğin şunlara ihtiyacı vardır:
  - `id` — kısa ve benzersiz bir tanımlayıcı
  - `priority` — tam sayı; daha düşük = daha yüksek öncelik
  - `area` — uygulamanın hangi kısmı (örn. "chat", "import", "search")
  - `title` — kısa açıklama
  - `user_visible_behavior` — çalıştığında kullanıcının görmesi gereken şey
  - `status` — `not_started`, `in_progress`, `blocked`, `passing` değerlerinden biri
  - `verification` — çalıştığını doğrulamak için adım adım talimatlar
  - `evidence` — doğrulamanın geçtiğine dair kaydedilmiş kanıt (ajan tarafından doldurulur)
  - `notes` — ek bağlam

**Durum kuralları:**

- `not_started` — henüz dokunulmamış
- `in_progress` — şu anda üzerinde çalışılan tek özellik (aynı anda yalnızca biri)
- `blocked` — belgelenmiş bir sorun nedeniyle ilerleyemiyor
- `passing` — doğrulama geçti ve kanıt kaydedildi

Ajanın aynı anda yalnızca tek bir özelliği `in_progress` durumunda tutması gerekir.

## session-handoff.md

Oturumlar arasında derli toplu bir devir notu. Bir oturum sona erdiğinde ve bir sonraki oturumun hızlıca devam almasını istediğinizde bunu kullanın.

**Nasıl kullanılır:**

- Projenizin köküne kopyalayın
- Her oturumun sonunda doldurun (veya ajana doldurtun)

**Her bölümün kapsadığı şey:**

- **Şu anda doğrulanan** — neyin çalıştığı doğrulandı ve hangi doğrulamanın çalıştırıldığı
- **Bu oturumdaki değişiklikler** — hangi kod veya altyapının değiştiği
- **Hâlâ bozuk veya doğrulanmamış** — bilinen sorunlar ve riskli alanlar
- **Sıradaki en iyi adım** — sıradaki oturumun ne yapması gerektiği ve neye dokunmaması gerektiği
- **Komutlar** — hızlı başvuru için başlatma, doğrulama ve hata ayıklama komutları

Bu dosya küçük oturumlar için isteğe bağlıdır. Oturumlar uzun olduğunda veya projenin birden fazla aktif alanı olduğunda önem kazanır.

## clean-state-checklist.md

Her oturumu bitirmeden önce gözden geçirilecek bir kontrol listesi. Deponun, sıradaki oturumun temiz bir şekilde başlayabileceği iyi bir durumda olduğundan emin olun.

**Nasıl kullanılır:**

- Projenizin köküne kopyalayın
- Bir oturumu kapatmadan önce listeyi gözden geçirin
- Ajan da oturum sonu rutininin bir parçası olarak bu maddeleri kontrol etmelidir

**Neleri kontrol eder:**

- Standart başlatma hâlâ çalışıyor mu
- Standart doğrulama hâlâ çalışıyor mu
- İlerleme günlüğü güncel mi
- Özellik listesi gerçek durumu yansıtıyor mu (yanlış `passing` girişleri yok)
- Kayıtsız bırakılmış yarım iş yok
- Sıradaki oturum manuel düzeltmeler olmadan devam edebilir mi

## evaluator-rubric.md

Ajan çıktısının kalitesini değerlendirmek için bir karne. Bir oturumdan sonra veya proje kilometre taşlarında, işin standardı karşılayıp karşılamadığını değerlendirmek için kullanın.

**Nasıl kullanılır:**

- Projenizin köküne kopyalayın
- Bir oturumdan (veya bir dizi oturumdan) sonra, ajanın işini altı boyutta puanlayın
- Her boyut 0-2 arasında puanlanır

**Altı boyut:**

1. **Doğruluk** — uygulama hedeflenen davranışla eşleşiyor mu?
2. **Doğrulama** — gerekli kontroller gerçekten kanıtla birlikte çalıştırıldı mı?
3. **Kapsam disiplini** — ajan seçilen özelliğin sınırları içinde kaldı mı?
4. **Güvenilirlik** — sonuç bir yeniden başlatma veya yeniden çalıştırmadan sonra ayakta kalıyor mu?
5. **Sürdürülebilirlik** — kod ve dokümantasyon sıradaki oturum için yeterince açık mı?
6. **Devir hazırlığı** — yeni bir oturum yalnızca depo dosyalarını kullanarak devam edebilir mi?

**Sonuç seçenekleri:**

- Kabul — standardı karşılıyor
- Revize — kabul edilmeden önce düzeltmeler gerektiriyor
- Engelle — önce çözülmesi gereken temel sorunlar var

**Önemli: değerlendiricinin ayarlanması gerekir.** Hazır halleriyle ajanlar zayıf öz-değerlendiricilerdir — sorunları tespit edip sonra kendilerini onaylamaya ikna ederler. Yinelemeniz gerekir:

1. Tamamlanmış bir sprint üzerinde değerlendiriciyi çalıştırın.
2. Puanlarını kendi insan yargınızla karşılaştırın.
3. Ayrıştıkları yerlerde, rubriği geçme/kalma kriterleri konusunda daha spesifik hale getirin.
4. Yeniden çalıştırın ve uyumu kontrol edin.
5. Değerlendirici, insan incelemesiyle tutarlı olarak eşleşene kadar tekrarlayın.

3-5 ayar turu için plan yapın. Hangi değişikliğin uyumu iyileştirdiğini takip edebilmek için her değişikliği kaydedin.

## quality-document.md

Projenizdeki her ürün alanına ve mimari katmana not veren bir kalite anlık görüntüsü. Yalnızca tek tek oturum çıktısını değil, kod tabanının zaman içindeki sağlığını izler.

**Nasıl kullanılır:**

- Projenizin köküne kopyalayın
- Bir oturuma başlamadan önce: kod tabanının nerede en zayıf olduğunu anlamak için okuyun
- Bir oturumdan sonra: değişikliklere göre notları güncelleyin
- Zamanla: hangi harness değişikliklerinin kod tabanı sağlığını gerçekten iyileştirdiğini görmek için anlık görüntüleri karşılaştırın

**Neyi puanlar:**

- **Ürün alanları** (örn. belge içe aktarma, Soru-Cevap akışı, dizinleme): her alan; doğrulama durumu, ajan okunabilirliği, test kararlılığı ve ana boşluklar açısından bir not (A-D) alır
- **Mimari katmanlar** (örn. main process, preload, renderer, services): her katman, sınır uygulaması ve ajan okunabilirliği için bir not alır

**Neden önemlidir:**

Değerlendirici rubriği tek tek ajan çıktılarını puanlar. Kalite belgesi ise kod tabanının kendisini puanlar. Farklı soruları yanıtlarlar:

- Değerlendirici rubriği: "Ajan bu oturumda iyi iş çıkardı mı?"
- Kalite belgesi: "Proje zamanla güçleniyor mu yoksa zayıflıyor mu?"

**Ne zaman güncellenmeli:**

- Her önemli oturumdan sonra
- Karşılaştırma (benchmark) öncesi
- Temizlik veya sadeleştirme turlarından sonra
- Projeye yeni bir ajan veya model dahil edilirken

**Harness sadeleştirme ile bağlantı:**

Kalite belgesi aynı zamanda harness sadeleştirmeyi de destekler. Her harness bileşeni, modelin yapamadığı bir şeye dair bir varsayımı kodlar. Modeller geliştikçe bu varsayımlar eskir. Bir bileşenin hâlâ gerekli olup olmadığını kontrol etmek için:

1. Bir kalite belgesi anlık görüntüsü alın.
2. Bir harness bileşenini kaldırın.
3. Karşılaştırma görev paketini çalıştırın.
4. Başka bir anlık görüntü alın.
5. Karşılaştırın — notlar düşmediyse bileşen fazladandı. Düştüyse geri getirin.
