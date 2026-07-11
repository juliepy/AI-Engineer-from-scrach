# Yöntem Haritası

Bu tablo, en yaygın uzun süreli kod yazma ajanı hata modlarını, onları
genellikle önce düzelten dosya veya çalışma kuralına haritalar.

| Hata modu | Pratikte nasıl göründüğü | Birincil çözüm | Destekleyici dosya |
| --- | --- | --- | --- |
| Soğuk başlangıç kafa karışıklığı | Yeni bir oturum zamanının çoğunu kurulumu ve durumu yeniden keşfederek geçirir | Depoyu kayıt sistemi yapın | `claude-progress.md` |
| Kapsam yayılması | Ajan birkaç özelliğe başlar ve hiçbirini temiz bir şekilde bitirmez | Aktif kapsamı kısıtlayın | `feature_list.json` |
| Erken tamamlama | Ajan, kod düzenlemelerinden sonra ancak çalıştırılabilir kanıttan önce bitti der | Tamamlamayı kanıta bağlayın | `clean-state-checklist.md` |
| Kırılgan başlatma | Her oturum, projeyi nasıl başlatacağını yeniden öğrenir | Kurulumu ve doğrulamayı standartlaştırın | `init.sh` |
| Zayıf devir | Sıradaki oturum neyin doğrulandığını, neyin bozuk olduğunu veya neyin sıradaki olduğunu söyleyemez | Açık bir devirle bitirin | `session-handoff.md` |
| Öznel inceleme | İnceleme kalitesi zevke veya hafızaya bağlıdır | Çıktıyı sabit kategorilerle puanlayın | `evaluator-rubric.md` |

## Çalışma İlkesi

Gözlemlenen hata modunu doğrudan ele alan en küçük dosyayı ekleyin.
Her güvenilirlik sorununu, tek bir genel talimat dosyasına daha fazla metin
yığarak çözmekten kaçının.
