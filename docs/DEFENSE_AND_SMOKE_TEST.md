# PrimeGuard — Windows tekshiruvi va 5 daqiqalik loyiha himoyasi

**Topshiriq:** sonlarni tublikka tekshiruvchi ehtimollikka asoslangan algoritmlarning kompleks dasturiy ta'minotini ishlab chiqish.

## 1. Windows'da ishga tushirish va test

```powershell
cd "$HOME\Projects\PrimeGuard"
git status --short
git pull --ff-only origin main
& "$HOME\PrimeGuardVenv\Scripts\python.exe" -m pip install -r requirements.txt
& "$HOME\PrimeGuardVenv\Scripts\python.exe" -m pytest -q
& "$HOME\PrimeGuardVenv\Scripts\python.exe" -m streamlit run app.py
```

**Eslatma:** `git status --short` lokal o'zgarishlarni ko'rsatsa, ularni saqlamasdan `git pull` qilish mumkin emas. Dasturning o'ziga kirish: `http://localhost:8501`.

### Vizual smoke-test ro'yxati

- [ ] Navigatsiyada aynan **2 ta** sahifa: «Sonni tekshirish» va «Algoritmlarni taqqoslash». RSA oynasi yo'q.
- [ ] `17`: aniq tub. `21`: murakkab. `2`: yagona juft tub. `0` va `1`: n ≥ 2 sohasi tushuntiriladi.
- [ ] Matn xatolari (harf, bo'sh, manfiy son) tushunarli xabar beradi.
- [ ] Uch testning natija kartalari, haqiqiy raundlar, guvoh va bajarilish vaqti chiqadi.
- [ ] Interaktiv algoritm/raund/qadam tanlash natijani tasodifiy qayta yaratmaydi.
- [ ] «Karmaykl tajribasini ochish» orqali `561` tahlili: `3,11,17`, Korselt mezoni va algoritmlar natijalari.
- [ ] Karmaykl tajribasiga 1 000 000 dan katta son kiritilsa ogohlantirish chiqadi, og'ir faktorizatsiya boshlanmaydi.
- [ ] Benchmark: 64/128 bit, 10 takrorlash; grafiklarga filtr ishlaydi va jadval/CSV saqlanadi.
- [ ] JSON hisobot yuklanadi. Terminalda exception yo'q.

## 2. Matematik namoyish

- **Fermat:** `a^(n-1) mod n` qiymati `1` ga teng bo'lmasligi sonning murakkabligini isbotlaydi.
- **Solovay–Strassen:** Yakobi belgisi bilan daraja qoldig'ini solishtiradi.
- **Miller–Rabin:** `n-1=2^s*d` va kvadratlash yordamida guvohlarni tekshiradi.
- **561:** `a=2` uchun Fermat va Solovay–Strassen raundi o'tishi mumkin; `a=5` Solovay–Strassen uchun guvoh.
- **Xatolik:** Solovay–Strassen `2^-k`, Miller–Rabin `4^-k` — mos shartlarda nazariy yuqori chegaralar. Fermat uchun universal chegara yo'q.
- **Etalon:** 64-bitdan kichik sonlar uchun alohida deterministik Miller–Rabin bazalari bilan nazorat.

## 3. 5 daqiqalik himoya

**0:00–0:40 — Muammo:** katta sonlarning tubligini tekshirish zarurati va ehtimoliy yondashuvning amaliy ahamiyati.

**0:40–1:40 — Uchta algoritm:** Fermat, Solovay–Strassen, Miller–Rabin va ular orasidagi matematik farq.

**1:40–2:45 — Sonni tekshirish:** `17`, `21` va raund navigatorini namoyish qiling; guvoh nima ekanini tushuntiring.

**2:45–3:35 — Karmaykl:** `561` misolida «sinovdan o'tish» va «tublik isboti» orasidagi farqni ko'rsating.

**3:35–4:30 — Taqqoslash:** 64/128 bit, takrorlashlar, median, tarqalish va grafiklarni izohlang.

**4:30–5:00 — Natija:** JSON/CSV va avtomatik testlarni ko'rsating; sonni aniq murakkab deb belgilash hamda ehtimoliy tub xulosalarini farqlang.

## 4. Qabul mezonlari

Avtomatik testlar muvaffaqiyatli, matematik ifodalar asl qoldiq bilan mos, ikki sahifa Windows brauzerida ochiladi, Karmaykl va benchmark natijalari tushunarli, eksport ishlaydi. **Windows vizual testlari alohida foydalanuvchi tomonidan tasdiqlanadi.**
