# Diskret tuzilmalar Telegram bot

Bu loyiha "Diskret tuzilmalar" faniga oid Telegram botning boshlang'ich versiyasidir. Bot foydalanuvchiga fan mavzularini ko'rsatadi, har bir mavzu bo'yicha qisqa tushuntirish beradi va yakuniy javobni alohida chiqaradi.

## Xususiyatlar
- `/start` buyrug'i bilan boshlash
- 14 ta mavzu bo'yicha menyu
- Har bir mavzu uchun qisqa va aniq tushuntirish
- Rasm/fayl yuborilganda tayyorgarlik xabarini ko'rsatish
- 24/7 ishlash uchun serverga deploy qilishga tayyorlik

## Loyiha tuzilmasi
```text
.
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ handlers.py
│  └─ topics.py
├─ .env.example
├─ .gitignore
├─ main.py
├─ requirements.txt
└─ README.md
```

## Boshlash
1. `python -m venv .venv`
2. `source .venv/bin/activate` (Linux/macOS)
3. `pip install -r requirements.txt`
4. `.env.example` dan `.env` yarating va `BOT_TOKEN` ni kiriting.
5. `python main.py`

## Bot ishlashi
- `/start` - menyu va mavzularni ko'rsatadi
- Mavzuni tanlash yoki mavzu raqamini yozish - tushuntirish beradi
- Rasm yoki fayl yuborish - "qo'shimcha OCR/fayl ishlovi qo'shilmoqda" xabarini ko'rsatadi

## Deploy
Serverga joylashtirish uchun quyidagi variantlar ishlatiladi:
- Ubuntu + systemd servizio
- Docker (keyingi versiyada)
- PM2 yoki supervisor (agar boshqa dasturlar bilan birga ishlatilsa)

## Eslatma
Tokenni GitHub repositoriga joylamang. Uni serverdagi `.env` faylida saqlang.
