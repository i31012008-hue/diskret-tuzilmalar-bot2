# Diskret tuzilmalar Telegram bot

Python va aiogram asosidagi Telegram bot. Hozirgi versiya fan bo'yicha 14 ta mavzu menyusini beradi; mavzuni tanlaganda qisqa tushuntirish va yakuniy javob ko'rsatiladi.

## Hozirgi imkoniyatlar
- `/start`, `/topics`, `/help` buyruqlari
- 14 ta mavzu uchun menyu va raqam bilan tanlash
- Rasm va hujjat kelganda OCR hali yoqilmaganini aniq bildiradi
- Polling rejimida ishlaydi; systemd orqali server qayta ishga tushganda avtomatik ishga tushirish mumkin

> Eslatma: hozirgi versiya foydalanuvchi yuborgan erkin masalani avtomatik yechmaydi va rasm/PDF ichidagi matnni OCR bilan ajratmaydi. Buning uchun alohida OCR hamda yechish xizmati keyin qo'shiladi.

## Mahalliy ishga tushirish
Talab: Python 3.11 yoki undan yangi.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` faylida `BOT_TOKEN` qiymatini o'zingizning Telegram tokeningiz bilan almashtiring, so'ng:

```bash
python main.py
```

Windows PowerShell uchun virtual muhitni faollashtirish: `.venv\\Scripts\\Activate.ps1`.

## Ubuntu serverga o'rnatish (24/7)
Quyidagi misolda loyiha `/opt/diskret-tuzilmalar-bot` ichiga olinadi. Serverda Python 3.11+, `git`, `python3-venv` o'rnatilgan bo'lishi kerak.

```bash
sudo mkdir -p /opt/diskret-tuzilmalar-bot
sudo chown "$USER":"$USER" /opt/diskret-tuzilmalar-bot
git clone https://github.com/i31012008-hue/diskret-tuzilmalar-bot2.git /opt/diskret-tuzilmalar-bot
cd /opt/diskret-tuzilmalar-bot
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
nano .env
chmod 600 .env
```

`.env` ichida haqiqiy tokenni kiriting. Tokenni GitHub-ga commit qilmang va chatda ulashmang.

Systemd unit namunasini o'rnating va ichidagi `User` hamda `WorkingDirectory` qiymatlarini tekshiring:

```bash
sudo cp deploy/diskret-bot.service.example /etc/systemd/system/diskret-bot.service
sudo nano /etc/systemd/system/diskret-bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now diskret-bot
sudo systemctl status diskret-bot
```

Loglarni ko'rish:

```bash
sudo journalctl -u diskret-bot -f
```

Kod шинэчлэсний дараа:

```bash
cd /opt/diskret-tuzilmalar-bot
git pull
.venv/bin/pip install -r requirements.txt
sudo systemctl restart diskret-bot
```

## Muhim
- Bir token bilan bir vaqtning o'zida faqat bitta polling jarayoni ishlasin. Eski bot jarayoni yoki webhook ishlayotgan bo'lsa, polling bilan to'qnashishi mumkin.
- `.env` maxfiy: repoga yubormang. Agar token oshkor bo'lib qolsa, BotFather orqali yangilang.
- Systemd unit `deploy/diskret-bot.service.example` ichida. Uni server foydalanuvchisi va loyiha yo'liga moslang.
