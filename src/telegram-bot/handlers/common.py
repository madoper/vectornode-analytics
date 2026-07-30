from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🤖 *VectorNode Аналитика* — AI-ассистент по финансовым рискам\n\n"
        "📋 *Аналитика ФНС:*\n"
        "/company <ИНН> — карточка компании\n"
        "/top — топ риск-компаний\n"
        "/signal <ИНН> — карта гипотез H1–H6\n"
        "/groups — топ групп риска\n"
        "/new — новые аномалии\n"
        "/compare <ИНН1> <ИНН2> — сравнение\n\n"
        "📖 *RAG-вопросы к нормативной базе:*\n"
        "/ask <вопрос> — задать вопрос\n\n"
        "/help — справка",
        parse_mode="Markdown",
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "*Справка по командам*\n\n"
        "`/ask Дивиденды при убытках` — AI проанализирует нормативную базу\n"
        "`/company 7707083893` — финансы, риски, гипотезы\n"
        "`/signal 7707083893` — детальная карта H1–H6\n"
        "`/top` — топ-10 компаний по уровню риска\n"
        "`/groups` — топ-5 групп риска\n"
        "`/new` — аномалии за последнюю неделю\n"
        "`/compare 7707083893 7712345678` — сравнение двух компаний",
        parse_mode="Markdown",
    )
