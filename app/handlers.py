from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings
from app.topics import TOPICS

router = Router()


def build_topics_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for topic_id in sorted(TOPICS.keys()):
        builder.button(
            text=f"{topic_id}",
            callback_data=f"topic:{topic_id}"
        )
    builder.adjust(4)
    return builder.as_markup()


@router.message(Command("start"))
async def start(message: Message) -> None:
    text = (
        "Diskret tuzilmalar botiga xush kelibsiz!\n\n"
        "Mavzularni tanlang yoki faqat mavzu raqamini yozing.\n\n"
        "Misol: 5\n"
        "Yoki /topics buyrug'ini yuboring."
    )
    await message.answer(text, reply_markup=build_topics_keyboard())


@router.message(Command("topics"))
async def topics(message: Message) -> None:
    await message.answer("Mavzular ro'yxati:", reply_markup=build_topics_keyboard())


@router.callback_query(F.data.startswith("topic:"))
async def handle_topic_callback(callback: CallbackQuery) -> None:
    topic_id = int(callback.data.split(":")[1])
    topic = TOPICS.get(topic_id)
    if not topic:
        await callback.answer("Bunday mavzu mavjud emas.")
        return

    answer = (
        f"<b>{topic['title']}</b>\n\n"
        f"<i>{topic['summary']}</i>\n\n"
        f"{topic['answer']}"
    )
    await callback.message.answer(answer)
    await callback.answer()


@router.message(F.text)
async def handle_text(message: Message) -> None:
    text = message.text.strip()
    if not text:
        return

    try:
        topic_id = int(text)
    except ValueError:
        topic_id = None

    if topic_id is not None and topic_id in TOPICS:
        topic = TOPICS[topic_id]
        answer = (
            f"<b>{topic['title']}</b>\n\n"
            f"<i>{topic['summary']}</i>\n\n"
            f"{topic['answer']}"
        )
        await message.answer(answer)
        return

    if "graf" in text.lower() or "to'plam" in text.lower() or "mantiq" in text.lower() or "diskret" in text.lower():
        await message.answer(
            "Bu mavzu haqida qisqacha tushuntirish: Diskret tuzilmalar matematik va hisoblashdagi alohida strukturalarni o'rganadi.\n\n"
            "Javob: Diskret tuzilmalar elementlari alohida, uzluksiz bo'lmagan modellarni ifodalaydi."
        )
        return

    await message.answer(
        "Mavzuni tanlang yoki mavzu raqamini yozing.\n\n"
        "Masalan: 1, 5, 10 yoki /topics"
    )


@router.message(F.photo)
async def handle_photo(message: Message) -> None:
    await message.answer(
        "Rasm yoki fayl bilan ishlash keyingi bosqichda qo'shiladi.\n\n"
        "Hozircha mavzuni tanlang yoki savolingizni matn ko'rinishida yuboring.\n"
        "Masalan: 7 yoki 'Bul algebra'"
    )


@router.message(F.document)
async def handle_document(message: Message) -> None:
    await message.answer(
        "Fayl ishlovi hozircha tayyorgarlik bosqichida.\n\n"
        "Mavzuni tanlang yoki matnli savol yuboring."
    )
