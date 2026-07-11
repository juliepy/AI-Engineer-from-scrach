# Inglizcha maʼlumotnomalar (English Reference)

Ushbu qaydlar andozalardan shunchaki tarqoq fayllar toʻplami emas, balki toʻliq ishlaydigan harness sifatida qanday foydalanish kerakligini tushuntiradi.

## Ichki maʼlumotnoma qaydlari (Internal Reference Notes)

- [`method-map.md`](./method-map.md): koʻp uchraydigan uzoq davom etadigan muvaffaqiyatsizlik rejimlari (failure modes) ni birinchi boʻlib hal qiladigan artefakt yoki siyosat bilan bogʻlaydi.
- [`initializer-agent-playbook.md`](./initializer-agent-playbook.md): inisializatsiya agenti funksiya (feature) ishini boshlashdan oldin nimalarni yozib qoldirishi kerak.
- [`coding-agent-startup-flow.md`](./coding-agent-startup-flow.md): kod yozuvchi (coding) agentlarning keyingi ishga tushishlari uchun belgilangan (fixed) sessiya boshlash oqimi.
- [`prompt-calibration.md`](./prompt-calibration.md): asosiy (root) yoʻriqnomalarni ularni ortiqcha shishib yoki moʻrt boʻlib ketishiga yoʻl qoʻymasdan qanday qilib aniq va foydali saqlash usullari.

## Asosiy maqolalar

Bu roʻyxat ataylab qisqa tutilgan. Harness bu model atrofidagi ishlash tizimi (execution system) degani: agent sikli (loop), vositalarni ishlatish (tool execution), izolyatsiya (sandboxing), holat (state), kontekst, tekshiruv (verification), yakunlash (termination), orkestratsiya va kuzatuvchanlik (observability). Umumiy prompt muhandisligi yoki keng agent-freymvork maqolalari asosiy roʻyxatga kirmaydi.

Dastlabki uchta maqola kursning tayanchi boʻlib qoladi:

