# PrimeGuard — ehtimollikka asoslangan tublikni tekshirish

**Loyiha mavzusi:** «Sonlarni tublikka tekshiruvchi ehtimollikka asoslangan algoritmlarning kompleks dasturiy ta'minotini ishlab chiqish».

PrimeGuard — katta natural sonlarning tubligini ehtimoliy algoritmlar yordamida tekshiradigan, har bir sinovning matematik asosini izohlaydigan va algoritmlarning hisoblash vaqtini bir xil sharoitda taqqoslaydigan **o'quv dasturi**.

**Muhim:** bu loyiha RSA kalit yaratish tizimi, shifrlash dasturi yoki sertifikatlangan kriptografik kutubxona emas. `analytics/prime_generator.py` ichidagi tub nomzod generatsiyasi benchmark uchun ishlatiladi; tarixiy `generate_rsa_pair` yordamchi funksiyasi asosiy interfeysda namoyish etilmaydi.

## Asosiy imkoniyatlar

| Bo'lim | Nima bajaradi? |
|---|---|
| **1. Sonni tekshirish** | Natural son `n` va raundlar soni `k` ni qabul qiladi. Fermat, Solovay–Strassen va Miller–Rabin natijalarini, bajarilgan raundlar sonini, murakkablik guvohini, nazariy xatolik chegarasini va vaqtni ko'rsatadi. |
| **1-bo'lim ichidagi ixtiyoriy Karmaykl tajribasi** | `561` va boshqa kichik sonlar yordamida Fermat sinovining chegarasini va Korselt mezonini tushuntiradi; alohida asosiy sahifa emas. |
| **2. Algoritmlarni taqqoslash** | Aynan bir xil tub va murakkab son nomzodlarida uchta testning vaqtini o'lchaydi, median va tarqalishni ko'rsatadi, CSV natijasini beradi. |

Matematik navigator avvalgi tekshiruvning haqiqiy `RoundLog` yozuvidan foydalanadi: algoritm, raund va hisoblash qadamini tanlash mumkin. Interfeys qayta chizilganda yangi tasodifiy asos tanlanmaydi. Son tekshiruvining natijasi JSON formatida ham saqlanadi.

### Algoritmlar va natijaning ma'nosi

1. **Fermat:** `a^(n-1) ≡ 1 (mod n)` mezoni. Ushbu mezonning bajarilishi tub son ekanini isbotlamaydi. Karmaykl sonlari barcha o'zaro tub asoslarda bu shartni bajaradi; universal `2^-k` xatolik chegarasi yo'q.
2. **Solovay–Strassen:** Yakobi belgisini `a^((n-1)/2) mod n` bilan solishtiradi. Mustaqil tasodifiy asoslarda noto'g'ri musbat xulosa ehtimoli yuqori chegarasi `2^-k`. **Bitta raund murakkab sonni aniqlamasligi mumkin**, shu jumladan Karmaykl sonlarida.
3. **Miller–Rabin:** `n-1 = 2^s * d` ajratish va ketma-ket kvadratlash orqali kuchli guvohlarni izlaydi. Mustaqil raundlarda noto'g'ri musbat xulosa yuqori chegarasi `4^-k`.

**«Murakkab»** — sonning murakkabligi guvoh bilan yoki dastlabki bo'linish tekshiruvida aniqlandi. **«Ehtimoliy tub»** — belgilangan raundlardan o'tdi, ammo bu matematik isbot emas. **«Aniq tub»** — dastlabki kichik tub sonlar ro'yxati yoki `n < 2^64` diapazonidagi alohida deterministik etalon tasdiqlagan holat.

Xatolik chegaralari nazariy yuqori chegaralardir; tajribada kuzatilgan foiz yoki har bir sinovning sertifikati emas. Tasodifiy asoslar `secrets` orqali mustaqil tanlanadi.

### Karmaykl soni bilan ilmiy misol

`561 = 3 × 11 × 17` — murakkab son. `a = 2` uchun Fermat sharti ham, Solovay–Strassenning **aynan shu bitta raundi** ham bajariladi. `a = 5` uchun Solovay–Strassen murakkablik guvohini topadi. Demak, «testdan o'tdi» natijasi bilan «isbotlangan tub» tushunchalarini aralashtirib bo'lmaydi.

