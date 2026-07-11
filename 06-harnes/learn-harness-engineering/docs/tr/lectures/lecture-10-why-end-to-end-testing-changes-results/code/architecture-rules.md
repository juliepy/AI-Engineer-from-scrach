# Electron mimari kuralları

- Renderer kodu dosya sistemine doğrudan erişemez.
- Preload, renderer ile Electron main arasındaki tek köprüdür.
- Geri getirme ve dizinleme mantığı arayüz bileşenlerinde değil, servis modüllerinde yaşar.
- Loglama yapılandırılmış olmalı ve servis sınırlarından yayılmalıdır.