- [OpenAI: Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (2026-02-11): agent-first repozitoriylar, repo-lokal kontekst, maxsus linting va strukturaviy himoya toʻsiqlari (guardrails).
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (2025-11-26): inisializatsiya agenti, kod yozuvchi agent, funksiyalar roʻyxati (feature list), jarayon jurnali (progress log) va kontekst oynalari oʻrtasida ishlarni topshirish (handoff).
- [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24): rejalashtiruvchi (planner) / yaratuvchi (generator) / baholovchi (evaluator) rollari, kontekstni qayta ishga tushirish (resets), harnessʼni soddalashtirish va eskirgan taxminlar.

Faqatgina juda aloqador boʻlgan bir nechta 2026-yilgi maqolalar qoʻshilgan:

- [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/) (2026-01-23): Codex runtime harness, vosita (tool) chaqiruvlari, kontekstning oʻsishi va siklning yakunlanishi (loop termination).
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (2026-01-09): modelni va harnessʼni birgalikda baholash (evaluating), hamda evaluation harnessʼlarni agent harnessʼlaridan farqlash.
- [LangChain: Improving Deep Agents with harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) (2026-02-17): kod yozuvchi agentni Terminal Bench 2.0 da Top 30 dan Top 5 ga koʻtarish uchun modelni oʻzgartirmasdan, tizim promptlari, vositalar, middleware, treysing va oʻz-oʻzini tekshirishni (self-verification) yaxshilash.
- [Thoughtworks / Martin Fowler: Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html) (2026-04-02): kod yozuvchi agent foydalanuvchilarining harnessʼlari feedforward yoʻriqnomalar va feedback datchiklari sifatida (deterministik va inferensial nazoratlar bilan).
- [Cursor: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness) (2026-04-30): harnessʼga offline evals, onlayn metrikalar, tool-error taksonomiyasi, modelga xos sozlashlar (tuning) va suhbat oʻrtasida modelni almashtirish (mid-chat switching) orqali doimiy takomillashib boruvchi mahsulot tizimi sifatida qarash.

## 2026-yildagi Qoʻshimcha Manbalar (Extended References)

Bular kursning asosiy manbalari emas, biroq maxsus harness modullarini loyihalashda juda foydali boʻlishi mumkin. Ushbu boʻlimda faqat asosiy matni bevosita agent sikli, vosita ishlatish, kontekstni boshqarish, tekshiruv, izolyatsiya, boshqaruv qatlamlari yoki regressiyani boshqarish (regression governance) ni qamrab olgan manbalargina saqlangan. Sof agent mahsulotlari, platforma eʼlonlari, jamoaviy case studyʼlar va benchmarklar kiritilmagan.

- [OpenAI: Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/) (2026-02-04): harness qayta foydalanish mumkin boʻlgan App Server protokoli sifatida (tred yashash davri, resume, fork, diffs va mijoz integratsiyalari bilan).
- [OpenAI Developers: Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex) (2026-02-23): uzoq davom etadigan vazifalar uchun doimiy (durable) loyiha xotirasi, bosqichlarni (milestone) validatsiya qilish va “done-when” misollari.
- [OpenAI: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/) (2026-04-15): modelga xos boʻlgan (model-native) harnessʼlar, sandboxʼda ishga tushirish (sandbox execution) hamda fayl/buyruq ishlashi.
- [OpenAI: An open-source spec for Codex orchestration: Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/) (2026-04-27): muammolar treykerini (issue tracker) yoki Linear doskasini koʻp agentli boshqaruv paneliga (control plane) aylantirish.
- [Anthropic: Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) (2026-02-05): parallel agentlar jamoalari, vazifa qulflari (task locks), git sinxronizatsiyasi, konteyner izolyatsiyasi va avtonom sikllar.
- [Anthropic: Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) (2026-04-08): sessiya, harness va sandboxʼni almashtirsa boʻladigan (swappable) interfeyslar sifatida ajratuvchi meta-harness qarashi.
- [Anthropic: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem) (2026-04-23): mantiqiy fikrlash kuchi, kontekstni tozalash (pruning) va tizim promptlari, regressiyani nazorat qilishni talab qiluvchi harness oʻzgarishlari sifatida.
- [LangChain: Context Management for Deep Agents](https://www.langchain.com/blog/context-management-for-deepagents) (2026-01-28): kontekstni fayl tizimiga oʻtkazish (offloading), tool-call qisqartirish, xulosalash (summarization) va kontekstni boshqarish harnessʼlari uchun maqsadli evalʼlar.
- [LangChain: Tuning Deep Agents to Work Well with Different Models](https://www.langchain.com/blog/tuning-deep-agents-different-models) (2026-04-29): promptlar, vosita nomlari, middleware va sub-agent konfiguratsiyasi uchun modelga xos harness profillari.
- [LangChain: Continual learning for AI agents](https://www.langchain.com/blog/continual-learning-for-ai-agents) (2026-04-05): agentni takomillashtirishni model, harness va kontekst qatlamlariga boʻlish (treyslar orqali quvvatlanadi).
- [Microsoft: Agent Harness in Agent Framework](https://devblogs.microsoft.com/agent-framework/agent-harness-in-agent-framework/) (2026-03-12): shell/filesystem harnessʼlari, tasdiqlash oqimi (approval flow), boshqariluvchi shell ijrosi va kontekst zichlash (compaction).
- [Google: Announcing ADK for Java 1.0.0](https://developers.googleblog.com/announcing-adk-for-java-100-building-the-future-of-ai-agents-in-java/) (2026-03-30): qayta ishlatiladigan harness primitivlari sifatida plaginlar, hodisa zichlash (event compaction), HITL, sessiya/xotira xizmatlari va A2A.
- [GitHub: Automate repository tasks with GitHub Agentic Workflows](https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/) (2026-02-13): GitHub Actions xavfsiz chiqishlar (outputs), izolyatsiya (sandboxing), ruxsatlar (permissions) va tekshirishlar (review) ga ega agentik jarayon (workflow) ishlatuvchisi sifatida.
- [AWS: AI agents in enterprises: Best practices with Amazon Bedrock AgentCore](https://aws.amazon.com/blogs/machine-learning/ai-agents-in-enterprises-best-practices-with-amazon-bedrock-agentcore/) (2026-02-03): Runtime, Xotira, Gateway, Identifikatsiya/Siyosat, Kuzatuvchanlik va Baholash (Evaluations) boʻyicha korporativ harness qatlamlari.
- [Stripe: Minions: Stripeʼs one-shot, end-to-end coding agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents) (2026-02-09) va [Part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2) (2026-02-19): devbox izolyatsiyasi, maxsus agent harnessʼlari, blueprint holat mashinalari, qoidalar fayllari, MCP vositalari nazorati, xavfsizlik tekshiruvlari va pre-push/CI qayta aloqa sikllari.
- [Cognition: What We Learned Building Cloud Agents](https://cognition.ai/blog/what-we-learned-building-cloud-agents) (2026-04-23): VM izolyatsiyasi, sessiya snapshot/resume, orkestratsiya, boshqaruv (governance), audit loglari va cloud-agent runtimeʼlari uchun integratsiyalar.
- [Cognition: Multi-Agents: Whatʼs Actually Working](https://cognition.ai/blog/multi-agents-working) (2026-04-22): generator-verifier sikllari, toza-kontekst (clean-context) tekshiruvchilari, aqlli-doʻst (smart-friend) yoʻnaltiruvchilari, menejer-xodim muvofiqlashtirishi va agentlararo aloqa chegaralari.
- [Replit: Decision-Time Guidance: Keeping Replit Agent Reliable](https://blog.replit.com/decision-time-guidance) (2026-01-20, yangilangan 2026-01-23): barcha qoidalarni tizim promptiga tiqish oʻrniga, yengil klassifikator qaror qabul qilish nuqtasida qisqa vaziyatga qarab (situational) yoʻriqnoma kiritadi.
- [Vercel: How we made v0 an effective coding agent](https://vercel.com/blog/how-we-made-v0-an-effective-coding-agent) (2026-01-07): dinamik tizim promptlari, streaming rewrite qatlami hamda deterministik/model asosidagi avto-toʻgʻrilagichlar (autofixers).
- [Vercel: Introducing deepsec](https://vercel.com/blog/introducing-deepsec-find-and-fix-vulnerabilities-in-your-code-base) (2026-05-04): skanerlash, tekshirish (investigate), qayta validatsiya (revalidate), boyitish (enrich), eksport, plagin va rad etishni tekshirish (refusal-checker) qadamlari bilan xavfsizlikka qaratilgan kod yozuvchi agent harnessʼi.
- [Sourcegraph: CodeScaleBench](https://sourcegraph.com/blog/codescalebench-testing-coding-agents-on-large-codebases-and-multi-repo-software-engineering-tasks) (2026-03-03): MCP vositalarini oʻzlashtirish, tool-use transkriptlari, benchmark QA, tekshiruvchi (verifier)/qayta ishlab chiqaruvchanlik eshiklari va prompt/muqaddima iteratsiyalarini qamrab oluvchi eval/vosita harnessʼi boʻyicha maʼlumotnoma.

Faqatgina 2025-yilga oid umumiy manbalar asosiy roʻyxatdan chiqarildi. Dastlabki 2025 Anthropic harness maqolasi kursning asosiy manbasi boʻlgani uchungina qoldirildi.

## Oʻqish boʻyicha tavsiya etilgan ketma-ketlik

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
