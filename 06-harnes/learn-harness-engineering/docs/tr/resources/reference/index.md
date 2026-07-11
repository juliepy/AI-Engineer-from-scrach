# Türkçe Referans

Bu notlar, şablonları gevşek bir dosya yığını olarak değil, çalışan bir harness
olarak nasıl kullanacağınızı açıklar.

## İç Referans Notları

- [`method-map.md`](./method-map.md): yaygın uzun süreli hata modlarını önce
  hangi dosyanın veya politikanın çözdüğüne haritalayın
- [`initializer-agent-playbook.md`](./initializer-agent-playbook.md): başlatıcı
  ajanın özellik işine başlamadan önce geride bırakması gerekenler
- [`coding-agent-startup-flow.md`](./coding-agent-startup-flow.md): daha sonraki
  kod yazma turları için sabit oturum başlatma akışı
- [`prompt-calibration.md`](./prompt-calibration.md): kök talimatları, şişkin
  ve kırılgan hale getirmeden nasıl keskin tutacağınız

## Birincil Makaleler

Bu liste bilinçli olarak dardır. Harness, modelin etrafındaki yürütme sistemi
anlamına gelir: ajan döngüsü, araç yürütme, sandbox, durum, bağlam, doğrulama,
sonlandırma, orkestrasyon ve gözlemlenebilirlik. Genel prompt mühendisliği
veya geniş ajan çerçevesi makaleleri birincil listeye ait değildir.

Orijinal üç makale kursun belkemiği olmaya devam etmektedir:

