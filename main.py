from aiogram import Bot, Dispatcher
import asyncio

from app.config import settings
from app.handlers import router


async def main() -> None:
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
