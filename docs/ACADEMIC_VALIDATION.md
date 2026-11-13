# PrimeGuard: akademik validatsiya protokoli

## Maqsad
Uch ehtimoliy tublik testini (Fermat, Solovay–Strassen, Miller–Rabin) bir xil sinov sharoitida solishtirish va ularning xulosalarini deterministik etalon tekshiruv bilan baholash.

## Natija semantikasi
- `Composite`: algoritm murakkablik guvohini topdi; son aniq murakkab.
- `Prime`: faqat mustaqil deterministik tekshiruv yoki to'liq isbotlangan kichik diapazon natijasi.
- `Probably Prime`: probabilistik test barcha raundlardan o'tdi; bu matematik isbot emas.
- `Unknown`: parametrlar yoki diapazon sababli tekshiruv ishonchli yakunlanmadi.

## Algoritmlarning nazariy xatolik chegaralari
| Algoritm | Murakkab sonni tub deb qabul qilish ehtimolining yuqori chegarasi |
|---|---|
| Fermat | Karmaykl sonlari sababli universal eksponensial chegara yo'q |
| Solovay–Strassen | `2^-k` |
| Miller–Rabin | `4^-k` |

Bu chegaralar mustaqil va tegishli taqsimotdan tanlangan asoslar shartida qo'llanadi. Amaliy implementatsiyada bazalar qanday tanlanishi ham qayd etilishi lozim.

## Deterministik etalon tekshiruv
`is_prime_deterministic_64(n)` faqat `0 <= n < 2**64` diapazonida deterministik Miller–Rabin bazalar to'plamidan foydalanadi. `n >= 2**64` uchun funksiya aniq natija deb da'vo qilmaydi va `ValueError` chiqaradi.

## Test matritsasi
1. Chegaralar: `-1, 0, 1, 2, 3, 4, 5`.
2. Kichik tub va murakkab sonlar.
3. Carmichael sonlari: `561, 1105, 1729, 2465, 2821, 6601`.
4. Kuchli psevdotublar va deterministik bazalarga qarshi ma'lum kompozitlar.
5. `2**61 - 1` kabi katta tub sonlar.
6. `2**64` chegarasidan tashqari qiymatlar.
7. Kichik diapazonda mustaqil trial-division oracle bilan to'liq solishtirish.

## Benchmark metodologiyasi
- Har bir bit uzunligi uchun aynan shu tub nomzod va aynan shu semiprime nomzod uch algoritmda tekshiriladi.
- Nomzodlarni yaratish va bitta warm-up chaqiruvi o'lchangan vaqtga kiritilmaydi.
- Har bir algoritm uchun takroriy o'lchovlar olinadi; o'rtacha, median, standart og'ish, minimum va maksimum qayd etiladi.
- Tub va murakkab nomzodlar natijalari alohida ko'rsatiladi; turli turdagi nomzodlarning vaqtlarini bitta guruhga aralashtirib talqin qilinmaydi.
- Benchmark natijalari apparat, Python versiyasi va tizim yuklamasiga bog'liq; ular asimptotik murakkablik isboti emas.
- Karmaykl sonlari alohida tajriba bo'lib qoladi; ularni tasodifiy semiprime to'plamining o'rniga qo'ymaslik kerak.
- Turli algoritmlarning xatolik chegaralari to'g'ridan-to'g'ri bir xil metrika deb taqdim etilmaydi.

## Cheklovlar
Ushbu loyiha o'quv va ilmiy tajriba prototipidir. U ishlab chiqarish kriptografik kalitlarini yaratish yoki standartlarga muvofiqlik sertifikati sifatida ishlatilmasligi kerak.

## Akademik manbalar

1. G. L. Miller, "Riemann's Hypothesis and Tests for Primality", *Journal of Computer and System Sciences*, 13(3), 1976, pp. 300–317.
2. R. Solovay and V. Strassen, "A Fast Monte-Carlo Test for Primality", *SIAM Journal on Computing*, 6(1), 1977, pp. 84–85.
3. M. O. Rabin, "Probabilistic Algorithm for Testing Primality", *Journal of Number Theory*, 12, 1980, pp. 128–138.
4. A. Korselt, "Sur le théorème de Fermat", *Comptes rendus de l'Académie des Sciences de Paris*, 129, 1899, pp. 438–440.
5. A. J. Menezes, P. C. van Oorschot, and S. A. Vanstone, *Handbook of Applied Cryptography*, CRC Press, 1996.