- [OpenAI: Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (2026-02-11): ajan öncelikli depolar, depo yerel bağlam, özel linting ve yapısal korkuluklar.
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (2025-11-26): başlatıcı ajan, kod yazma ajanı, özellik listesi, ilerleme günlüğü ve bağlam pencereleri arasında devir.
- [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24): planlayıcı / üretici / değerlendirici rolleri, bağlam sıfırlamaları, harness sadeleştirme ve eskimiş varsayımlar.

Yalnızca birkaç son derece alakalı 2026 makalesi eklenmiştir:

- [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/) (2026-01-23): Codex runtime harness'ı, araç çağrıları, bağlam büyümesi ve döngü sonlandırma.
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (2026-01-09): modeli ve harness'ı birlikte değerlendirmek ve değerlendirme harness'larını ajan harness'larından ayırmak.
- [LangChain: Improving Deep Agents with harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) (2026-02-17): modeli sabit tutarken bir kod yazma ajanını Terminal Bench 2.0'da İlk 30'dan İlk 5'e taşımak için sistem promptlarını, araçları, ara katmanları, izlemeyi ve öz-doğrulamayı iyileştirme.
- [Thoughtworks / Martin Fowler: Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html) (2026-04-02): deterministik ve çıkarımsal kontrollerle ileri besleme kılavuzları ve geri bildirim sensörleri olarak kod yazma ajanı kullanıcı harness'ları.
- [Cursor: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness) (2026-04-30): harness'ı çevrimdışı değerlendirmeler, çevrimiçi metrikler, araç hatası taksonomisi, modele özgü ayarlama ve sohbet ortası model değişimi ile sürekli iyileştirilen bir ürün sistemi olarak ele almak.

## 2026 Genişletilmiş Referanslar

Bunlar temel kurs kaynakları değildir, ancak belirli harness modüllerini
tasarlarken faydalıdır. Bu bölüm yalnızca, içeriği doğrudan ajan döngüsü,
araç yürütme, bağlam yönetimi, doğrulama, sandbox, kontrol katmanları veya
regresyon yönetişimini kapsayan kaynakları tutar. Saf ajan ürünleri,
platform duyuruları, ekip vaka çalışmaları ve karşılaştırma testleri hariçtir.

- [OpenAI: Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/) (2026-02-04): iş parçacığı yaşam döngüsü, devam, çatallama, diff'ler ve istemci entegrasyonları içeren yeniden kullanılabilir bir App Server protokolü olarak harness.
- [OpenAI Developers: Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex) (2026-02-23): uzun süreli görevler için kalıcı proje hafızası, kilometre taşı doğrulaması ve "ne zaman bitti" örnekleri.
- [OpenAI: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/) (2026-04-15): model-yerel harness'lar, sandbox yürütme ve dosya/komut yürütme.
- [OpenAI: An open-source spec for Codex orchestration: Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/) (2026-04-27): bir konu takipçisini veya Linear panosunu çok ajanlı bir kontrol düzlemine dönüştürmek.
- [Anthropic: Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) (2026-02-05): paralel ajan ekipleri, görev kilitleri, git senkronizasyonu, konteyner yalıtımı ve otonom döngüler.
- [Anthropic: Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) (2026-04-08): oturum, harness ve sandbox'ı değiştirilebilir arayüzler olarak ayıran meta-harness görünümü.
- [Anthropic: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem) (2026-04-23): regresyon yönetişimi gerektiren harness değişiklikleri olarak akıl yürütme çabası, bağlam budama ve sistem promptları.
- [LangChain: Context Management for Deep Agents](https://www.langchain.com/blog/context-management-for-deepagents) (2026-01-28): bağlam yönetimi harness'ları için dosya sistemi aktarımı, araç çağrısı kısaltma, özetleme ve hedefli değerlendirmeler.
- [LangChain: Tuning Deep Agents to Work Well with Different Models](https://www.langchain.com/blog/tuning-deep-agents-different-models) (2026-04-29): promptlar, araç adları, ara katmanlar ve alt-ajan yapılandırması için modele özgü harness profilleri.
- [LangChain: Continual learning for AI agents](https://www.langchain.com/blog/continual-learning-for-ai-agents) (2026-04-05): izlemelerle beslenen ajan iyileştirmesini model, harness ve bağlam katmanlarına ayırmak.
- [Microsoft: Agent Harness in Agent Framework](https://devblogs.microsoft.com/agent-framework/agent-harness-in-agent-framework/) (2026-03-12): shell/dosya sistemi harness'ları, onay akışı, barındırılan shell yürütme ve bağlam yoğunlaştırma.
- [Google: Announcing ADK for Java 1.0.0](https://developers.googleblog.com/announcing-adk-for-java-100-building-the-future-of-ai-agents-in-java/) (2026-03-30): yeniden kullanılabilir harness ilkelleri olarak eklentiler, olay yoğunlaştırma, HITL, oturum/hafıza hizmetleri ve A2A.
- [GitHub: Automate repository tasks with GitHub Agentic Workflows](https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/) (2026-02-13): güvenli çıktılar, sandbox, izinler ve inceleme ile ajan iş akışı çalıştırıcısı olarak GitHub Actions.
- [AWS: AI agents in enterprises: Best practices with Amazon Bedrock AgentCore](https://aws.amazon.com/blogs/machine-learning/ai-agents-in-enterprises-best-practices-with-amazon-bedrock-agentcore/) (2026-02-03): Runtime, Memory, Gateway, Identity/Policy, Observability ve Evaluations boyunca kurumsal harness katmanları.
- [Stripe: Minions: Stripe's one-shot, end-to-end coding agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents) (2026-02-09) ve [Part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2) (2026-02-19): devbox yalıtımı, özel ajan harness'ları, blueprint durum makineleri, kural dosyaları, MCP araç küratörlüğü, güvenlik kontrolleri ve pre-push/CI geri bildirim döngüleri.
- [Cognition: What We Learned Building Cloud Agents](https://cognition.ai/blog/what-we-learned-building-cloud-agents) (2026-04-23): bulut-ajan runtime'ları için VM yalıtımı, oturum anlık görüntüsü/devam, orkestrasyon, yönetişim, denetim günlüğü ve entegrasyonlar.
- [Cognition: Multi-Agents: What's Actually Working](https://cognition.ai/blog/multi-agents-working) (2026-04-22): üretici-doğrulayıcı döngüleri, temiz bağlamlı inceleyiciler, akıllı arkadaş yönlendirmesi, yönetici-alt koordinasyonu ve ajanlar arası iletişim sınırları.
- [Replit: Decision-Time Guidance: Keeping Replit Agent Reliable](https://blog.replit.com/decision-time-guidance) (2026-01-20, güncelleme 2026-01-23): tüm kuralları sistem promptuna doldurmak yerine, karar noktasında kısa durumsal rehberlik enjekte eden hafif bir sınıflandırıcı.
- [Vercel: How we made v0 an effective coding agent](https://vercel.com/blog/how-we-made-v0-an-effective-coding-agent) (2026-01-07): dinamik sistem promptları, akıcı bir yeniden yazma katmanı ve deterministik/model güdümlü otomatik düzelticiler.
- [Vercel: Introducing deepsec](https://vercel.com/blog/introducing-deepsec-find-and-fix-vulnerabilities-in-your-code-base) (2026-05-04): tarama, soruşturma, yeniden doğrulama, zenginleştirme, dışa aktarma, eklenti ve reddetme denetleyici adımları içeren güvenlik odaklı bir kod yazma ajanı harness'ı.
- [Sourcegraph: CodeScaleBench](https://sourcegraph.com/blog/codescalebench-testing-coding-agents-on-large-codebases-and-multi-repo-software-engineering-tasks) (2026-03-03): MCP araç benimsemesi, araç kullanım transkriptleri, kıyaslama QA, doğrulayıcı/yeniden üretilebilirlik kapıları ve prompt/önsöz yinelemesi içeren bir değerlendirme/araçlar harness referansı.

Yalnızca 2025'e ait genel referanslar birincil listeden çıkarılmıştır.
Orijinal 2025 Anthropic harness makalesi, kursun temel kaynağı olduğu için
kalmıştır.

## Önerilen Okuma Sırası

1. `method-map.md`
2. `initializer-agent-playbook.md`
3. `coding-agent-startup-flow.md`
4. `prompt-calibration.md`
5. OpenAI Harness engineering
6. Anthropic Effective harnesses
7. Anthropic Harness design for long-running application development
8. OpenAI Codex agent loop
9. Anthropic agent evals
10. LangChain Improving Deep Agents
11. Thoughtworks / Martin Fowler Harness engineering for coding agent users
12. Cursor Continually improving our agent harness