## React + FastAPI interfeys (ixtiyoriy v2)

Asosiy Python algoritmlarini o'zgartirmasdan, alohida **React + TypeScript + Vite** interfeys va **FastAPI** adapter ham ishlab chiqilgan. Vizual maketning ikki asosiy ish maydoni loyiha mavzusiga qat'iy moslashtirilgan: **Sonni tekshirish** va **Algoritmlarni taqqoslash**. Karmaykl/Korselt tajribasi birinchi bo'lim ichida qoladi. RSA oynasi yo'q.

Windows o'rnatish, ikki terminalda ishga tushirish, REST endpointlari, JSON transportdagi butun sonlarning aniqligi va CI nazorati: [React laboratoriya qo'llanmasi](docs/REACT_LAB.md).

## Ishga tushirish

Python 3.11–3.13 va Windows PowerShell uchun:

```powershell
cd "$HOME\Projects\PrimeGuard"
& "$HOME\PrimeGuardVenv\Scripts\python.exe" -m pip install -r requirements.txt
& "$HOME\PrimeGuardVenv\Scripts\python.exe" -m pytest -q
& "$HOME\PrimeGuardVenv\Scripts\python.exe" -m streamlit run app.py
```

Brauzer: `http://localhost:8501`.

Agar boshqa tizimda birinchi marta o'rnatayotgan bo'lsangiz, virtual muhitni yaratib, `python -m pip install -r requirements.txt` va `python -m streamlit run app.py` dan foydalaning.

## Sinov va qabul mezonlari

- `2`, `17`, `104729` kabi tub sonlar va `4`, `21`, `91` kabi murakkab sonlar uchun mantiqan to'g'ri natija.
- `0`, `1`, manfiy, bo'sh va harfli kiritishlar uchun tushunarli domen cheklovi.
- `561` misolida Fermat cheklovi va Solovay–Strassenning asosga bog'liq xulosasi to'g'ri tushuntiriladi.
- Miller–Rabin jurnali haqiqiy hisoblangan modular qoldiqni ifodalaydi.
- Bir xil nomzodlarda takroriy vaqt o'lchovlari, median, tarqalish, erta to'xtashlar va CSV.
- Matematik natijalar asosiy navigatsiyadagi **ikkita** sahifada. RSA oynasi yo'q.
- Avtomatik testlar va Windows'da brauzer orqali tekshiruv o'tkaziladi.

## Loyiha tuzilmasi

```text
app.py                      # ikki sahifali Streamlit interfeys
core/fermat.py              # Fermat testi
core/solovay_strassen.py    # Solovay–Strassen testi
core/miller_rabin.py        # Miller–Rabin testi
core/witness.py             # tasodifiy asoslarni tanlash
core/number_theory.py       # EKUB, Yakobi belgisi, deterministik 64-bit etalon
analytics/round_explainer.py # matematik raund izohi
analytics/carmichael.py     # yordamchi Karmaykl / Korselt tajribasi
analytics/benchmark.py      # taqqoslovchi vaqt o'lchovi
analytics/prime_generator.py # benchmark nomzodlarini yaratish
ui/round_explorer.py        # interaktiv matematik navigator
tests/                      # avtomatik testlar
docs/                       # foydalanuvchi va himoya qo'llanmalari
```

## Akademik manbalar

- G. L. Miller, *Riemann's Hypothesis and Tests for Primality*, Journal of Computer and System Sciences 13(3), 1976.
- R. Solovay va V. Strassen, *A Fast Monte-Carlo Test for Primality*, SIAM Journal on Computing 6(1), 1977.
- M. O. Rabin, *Probabilistic Algorithm for Testing Primality*, Journal of Number Theory 12(1), 1980.
- Korselt mezoni, 1899 — Karmaykl sonlarini xarakterlash.

Qolgan cheklovlar va tekshiruv protokoli: [Akademik validatsiya](docs/ACADEMIC_VALIDATION.md), [Foydalanuvchi qo'llanmasi](docs/USER_GUIDE.md), [Himoya va Windows sinovi](docs/DEFENSE_AND_SMOKE_TEST.md).
