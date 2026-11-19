# PrimeGuard v2 — React + TypeScript + Python API

## Maqsad

Bu — ehtimoliy tublik tekshirish bo‘yicha PrimeGuard loyihasining yangi interfeysidir. Dizayn zamonaviy, ammo matematik kod **almashtirilmagan**: API mavjud `core/` va `analytics/` funksiyalarini chaqiradi.

**Loyiha chegarasi:** asosiy bo‘limlar faqat «Sonni tekshirish» va «Algoritmlarni taqqoslash». Karmaykl tajribasi sonni tekshirish ichidagi o‘quv panelidir. RSA qo‘shilmagan.

## Texnologiyalar

- **React 19 + TypeScript + Vite** — komponentlar, tekshiruv va navigatsiya.
- **CSS** — tema, responsiv ekran, semantic ranglar, fokus va animatsiyani kamaytirish.
- **Recharts** — bajarilish vaqti va benchmark diagrammalari.
- **KaTeX** — Python matematik modul qaytargan formulalarni o‘qilishi qulay ko‘rsatish.
- **FastAPI (Python)** — REST API, validatsiya va matematika yadro bilan integratsiya.
- **Pytest + TypeScript compiler + Vite build** — regressiya va build nazorati.

## Windows PowerShell: ishlab chiqish

Loyihani asosiy repozitoriydan yangilang. Avval `git status --short` natijasi bo‘shligiga ishonch hosil qiling.

```powershell
cd "$HOME\Projects\PrimeGuard"
git pull --ff-only origin main

& "$HOME\PrimeGuardVenv\Scripts\python.exe" -m pip install -r web-requirements.txt

cd frontend
npm install
npm run build
```

Ikkita **alohida PowerShell oynasi** oching.

Birinchi terminal (Python API):

```powershell
cd "$HOME\Projects\PrimeGuard"
& "$HOME\PrimeGuardVenv\Scripts\python.exe" -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Ikkinchi terminal (React):

```powershell
cd "$HOME\Projects\PrimeGuard\frontend"
npm run dev
```

Brauzer: **http://127.0.0.1:5173**. API salomatligi: **http://127.0.0.1:8000/api/health**.

Agar Windows kompyuteringizda Node.js/npm o‘rnatilmagan bo‘lsa, LTS versiyasini o‘rnating. Matematika yadro dastlabki Streamlit ko‘rinishida ham mavjud qoladi (`streamlit run app.py`).

## API shartnomasi

| Method va URL | Body | Natija |
|---|---|---|
| GET `/api/health` | — | Holat |
| POST `/api/check` | `{"n":"561","k":20}` | Uch algoritm, aniq/ehtimoliy xulosa, haqiqiy raund loglari |
| POST `/api/trace` | `{"n":"561","algorithm":"Miller-Rabin","log":{...}}` | Asl logdagi asos bilan qadamlarni qayta hisoblash |
| POST `/api/carmichael` | `{"n":"561","k":20}` | Korselt mezoni, faktorlar, uch algoritm |
| POST `/api/benchmark` | `{"bit_sizes":[64,128],"k":20,"trials":10}` | Haqiqiy vaqt statistikasi |

**Juda katta sonlar:** API `n` va `witness_a` ni **o‘nlik matn** sifatida uzatadi. Sabab: JavaScript `Number` turi 53 bitdan katta butun sonlarni aniq saqlamaydi. Formula va tekshiruvlarni Python bajaradi. `n` ko‘pi bilan 2048 ta raqam; `k` 1–64. Benchmark resurslari ataylab cheklangan: 3 ta bit uzunligidan ortiq emas, 64–512 bit, 3–12 takrorlash.

Natijalar oldindan uydirilmaydi. Foydalanuvchi `Tekshirishni boshlash` tugmasini bosganda API’dan haqiqiy javob keladi.

## Test va tasdiqlash

```powershell
cd "$HOME\Projects\PrimeGuard"
& "$HOME\PrimeGuardVenv\Scripts\python.exe" -m pytest -q
cd frontend
npm run build
```

**Muhim:** avtomatik test va build vizual UI brauzerda to‘g‘ri ko‘ringanini to‘liq isbotlamaydi. Windows Chrome/Edge’da 1440px, 1366px va 390px kenglikda, 100% va 125% masshtabda tekshiriladi.

## Arxitektura

```text
React + TypeScript (frontend/src)
      │ JSON /api  (Vite proxy in dev)
      ▼
FastAPI (api/main.py)
      │ calls existing functions; no duplicated primality formulas
      ▼
core/fermat.py, core/solovay_strassen.py, core/miller_rabin.py
analytics/round_explainer.py, analytics/carmichael.py, analytics/benchmark.py
```

## Deploy va xavfsizlik

Ishlab chiqish rejimida API `127.0.0.1:8000` orqali ochiladi; keng ommaga chiqarish uchun reverse proxy, HTTPS, rate limit va hisoblash vaqtiga limit qo‘shish shart. `VITE_API_BASE_URL` alohida host uchun sozlanadi. **Bu MVP o‘quv prototipi; xizmat xavfsizligi auditi yoki production deployment hali bajarilmagan.**
