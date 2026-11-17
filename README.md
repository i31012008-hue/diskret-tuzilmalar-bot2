# Diskret tuzilmalar Telegram bot

Python/aiogram Telegram boti: 14 ta fan mavzusi, qisqa tushuntirishlar, rasm OCR va PDF matnini o'qish. Railway uchun Dockerfile ham bor; u Tesseract OCR dasturini ham o'rnatadi.

## Railway sozlash
1. Railway'da shu GitHub repository va `main` branchni deploy qiling. Root Directory bo'sh qolsin.
2. Service → Variables bo'limida `BOT_TOKEN` nomli variable yarating va BotFather'dan olingan **yangilangan** tokenni value sifatida kiriting. Tokenni kod, GitHub yoki chatga qo'ymang.
3. Root Directory-д `Dockerfile` ba `railway.toml` borligini tekshiring. Build tugagach deploy loglarini kuzating.
4. Telegram'da botga `/start` yuboring.

Bu bot polling ishlatadi, shuning uchun Railway'da web port talab qilinmaydi. Bitta token uchun faqat bitta running instance bo'lsin.

## Lokal ishga tushirish
Talab: Python 3.11+ va Tesseract OCR (uzb, eng til paketlari bilan).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` файлига tokenni kiriting va ishga tushiring:

```bash
python main.py
```

## Muhim
- Token oshkor bo'lgan bo'lsa, BotFather'da revoke qilib yangisini yarating. Yangi tokenni faqat Railway Variables'ga kiriting.
- Rasm/PDF OCR matnni ajratadi va mavjud 14 ta mavzuga mos javob topishga urinadi; murakkab masalani mustaqil to'liq yechadigan AI emas.
- Skanlangan PDF sahifalarida ichki matn bo'lmasligi mumkin; bunday holatda sahifani rasm qilib yuboring.
