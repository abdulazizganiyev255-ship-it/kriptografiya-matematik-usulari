# PrimeGuard — foydalanuvchi qo'llanmasi

## 1. Dasturni ishga tushirish

Windows PowerShell'da loyiha papkasiga kiring va quyidagini bajaring:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\start_primeguard.ps1
```

Skript virtual muhit yaratadi, kutubxonalarni o'rnatadi, testlarni bajaradi va Streamlit dasturini ishga tushiradi. Testlar yiqilsa, dastur avtomatik ravishda ishga tushmaydi.

## 2. Sonni tekshirish

1. **Sonni tekshirish** sahifasini oching.
2. Tekshirmoqchi bo'lgan natural sonni kiriting. Raqamlar orasida bo'sh joy yoki pastki chiziq ishlatish mumkin.
3. Chap paneldagi **Raundlar soni (k)** qiymatini tanlang.
4. **Sonni tekshirish** tugmasini bosing.
5. Fermat, Solovay–Strassen va Miller–Rabin natijalarini yonma-yon ko'ring.
6. Har bir algoritmning tekshiruv bosqichlarini ochib, tanlangan asos va hisoblangan qiymatlarni o'rganing.
7. Natijani CSV yoki JSON formatida yuklab oling.

### Natijalarni qanday tushunish kerak?

- **Aniq tub:** son kichik tub sonlar jadvali orqali tekshirilgan.
- **Ehtimoliy tub:** algoritm tanlangan raundlarda murakkablik guvohini topmagan. Bu matematik isbot emas.
- **Aniq murakkab:** kamida bitta algoritm murakkablik guvohini topgan yoki son kichik bo'luvchi bilan aniqlangan.

Miller–Rabin uchun standart nazariy yuqori chegara har bir mustaqil raundda (1/4), demak k raund uchun (4^{-k}). Solovay–Strassen uchun (2^{-k}). Fermat testida Karmaykl sonlari sabab universal foydali chegara mavjud emas.

## 3. Karmaykl tahlili

1. **Karmaykl tahlili** bo'limini oching.
2. Ro'yxatdan mashhur sonni tanlang yoki o'zingiz son kiriting.
3. Tahlil tugmasini bosing.
4. Fermat testining Karmaykl sonlarida qanday aldanishini, Solovay–Strassen va Miller–Rabin natijalarini ko'ring.
5. Korselt mezoni va faktorizatsiya tafsilotlarini oching.

Faktorizatsiya hisoblash limiti bilan cheklangan. Limit tugasa, dastur noto'g'ri yakuniy xulosa bermasdan tekshiruv to'liq emasligini ko'rsatadi.

## 4. Algoritmlar tezligini taqqoslash

1. **Tezlik taqqoslash** bo'limiga o'ting.
2. Son uzunliklarini tanlang. Dastlab 64–512 bit bilan boshlash tavsiya etiladi.
3. Raundlar va takrorlashlar sonini belgilang.
4. Sinovni boshlang.
5. Grafiklar, jadval va CSV natijalarini ko'ring.

Benchmark har bir tanlangan bit uzunligida tub nomzod va murakkab semiprime nomzodini alohida tekshiradi. Nomzod yaratish va warm-up o'lchovga kiritilmaydi. Jadvalda o'rtacha, median, standart og'ish, minimum va maksimum vaqtlar beriladi. Katta bit uzunliklari va ko'p takrorlashlar ko'proq vaqt talab qiladi. Natijalar kompyuter, Python versiyasi va tizim yuklamasiga bog'liq; ular matematik murakkablik isboti emas.

## 5. RSA uchun o'quv parametrlari

1. **RSA parametrlari** bo'limiga o'ting.
2. N modulining maqsadli bit uzunligini tanlang.
3. Miller–Rabin raundlari sonini belgilang.
4. p, q, N va φ(N) qiymatlarini yarating.
5. JSON hisobotini yuklab oling.

**Muhim:** bu o'quv moduli. U to'liq RSA kalit juftligini, e va d eksponentlarini yaratmaydi va ishlab chiqarish muhitida foydalanish uchun mo'ljallanmagan. p va q ham ehtimoliy tub son sifatida tekshiriladi.

## 6. Tavsiya etilgan namoyish ssenariysi

Universitet himoyasida quyidagi tartibdan foydalanish mumkin:

1. 127-bit Mersenne tub sonini tekshirish.
2. 8911 Karmaykl sonini tahlil qilish.
3. Uch algoritmning vaqtini 64, 128, 256 va 512 bitda taqqoslash.
4. RSA o'quv modulida 1024 yoki 2048 bitli N parametrlarini yaratish.
5. CSV/JSON hisobotini ko'rsatish.

## 7. Cheklovlar

- Ehtimoliy tublik testlari katta sonlar uchun matematik isbot o'rnini bosmaydi.
- Deterministik Miller–Rabin etaloni faqat (n < 2^{64}) uchun kafolatlangan.
- Benchmark natijalari apparat va tizim sharoitlariga bog'liq.
- Loyiha akademik prototip bo'lib, sertifikatlangan kriptografik kutubxona emas.
