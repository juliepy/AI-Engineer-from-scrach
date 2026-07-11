[中文版本 →](../../../zh/projects/project-02-agent-readable-workspace/)

> İlgili dersler: [Ders 03. Depoyu tek doğruluk kaynağınız yapın](./../../lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md) · [Ders 04. Talimatları dosyalara bölün](./../../lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)
> Şablon dosyaları: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Proje 02. Projeyi okunabilir kılın ve kaldığınız yerden devam edin

## Ne Yapacaksınız

Depoya "okunabilirlik" ekleyin; böylece yeni bir ajan proje yapısını hızla anlayabilsin, mevcut ilerlemeyi bilsin ve çalışmayı sürdürebilsin. Somut olarak: doküman içe aktarma, doküman detay görünümü ve yerel kalıcılığı, iki oturuma yayılı şekilde tamamlayın.

İki kez çalıştırın: ilk seferinde hiçbir yardım olmadan, ikinci seferinde `ARCHITECTURE.md`, `PRODUCT.md` ve `session-handoff.md` önceden depoya yerleştirilmiş şekilde.

## Depodaki projeyi kullanın

Depo yolu: [`projects/project-02/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02)

| Dizin | İçerik | Nasıl kullanılır |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/starter) | Project 01 kodu; tamamlanmamış doküman içe aktarma, detay görünümü ve kalıcılık içerir. Dokümanlar vardır ama incedir; `session-handoff.md` yoktur. | İkinci agent oturumunun ne kadar bağlamı yeniden keşfetmesi gerektiğini ölçün. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) | Aynı ürün dilimini tamamlar ve [`projects/project-02/solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) altında çekirdek dokümanları, [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/feature_list.json) ve [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/session-handoff.md) dosyalarını ekler. | Yeni oturumun yalnızca depo durumuna bakarak çalışmaya devam edip edemediğini kontrol edin. |

Ürün özellikleri doküman içe aktarma, tam detay/içerik yükleme ve yeniden başlatmalar arasında kalıcılıktır; harness özelliği ise devredilebilir, agent-readable workspace'tir.

## Araçlar

- Claude Code veya Codex
- Git
- Node.js + Electron

## Harness Mekanizması

Ajanın okuyabildiği çalışma alanı + kalıcı durum dosyaları
