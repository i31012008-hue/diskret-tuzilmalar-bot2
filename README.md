# Diskret tuzilmalar Telegram bot

Python/aiogram bot: fan bo'yicha 14 mavzu, rasm/PDF OCR va mantiqiy formulalar uchun rostlik jadvali.

## Railway
- GitHub repository va `main` branchni deploy qiling; root directory bo'sh qolsin.
- Service → Variables ichida `BOT_TOKEN` nomli secret/environment variable yarating.
- Bot polling rejimida ishlaydi, web port shart emas. Bitta token uchun faqat bitta running instance bo'lsin.
- Railway build Dockerfile orqali Tesseract OCR va Python paketlarini o'rnatadi.

## Lokal ishga tushirish
Python 3.11+ va Tesseract kerak:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```
`.env` ichiga `BOT_TOKEN=...` kiriting. Haqiqiy tokenni GitHub yoki chatga yozmang.

Mantiqiy ifodalar uchun `A&(B -> ¬C)` ko'rinishidagi formulani yuboring yoki topshiriq rasmini bering. Bot A–D o'zgaruvchilar uchun rostlik jadvalini tuzadi. OCR aniqligi surat tiniqligi va formulalarning to'g'ri tanilishiga bog'liq; javobni tekshirib chiqing.
