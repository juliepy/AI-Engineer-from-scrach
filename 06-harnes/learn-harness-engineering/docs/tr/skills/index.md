# Yetenekler

Bu dizin, kursla birlikte gelen yapay zeka ajan yeteneklerini içerir. Yetenekler, AI kod yazma ajanları (Claude Code, Codex, Cursor, Windsurf vb.) tarafından özelleşmiş görevleri yerine getirmek için yüklenebilen, kendi kendine yeten prompt şablonlarıdır.

## harness-creator

Yapay zeka kod yazma ajanları için üretim seviyesinde bir harness mühendisliği yeteneği. Beş temel harness alt sistemini oluşturmanıza, değerlendirmenize ve iyileştirmenize yardımcı olur: talimatlar, durum, doğrulama, kapsam ve oturum yaşam döngüsü.

### Ne işe yarar

- **Sıfırdan harness oluşturma** — AGENTS.md, özellik listeleri, doğrulama akışları
- **Var olan harness'ları geliştirme** — Beş alt sistem üzerinden öncelikli iyileştirme değerlendirmesi
- **Oturum sürekliliği tasarımı** — Bellek kalıcılığı, ilerleme takibi, devir prosedürleri
- **Üretim desenleri uygulama** — Bellek, bağlam mühendisliği, araç güvenliği, çoklu-ajan koordinasyonu

### Hızlı başlangıç

Yetenek dosyaları depoda şu adreste yer alır: [`skills/harness-creator/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/skills/harness-creator).

```bash
npx skills add walkinglabs/learn-harness-engineering --skill harness-creator
```

Claude Code ile kullanmak için `harness-creator/` dizinini projenizin yetenek yoluna kopyalayın ya da ajanınızı SKILL.md dosyasına yönlendirin.

### Referans desenleri

Yetenek, 7 odaklı referans belge içerir:

| Desen | Ne zaman kullanılır |
|---------|-------------|
| Bellek Kalıcılığı | Ajan oturumlar arasında unutuyor |
| Skill Runtime | Yeniden kullanılabilir iş akışlarını skill olarak paketleme |
| Bağlam Mühendisliği | Bağlam bütçesi yönetimi, JIT yükleme |
| Araç Kayıt Defteri | Araç güvenliği, eşzamanlılık kontrolü |
| Çoklu-Ajan Koordinasyonu | Paralellik, uzmanlaşma akışları |
| Yaşam Döngüsü ve Bootstrap | Kancalar, arka plan görevleri, başlatma |
| Tuzaklar | 15 görünmez başarısızlık modu ve çözümleri |

### Şablonlar

Yetenek, doğrudan kullanılabilen şablonlar içerir:

- `agents.md` — Çalışan kuralları içeren AGENTS.md iskeleti
- `feature-list.json` — JSON Schema + örnek özellik listesi
- `init.sh` — Standart başlatma betiği
- `progress.md` — Oturum ilerleme günlüğü şablonu
- `session-handoff.md` — Oturum devir şablonu

### Scriptler

Yetenek ayrıca scaffold, doğrulama, HTML değerlendirme raporu ve yapısal benchmark raporu için saf Node.js scriptleri içerir.

### Bu yetenek nasıl geliştirildi

`harness-creator`, **skill-creator** metodolojisi ile geliştirildi — Anthropic'in ajan yetenekleri oluşturmak, test etmek ve iyileştirmek için resmî meta yeteneği. skill-creator; yapılandırılmış bir akış (taslak → test → değerlendir → iyileştir) ile gömülü eval çalıştırıcıları, değerlendiriciler ve bir benchmark görüntüleyici sunar.

- **skill-creator kaynağı**: [anthropics/skills — skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- **Claude Code skills belgeleri**: [anthropics/claude-code — plugin-dev/skills](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev/skills)
