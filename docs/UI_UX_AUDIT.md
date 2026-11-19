# PrimeGuard — UX/UI nazorat auditi va dizayn tizimi

**Loyiha chegarasi:** «Sonlarni tublikka tekshiruvchi ehtimollikka asoslangan algoritmlarning kompleks dasturiy ta'minotini ishlab chiqish».

**Manba:** mavjud Streamlit `app.py`, `ui/round_explorer.py`, `assets/style.css`, Windows 2026-11-19 skrinshotlari, mavjud regressiya testlari.

## 0. Audit mezonlari va bazaviy holat

Bu ballar mutaxassisning amaliy, subyektiv audit bahosi. Ular real auditoriya testidan olingan statistik o'lchov emas.

| Yo'nalish | Boshlang'ich baho | Muammo | Muvaffaqiyat mezoni |
|---|---:|---|---|
| Vazifaga moslik | 9/10 | Faqat ikkita asosiy ish oqimi bo'lishi kerak | RSA oynasi yo'q; 2 ta sahifa |
| Navigatsiya va oqim | 7/10 | Tayyor misol va Karmaykl tajribasi bir-biriga bog'lanmagan | Misol tanlansa to'g'ri maydon yuklanadi, tajriba ochiladi |
| Natijalar izohi | 7/10 | «Guvoh topilmadi» elak orqali aniqlangan holatga ham yoziladi | «Oldindan tekshirildi» alohida ko'rsatiladi |
| Vizual ierarxiya | 6/10 | Neonga o'xshash soyalar va noto'g'ri font aksentlari | Yagona rang tizimi, birlamchi CTA, o'qiladigan kartalar |
| Moslashuvchanlik | 6/10 | 3 ta natija kartasi va 64 ta raundli slayder siqiladi | Kartalar moslashadi, raundlar ro'yxatdan tanlanadi |
| Akademik aniqlik | Avtomatik testlar asosida | Ehtimoliy natijani isbot deb ko'rsatmaslik | Ayni son, asos, qoldiq, raund va izoh mos bo'ladi |

## 1. UI arxitekturasi

```text
PrimeGuard
├── Sonni tekshirish
│   ├── n sonini kiritish + k raundlarini tanlash
│   ├── Yakuniy matematik xulosa
│   ├── Fermat / Solovay–Strassen / Miller–Rabin
│   ├── Matematik qadamlar navigatori
│   ├── Raund jurnali va natijalarni eksport qilish
│   └── Karmaykl/Korselt (ixtiyoriy, ochiladigan dars)
└── Algoritmlarni taqqoslash
    ├── Bit uzunligi / k / takrorlash
    ├── Tub va murakkab nomzod filtri
    ├── Median tendensiyasi yoki taqqoslash grafigi
    └── O'zbekcha jadval + ilmiy CSV eksport
```

RSA dastur interfeysidan olib tashlangan, tarixiy yordamchi kod backendda qolgan; loyihaning vazifalari sifatida ko'rsatilmaydi.

## 2. Dizayn tokenlari

Interfeys foydalanuvchiga «hacker» estetikasini emas, akademik ishonchlilikni berishi kerak.

| Element | Token | Qiymat |
|---|---|---|
| Asosiy fon | `--pg-canvas` | `#0B1220` |
| Kartalar foni | `--pg-surface` | `#131F32` |
| Asosiy matn | `--pg-ink` | `#F2F6FA` |
| Ikkinchi darajali matn | `--pg-muted` | `#ACBCCD` |
| Asosiy harakat | `--pg-accent` | `#69D6C5` |
| Ehtimoliy tub/tekshiruvdan o'tgan | `--pg-success` | `#75D9AF` |
| Aniq murakkablik | `--pg-error` | `#FF8898` |
| O'quv ogohlantirishi | `--pg-warning` | `#F3C77B` |

Mahalliy OS shriftlari qo'llanadi; tashqi font/CDN talab etilmaydi. `.streamlit/config.toml` Streamlit-ning o'z ranglarini ham bir xil qiladi. WCAG AA kontrast testlari kichik matn va CTA uchun avtomatik tekshiriladi. Fokus holati, kichik ekran, va `prefers-reduced-motion` mavjud.

## 3. Nazoratli bajarish bosqichlari

| Bosqich | Vazifa | Tekshiruv |
|---|---|---|
| A | Mavzu va ekranlar oqimini tekshirish | 2 asosiy bo'lim, matematik API saqlangan |
| B | Dizayn tokenlari va natija kartalari | CSS; Streamlit theme; kontrast testi |
| C | Sonni tekshirishning birinchi foydalanish oqimi | Asosiy CTA, tushunarli kiritish va guvohlar |
| D | Matematik navigator | 1–64 raund uchun ro'yxat, qadam progressi, logga moslik |
| E | Karmaykl darsi | Son yuklash, izoh va guvohlar, alohida xato holati |
| F | Algoritmlarni taqqoslash | Toza grafiklar, o'zbekcha sarlavha, filtr va CSV |
| G | Yakuniy QA | GitHub Actions, Windows Chrome/Edge 100% va 125% zoom, 1366 px / kichik ekran |

**Kodga o'tkazish qoidasi:** yangi algoritm yoki majburiy bo'lmagan yirik funksiya qo'shilmaydi. Har bir xatti-harakat natijalar jurnalini buzmasligi shart. Dizayn interfeysi matematik haqiqatni o'zgartirmaydi.

**Tekshirish uchun alohida topshiriqlar:**
- `2`, `17`, `21`, `561`, `2^127−1` kabi turli holatlar;
- `0`, `1`, manfiy, bo'sh va harfli kiritishlar;
- maxsus elak tufayli 0 raund bajarilgan holat;
- 20 va 64 raundda navigatorni boshqarish;
- benchmark natijasi filtr o'zgarganda saqlanishi;
- Karmaykl tugmasi o'quv panelini ochishi;
- Windows vizual sinovi: uch kartaning kengligi, bo'limlar, grafiklar, 100% va 125% zoom.

## 4. Holat va cheklovlar

Mazkur dizayn o'zgarishlari yangi branch'da test qilinadi. Avtomatik testdan o'tish vizual yoki real foydalanuvchi qabul sinovini almashtirmaydi. Windows brauzeridagi yakuniy tasdiq foydalanuvchining sinovi bilan amalga oshiriladi.
