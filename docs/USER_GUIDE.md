# PrimeGuard — foydalanuvchi qo'llanmasi

## 1. Ishga tushirish

Windows PowerShell'da:

```powershell
cd "$HOME\Projects\PrimeGuard"
& "$HOME\PrimeGuardVenv\Scripts\python.exe" -m pip install -r requirements.txt
& "$HOME\PrimeGuardVenv\Scripts\python.exe" -m pytest -q
& "$HOME\PrimeGuardVenv\Scripts\python.exe" -m streamlit run app.py
```

Brauzer: `http://localhost:8501`.

## 2. Sonni tekshirish — asosiy sahifa

1. Sonni `n` maydoniga kiriting (2 dan boshlab; ko'pi bilan 2048 ta raqam).
2. Chap panelda raundlar sonini (`k`) belgilang.
3. **Sonni tekshirish** tugmasini bosing.
4. Dastur Fermat, Solovay–Strassen va Miller–Rabin xulosasini, bajarilgan raundlar sonini, guvohni va vaqtni ko'rsatadi.
5. **Algoritm qanday ishlaydi?** qismida algoritm, bajarilgan raund va ketma-ket matematik qadamlarni tanlang. Har bir qoldiq asl logdagi tasodifiy asos bilan mustaqil qayta hisoblanadi.
6. Raundlar jadvali va JSON hisoboti yordamida natijalarni saqlang.

**«Aniq murakkab»** — murakkablik guvohi topildi yoki bo'luvchi orqali aniqlandi.
**«Ehtimoliy tub»** — raundlar o'tildi, lekin tublik isbotlanmadi.
**«Aniq tub»** — kichik tub sonlar elagi yoki `n < 2^64` uchun deterministik etalon tekshirdi.

`0` va `1` tub ham, murakkab ham emas; dastur `n ≥ 2` chegarasini tushuntiradi. Bo'sh, manfiy va harfli kiritishlar tegishli xabar bilan rad etiladi.

## 3. Fermat testining cheklovi: Karmaykl tajribasi

**Sonni tekshirish** sahifasining pastida **Karmaykl tajribasini ochish** tugmasini yoqing. U alohida asosiy bo'lim emas, balki asosiy tublik testlariga didaktik namoyishdir.

1. `561` yoki `8911` ni tanlang (yoki `1 000 000` dan oshmaydigan boshqa son kiriting).
2. **Karmaykl sonini tahlil qilish** tugmasini bosing.
3. Uch algoritm natijalarini va Korselt mezonini ko'ring.
4. Interaktiv matematik navigator orqali bitta raunddagi asosni, daraja qoldig'ini va guvohni tekshiring.

`561 = 3 × 11 × 17`. Har bir o'zaro tub asos uchun Fermat tengligi bajariladi. Solovay–Strassen esa **ayrim asoslarda ham** o'tishi mumkin: `a=2` — sinovdan o'tadi; `a=5` — murakkablik guvohi. Hech bir ehtimoliy testning bitta raundi barcha murakkab sonlarni aniqlashi shart emas.

Tajriba hajmi qasddan cheklangan. Katta sonlarni asosiy son tekshiruviga kiriting.

## 4. Algoritmlarni taqqoslash — ikkinchi sahifa

1. **Algoritmlarni taqqoslash** bo'limini oching.
2. Avval `64, 128, 256` bitni sinab ko'ring.
3. Raundlar soni va takrorlashlarni tanlang. Standart **10** ta takrorlash; 10+ tavsiya etiladi.
4. Grafikda tub va murakkab nomzodlarni alohida ko'ring.
5. Jadvaldan median, o'rtacha vaqt, standart og'ish, bajarilgan raundlar va natijalar izchilligini ko'ring; CSV eksport qiling.

Nomzodlar uch algoritm uchun bir xil. Dastlabki sinov va nomzod generatsiyasi vaqtga kiritilmaydi. Murakkab sonlarda guvoh erta topilishi mumkin; shuning uchun vaqtlar har xil. Natijalar kompyuter holatiga bog'liq va nazariy tezlik isboti emas.

## 5. Universitet himoyasi

- Sonni tekshirish: `17` va `21` orqali tub/murakkab farqini tushuntiring.
- Matematik qadamlar: Miller–Rabin kvadratlash zanjiri va oldingi/log qoldiqni ko'rsating.
- Karmaykl: `561` yordamida Fermat testining noto'g'ri musbat xulosasi mumkinligini tushuntiring.
- Taqqoslash: 64/128 bit va 10 takrorlash, median va erta to'xtashlarni izohlang.
- Xulosa: «Ehtimoliy tub» qat'iy matematik isbot emasligini ta'kidlang.

**Cheklov:** dastur tublik tekshiruvlari uchun o'quv prototipi; RSA kalit generatori yoki kriptografik ishlab chiqarish vositasi sifatida taqdim etilmaydi.
