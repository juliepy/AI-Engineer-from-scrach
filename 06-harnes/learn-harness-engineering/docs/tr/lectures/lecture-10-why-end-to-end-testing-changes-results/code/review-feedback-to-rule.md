# Örnek: İnceleme geri bildirimini kurala dönüştürmek

Tekrar eden inceleme yorumu:

> Renderer içinden dosya sistemi araçlarını çağırmayın. Preload köprüsünü kullanın.

Yükseltilmiş harness kuralı:

- renderer kodunda `fs` kullanımını engelleyen bir lint veya import kuralı ekle
- preload sınırını açıklayan çözüm metnini ekle
