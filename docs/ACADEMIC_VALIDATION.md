# PrimeGuard: akademik validatsiya protokoli

## Maqsad
Uch ehtimoliy tublik testini (Fermat, Solovay–Strassen, Miller–Rabin) bir xil sinov sharoitida solishtirish va ularning xulosalarini mustaqil etalon tekshiruv bilan baholash.

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

## Mustaqil etalon
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
- Har bir bit uzunligi uchun bir xil nomzod sonni uch algoritmda tekshirish.
- Har bir tajriba uchun algoritm, bit uzunligi, raundlar, asoslar tanlash usuli va vaqtni yozish.
- Warm-up va takroriy tajribalarni ajratish; medianani ham ko'rsatish.
- Tub nomzodlar bilan birga murakkab va pseudoprime to'plamlarida aniqlash samaradorligini alohida o'lchash.
- Turli algoritmlarning xatolik chegaralarini to'g'ridan-to'g'ri bir xil metrika deb taqdim etmaslik.

## Cheklovlar
Ushbu loyiha o'quv va ilmiy tajriba prototipidir. U ishlab chiqarish kriptografik kalitlarini yaratish yoki standartlarga muvofiqlik sertifikati sifatida ishlatilmasligi kerak.