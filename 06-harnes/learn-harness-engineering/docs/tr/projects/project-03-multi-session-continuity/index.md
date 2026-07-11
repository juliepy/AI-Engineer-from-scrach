[中文版本 →](../../../zh/projects/project-03-multi-session-continuity/)

> İlgili dersler: [Ders 05. Bağlamı oturumlar boyunca canlı tutun](./../../lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md) · [Ders 06. Her ajan oturumundan önce başlatma yapın](./../../lectures/lecture-06-why-initialization-needs-its-own-phase/index.md)
> Şablon dosyaları: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Proje 03. Ajanı oturum yeniden başlatmaları boyunca çalışır tutun

## Ne Yapacaksınız

Ajana kapsam kontrolü ve doğrulama eşikleri ekleyin. Doküman parçalama, üst veri çıkarımı, dizinleme ilerleme göstergesi ve alıntı tabanlı Soru-Cevap akışını uygulayın.

Bir `feature_list.json` gerekir; her özelliğin açık bir durumu olmalıdır. Kural basittir: aynı anda tek özellik, çalışır doğrulama kanıtı olmadan `passing` işaretlemesi yok. Depodaki starter erken bir özellik listesi içerir ama tam yeniden başlatma ve devir artefaktları eksiktir; solution bu artefaktları tamamlar. İkisini karşılaştırın.

İki kez çalıştırın: ilk seferinde kısıt olmadan, ikinci seferinde katı uygulamayla.

## Depodaki projeyi kullanın

Depo yolu: [`projects/project-03/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03)

| Dizin | İçerik | Nasıl kullanılır |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/starter) | Project 02 kodu; indeksleme ve alıntılı Soru-Cevap tamamlanmamıştır. Starter sürümü [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/starter/feature_list.json) içerir ama son yeniden başlatma/devir artefaktları eksiktir. | Agent'ın birden çok özellik arasında kayıp kaymadığını ve yeniden başlatmadan sonra durumu kaybedip kaybetmediğini ölçün. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/solution) | Doküman parçalama, üst veri, indeksleme durumu ve alıntılı Soru-Cevap tamamlanmıştır; ayrıca [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/session-handoff.md), [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/claude-progress.md), [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/clean-state-checklist.md) eklenmiştir. | Her özelliğin ancak doğrulama kanıtı varsa `passing` olup olmadığını kontrol edin. |

## Araçlar

- Claude Code veya Codex
- Git
- Node.js + Electron

## Harness Mekanizması

İlerleme günlüğü + oturum devri + çok oturumlu süreklilik
