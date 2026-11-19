# PrimeGuard: 5 daqiqalik himoya va Windows tekshiruvi

## 1. Windows vizual tekshiruvi (PowerShell)

Loyiha papkasida:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\start_primeguard.ps1
```
Skript Python virtual muhitini yaratadi (Python 3.11, keyin 3.x, keyin python), dependencies o'rnatadi, compileall va pytest testlarini bajaradi, so'ng Streamlitni faqat lokal 127.0.0.1:8501 da ishga tushiradi. Python o'rnatilmagan yoki papkaga yozish huquqi yo'q bo'lsa, muammoni bartaraf qiling. Ishga tushirish yakunlanganini taxmin qilmang: terminal va brauzer natijalarini tekshiring.

Brauzer: http://localhost:8501

### Vizual tekshiruv ro'yxati
- [ ] Barcha to'rtta bo'lim ochiladi: Sonni tekshirish, Karmaykl tahlili, Tezlik taqqoslash, RSA parametrlari.
- [ ] 17 kiritilganda aniq tub; 21 kiritilganda murakkab ko'rsatiladi.
- [ ] 561 Karmaykl tahlilida faktorlari 3, 11, 17 va Korselt mezoni ko'rinadi.
- [ ] 64/128 bit, 3 takrorlash benchmarki grafik va jadval beradi.
- [ ] RSA 65 bit modul yaratadi, N.bit_length() = 65, N = p*q, phi = (p-1)*(q-1).
- [ ] CSV/JSON yuklab olish ishlaydi.
- [ ] Noto'g'ri kiritishlarda tushunarli xabar chiqadi, interfeys yiqilmaydi.
- [ ] Terminalda Python xatolari yo'q; oynalar kichik ekran va oddiy zoomda o'qiladi.

## 2. Tasodifiy bo'lmagan Karmaykl namoyishi

```powershell
.\.venv\Scripts\python.exe demo_carmichael_561.py
```
561 = 3 * 11 * 17, murakkab son. Skript oldindan belgilangan o'zaro tub asoslarda Fermat, Solovay-Strassen va Miller-Rabin shartlarini ko'rsatadi. Har bir asos uchun Fermat PASS chiqishi kerak. Bu Fermat PASS degani tub son isboti emasligini ko'rsatadi. Boshqa ikki algoritm uchun har bir alohida asos albatta FAIL bo'lishi shart emas; ularning xulosasi tanlangan asosga bog'liq. Asosiy interfeysning Karmaykl bo'limi esa probabilistik tajribadir.

## 3. 5 daqiqalik himoya

**0:00-0:40 — Kirish.** "PrimeGuard sonlarning tubligini uch ehtimoliy algoritm bilan tekshiradi. U matematik raundlarni va ishlash vaqtini ko'rsatadi."

**0:40-1:40 — Nazariya.** "Fermat a^(n-1) mod n = 1 ni tekshiradi. Solovay-Strassen Eyler-Yakobi mezoniga tayanadi. Miller-Rabin n-1 = 2^s*d ni ajratib, kuchli guvohlarni izlaydi. Guvoh topilsa son aniq murakkab; guvoh topilmasa faqat ehtimoliy tub."

**1:40-2:30 — Asosiy ekran.** 17 va 21 ni tekshirib, xulosa, raund jurnali va vaqtni ko'rsating.

**2:30-3:40 — Karmaykl.** 561 = 3*11*17 ni oching. "561 murakkab, ammo har bir o'zaro tub asos uchun Fermat shartini bajaradi. Shu sabab Fermatni yagona ishonchli test sifatida ishlatib bo'lmaydi." Terminaldagi demo_carmichael_561.py oldindan belgilangan asoslar bilan qayta namoyish qilinadi.

**3:40-4:30 — Benchmark.** 64/128 bit, 3 takrorlash. "Grafik empirik vaqtlarni ko'rsatadi, matematik murakkablik isboti emas; kompyuter va tasodifiy asoslar natijaga ta'sir qiladi."

**4:30-5:00 — Xulosa.** "Dastur natijalarni CSV/JSON saqlaydi, 64-bit diapazonda deterministik etalon bilan tekshiradi. Katta sonlarda ehtimoliy tublik qat'iy isbot emas. RSA bo'limi o'quv parametrlari yaratadi, to'liq kalit juftligini emas."

## Savollarga javob
- **Nega uchta algoritm?** Xatolik kafolatlari, nazariy asoslar va ishlash tezligini taqqoslash uchun.
- **Miller-Rabin 100% aniqmi?** Tasodifiy rejimda yo'q; alohida belgilangan asoslar bilan 0 <= n < 2^64 diapazonda deterministik etalon mavjud.
- **561 nimaga kerak?** Fermatning noto'g'ri musbat xulosaga olib kelishi mumkinligini tushuntirish uchun.
- **k nima?** Tasodifiy tekshiruv raundlari soni. Mustaqil tasodifiy asoslar uchun MR xatolik yuqori chegarasi 4^(-k), SS uchun 2^(-k).
- **RSA tayyormi?** Faqat p, q, N va phi(N) o'quv parametrlari; e/d va xavfsiz kalit formati yo'q.
- **Benchmark adolatlimi?** Bir xil nomzodlar qo'llanadi, lekin har bir algoritmning erta to'xtashi va tasodifiy asoslari sabab natija tajriba sharoitiga bog'liq.

## Topshirish mezoni
Barcha avtomatik testlar o'tishi, Windows interfeysini tekshirish bandlari tasdiqlanishi, Karmaykl deterministik demo xatosiz bajarilishi va 5 daqiqalik himoya mashq qilinishi kerak.
