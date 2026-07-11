<p align="center">
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/English-d9d9d9"></a>
  <a href="README-CN.md"><img alt="简体中文" src="https://img.shields.io/badge/简体中文-d9d9d9"></a>
  <a href="README-ZH-TW.md"><img alt="繁體中文" src="https://img.shields.io/badge/繁體中文-d9d9d9"></a>
  <a href="README-JA.md"><img alt="日本語" src="https://img.shields.io/badge/日本語-d9d9d9"></a>
  <a href="README-ES.md"><img alt="Español" src="https://img.shields.io/badge/Español-d9d9d9"></a>
  <a href="README-FR.md"><img alt="Français" src="https://img.shields.io/badge/Français-d9d9d9"></a>
  <a href="README-KO.md"><img alt="한국어" src="https://img.shields.io/badge/한국어-d9d9d9"></a>
  <a href="README-AR.md"><img alt="العربية" src="https://img.shields.io/badge/العربية-d9d9d9"></a>
  <a href="README-VI.md"><img alt="Tiếng_Việt" src="https://img.shields.io/badge/Tiếng_Việt-d9d9d9"></a>
  <a href="README-DE.md"><img alt="Deutsch" src="https://img.shields.io/badge/Deutsch-d9d9d9"></a>
  <a href="README-TR.md"><img alt="Türkçe" src="https://img.shields.io/badge/Türkçe-d9d9d9"></a>
</p>

# Skill'ler

Bu dizin, Learn Harness Engineering projesi için yeniden kullanılabilir yapay zeka ajan skill'leri içermektedir. Her skill, Claude Code, Codex, Cursor, Windsurf gibi yapay zeka kodlama ajanları tarafından yüklenebilen bağımsız bir prompt şablonudur.

## Mevcut Skill'ler

### harness-creator

Yapay zeka kodlama ajanları için üretim düzeyinde harness mühendisliği skill'i. Ajan harness dosyaları (AGENTS.md, özellik listeleri, doğrulama iş akışları, oturum sürekliliği mekanizmaları) oluşturma, değerlendirme ve iyileştirme konularında yardımcı olur.

- **7 referans pattern**: Memory Persistence, Skill Runtime, Context Engineering, Tool Registry, Multi-Agent Coordination, Lifecycle & Bootstrap, Gotchas
- **Şablonlar**: AGENTS.md/CLAUDE.md, feature-list.json, init.sh, progress.md, session-handoff.md
- **Script'ler**: scaffold, doğrulama, HTML değerlendirme ve yapısal benchmark
- **10 yerleşik eval test senaryosu**

Tam belgeleme için [harness-creator/README.md](harness-creator/README.md) dosyasına bakın.

## harness-creator Nasıl Oluşturuldu

`harness-creator` skill'i, Anthropic'in ajan skill'leri oluşturmak, test etmek ve üzerinde yineleme yapmak için resmi meta-skill'i olan **skill-creator** metodolojisi kullanılarak geliştirilmiştir. skill-creator, yerleşik eval runner'lar, grader'lar ve bir benchmark görüntüleyicisi ile birlikte yapılandırılmış bir iş akışı (taslak → test → değerlendirme → yineleme) sağlar.

- **skill-creator kaynağı**: [anthropics/skills — skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- **Anthropic Claude Code skills belgeleri**: [anthropics/claude-code — plugin-dev/skills](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev/skills)

## Dizin Yapısı

```
skills/
├── README.md                    # Bu dosya (İngilizce)
├── README-CN.md                 # Basitleştirilmiş Çince
├── README-ZH-TW.md              # Geleneksel Çince
├── README-JA.md                 # Japonca
├── README-ES.md                 # İspanyolca
├── README-FR.md                 # Fransızca
├── README-AR.md                 # Arapça
├── README-VI.md                 # Vietnamca
├── README-DE.md                 # Almanca
├── README-TR.md                 # Türkçe
└── harness-creator/             # Harness mühendisliği skill'i
    ├── SKILL.md                 # Ana skill tanımı
    ├── SKILL.md.en              # Yalnızca İngilizce sürüm
    ├── README.md                # Ayrıntılı belgeleme
    ├── metadata.json            # Skill meta verisi ve tetikleyiciler
    ├── agents/                  # Skill UI meta verisi
    ├── scripts/                 # Scaffold, doğrulama ve benchmark yardımcıları
    ├── evals/                   # Test senaryoları
    ├── templates/               # Scaffold şablonları
    └── references/              # Derinlemesine pattern belgeleri
```

## Skill'ler Nasıl Çalışır

Her skill standart bir yapıyı izler:

1. **SKILL.md** — Giriş noktası. YAML ön madde (ad, tetikleme için açıklama) ve ajan için Markdown talimatları içerir.
2. **references/** — Gerektiğinde bağlama yüklenen ek belgeler.
3. **templates/** — Skill'in kullanıcılar için oluşturabileceği başlangıç şablonları.

Skill'ler aşamalı açıklama kullanır: ajan önce yalnızca adı ve açıklamayı görür, tetiklendiğinde tam SKILL.md gövdesini yükler ve paketlenmiş kaynakları yalnızca gerektiğinde okur.

## Güvenlik Denetimi

Bu dizindeki tüm dosyalar güvenlik açısından denetlenmiştir:

- Arka kapı, gizli URL veya kodlanmış payload yok
- Veri sızdırma veya sabit kodlanmış kimlik bilgisi yok
- Komut enjeksiyonu güvenlik açığı yok
- Script'ler yalnızca Node.js yerleşik modüllerini kullanır
- Oluşturulan `init.sh`, tespit edilen proje doğrulama komutlarını çalıştırır

## Lisans

MIT
