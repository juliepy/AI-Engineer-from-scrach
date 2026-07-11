# Electron Arxitektura Qoidalari

- Renderer kodi bevosita fayl tizimiga kira olmaydi.
- Preload — bu renderer va Electron main oʻrtasidagi yagona koʻprik.
- Qidirish va indekslash mantiqlari (logic) UI komponentlarida emas, balki xizmatlar (service) modullarida joylashadi.
- Logging (log yozish) strukturaviy boʻlishi va xizmat chegaralaridan (service boundaries) uzatilishi kerak.
