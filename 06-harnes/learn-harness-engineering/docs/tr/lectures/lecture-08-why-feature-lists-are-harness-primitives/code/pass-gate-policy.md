# Geçer kapı politikası

Bir özellik yalnızca aşağıdaki koşullar sağlandığında `passes: false` durumundan `passes: true` durumuna geçebilir:

- beklenen iş akışı çalıştırılmış olmalı
- başarının kanıtı kaydedilmiş olmalı
- test edilen yolda engelleyici bir hata bulunmamalı
- uygulama, çözümü ardından bozuk veya belirsiz bir durumda bırakmamalı
