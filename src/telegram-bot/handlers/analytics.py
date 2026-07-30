from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.formatters import (
    company_card, signals_card, top_risk_list,
    groups_list, recent_list, compare_card,
)
from services.gateway import GatewayClient

router = Router()
gw = GatewayClient()


@router.message(Command("company"))
async def cmd_company(message: Message):
    args = message.text.removeprefix("/company").strip()
    if not args:
        await message.answer("Укажите ИНН: `/company 7707083893`", parse_mode="Markdown")
        return
    inn = args.split()[0]
    try:
        data = await gw.get_company(inn)
        if not data:
            await message.answer(f"Компания с ИНН `{inn}` не найдена", parse_mode="Markdown")
            return
        await message.answer(company_card(data), parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@router.message(Command("signal"))
async def cmd_signal(message: Message):
    args = message.text.removeprefix("/signal").strip()
    if not args:
        await message.answer("Укажите ИНН: `/signal 7707083893`", parse_mode="Markdown")
        return
    inn = args.split()[0]
    try:
        data = await gw.get_signals(inn)
        if not data:
            await message.answer(f"Компания с ИНН `{inn}` не найдена", parse_mode="Markdown")
            return
        await message.answer(signals_card(data), parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@router.message(Command("top"))
async def cmd_top(message: Message):
    try:
        companies = await gw.top_risk()
        await message.answer(top_risk_list(companies), parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@router.message(Command("groups"))
async def cmd_groups(message: Message):
    try:
        groups = await gw.top_groups()
        await message.answer(groups_list(groups), parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@router.message(Command("new"))
async def cmd_new(message: Message):
    try:
        anomalies = await gw.recent_anomalies()
        if not anomalies:
            await message.answer("Новых аномалий за неделю нет")
            return
        await message.answer(recent_list(anomalies), parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@router.message(Command("compare"))
async def cmd_compare(message: Message):
    args = message.text.removeprefix("/compare").strip().split()
    if len(args) < 2:
        await message.answer("Укажите два ИНН: `/compare 7707083893 7712345678`", parse_mode="Markdown")
        return
    inn1, inn2 = args[0], args[1]
    try:
        data = await gw.compare_companies(inn1, inn2)
        await message.answer(compare_card(data), parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
