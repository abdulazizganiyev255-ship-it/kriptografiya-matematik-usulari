# PrimeGuard kod tuzilmasi — sodda qo'llanma

## Loyihaning vazifasi
PrimeGuard butun sonning tub yoki murakkab ekanini uchta ehtimoliy algoritm bilan tekshiradi va natijalarni taqqoslaydi.

## Papkalar nima qiladi?

```text
PrimeGuard/
├── app.py                    # Dasturni ishga tushiradigan Streamlit oynasi
├── core/                     # Asosiy matematik algoritmlar
│   ├── models.py              # Natija va raund loglari
│   ├── number_theory.py       # EKUB, Yakobi belgisi, elak va etalon test
│   ├── fermat.py              # Fermat tublik testi
│   ├── solovay_strassen.py    # Solovay–Strassen tublik testi
│   └── miller_rabin.py        # Miller–Rabin tublik testi
├── analytics/                # Qo'shimcha tahlil va tajribalar
│   ├── carmichael.py          # Karmaykl sonlari tahlili
│   ├── benchmark.py           # Algoritmlar tezligini solishtirish
│   └── prime_generator.py     # Ehtimoliy tub son yaratish
├── tests/                    # Avtomatik testlar
├── assets/style.css           # Interfeys dizayni
├── docs/                     # Akademik va kod bo'yicha hujjatlar
├── requirements.txt           # Python kutubxonalari
└── README.md                  # Loyiha tavsifi
```

## Dastur qanday ishlaydi?
1. Foydalanuvchi `app.py` oynasiga tekshiriladigan `n` sonini kiritadi.
2. `app.py` tanlangan algoritmni chaqiradi.
3. Algoritm avval sonning chegarasi, juftligi va kichik tub bo'luvchilarini tekshiradi.
4. Keyin algoritm o'z formulasini modul bo'yicha hisoblaydi.
5. Har bir urinish `RoundLog` obyektiga yoziladi.
6. Yakuniy natija `PrimalityResult` obyektida qaytadi.
7. Interfeys xulosa, urinishlar tarixi va bajarilish vaqtini ko'rsatadi.

## Uch algoritmni sodda tushunish
### Fermat
Fermat teoremasiga ko'ra, tub `p` va unga o'zaro tub `a` uchun `a^(p-1) mod p = 1`. Tenglik buzilsa, `n` aniq murakkab. Tenglik bajarilsa, faqat ehtimoliy tub. Karmaykl sonlari bu testni aldashi mumkin.

### Solovay–Strassen
`a^((n-1)/2) mod n` qiymati Yakobi belgisi `(a/n)` bilan solishtiriladi. Farq topilsa — aniq murakkab; barcha raundlardan o'tsa — ehtimoliy tub.

### Miller–Rabin
`n-1 = 2^s * d` ko'rinishiga ajratiladi, `d` toq. Tanlangan asos uchun modul darajalar tekshiriladi. Guvoh topilsa — murakkab; barcha raundlardan o'tsa — ehtimoliy tub.

## Natija ma'nosi
- **Murakkab:** algoritm murakkablik guvohini topdi; xulosa aniq.
- **Ehtimoliy tub:** tanlangan raundlardan o'tdi; bu matematik isbot emas.
- **Aniq tub:** faqat deterministik tekshiruv yoki to'liq isbot bo'lsa aytiladi.

`is_prime_deterministic_64(n)` faqat `0 <= n < 2**64` diapazonida aniq natija beradi. Katta diapazonda kafolat yo'q.

## Ishga tushirish
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

Testlar: `pytest -q`

## Himoyada aytish uchun qisqa izoh
"PrimeGuard sonlarning tubligini tekshiruvchi dasturiy tizim. Unda Fermat, Solovay–Strassen va Miller–Rabin algoritmlari ishlatiladi. Foydalanuvchi son va raundlar sonini kiritadi, dastur algoritmlarning hisoblash jarayonini, xulosasini va vaqtini ko'rsatadi. Algoritmlar natijalari avtomatik testlar va 64-bit diapazondagi deterministik etalon bilan tekshiriladi. Katta sonlarda ehtimoliy tub xulosasi aniq matematik isbotdan farqli ko'rsatiladi."