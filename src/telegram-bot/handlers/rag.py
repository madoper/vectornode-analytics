from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.formatters import answer_text
from services.gateway import GatewayClient

router = Router()
gw = GatewayClient()


@router.message(Command("ask"))
async def cmd_ask(message: Message):
    query = message.text.removeprefix("/ask").strip()
    if not query:
        await message.answer("Укажите вопрос после /ask\nНапример: `/ask Выплата дивидендов при убытках`", parse_mode="Markdown")
        return

    await message.answer("🔍 Ищу в нормативной базе...")
    try:
        data = await gw.ask(query)
        text = answer_text(data)
        if len(text) > 4000:
            text = text[:4000] + "..."
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
