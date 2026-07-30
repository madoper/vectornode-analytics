import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers import common, rag, analytics


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(rag.router)
    dp.include_router(analytics.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
