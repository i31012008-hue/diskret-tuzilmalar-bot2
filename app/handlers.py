import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.topics import TOPICS

router = Router()
logger = logging.getLogger(__name__)


def build_topics_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for topic_id, topic in TOPICS.items():
        builder.button(text=f"{topic_id}. {topic['title'][:45]}", callback_data=f"topic:{topic_id}")
    builder.adjust(1)
    return builder.as_markup()


def format_topic(topic_id: int) -> str:
    topic = TOPICS[topic_id]
    return (
        f"<b>{topic['title']}</b>\n\n"
        f"{topic['summary']}\n\n"
        f"<b>{topic['answer']}</b>"
    )


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Assalomu alaykum! Bu bot Diskret tuzilmalar fanini o'rganishga yordam beradi.\n\n"
        "Mavzuni quyidagi tugmalardan tanlang yoki /topics buyrug'ini yuboring. "
        "Masala matnini yuborsangiz, hozircha mavzu tanlash bo'yicha yo'l-yo'riq beraman.",
        reply_markup=build_topics_keyboard(),
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "Buyruqlar:\n"
        "/start — botni boshlash\n"
        "/topics — mavzular ro'yxati\n"
        "/help — yordam\n\n"
        "Mavzuni raqami yoki menyudagi tugma orqali tanlang."
    )


@router.message(Command("topics"))
async def topics_command(message: Message) -> None:
    await message.answer("Diskret tuzilmalar mavzulari:", reply_markup=build_topics_keyboard())


@router.callback_query(F.data.startswith("topic:"))
async def topic_callback(callback: CallbackQuery) -> None:
    try:
        topic_id = int((callback.data or "").split(":", maxsplit=1)[1])
    except (IndexError, ValueError):
        await callback.answer("Mavzu raqami noto'g'ri.", show_alert=True)
        return

    if topic_id not in TOPICS:
        await callback.answer("Bunday mavzu mavjud emas.", show_alert=True)
        return

    if callback.message:
        await callback.message.answer(format_topic(topic_id), reply_markup=build_topics_keyboard())
    await callback.answer()


@router.message(F.photo)
async def photo_message(message: Message) -> None:
    await message.answer(
        "Rasm qabul qilindi, lekin hozircha rasm ichidagi matnni avtomatik o'qish (OCR) yoqilmagan.\n"
        "Masalani matn qilib yuboring yoki mavzuni /topics orqali tanlang."
    )


@router.message(F.document)
async def document_message(message: Message) -> None:
    await message.answer(
        "Fayl qabul qilindi, ammo hozircha PDF/fayl ichidagi matnni o'qish yoqilmagan.\n"
        "Masala matnini xabarda yuboring yoki mavzuni /topics orqali tanlang."
    )


@router.message(F.text)
async def text_message(message: Message) -> None:
    text = (message.text or "").strip()
    if text.isdecimal():
        topic_id = int(text)
        if topic_id in TOPICS:
            await message.answer(format_topic(topic_id), reply_markup=build_topics_keyboard())
            return

    await message.answer(
        "Mavzuni menyudan tanlang yoki raqamini yuboring (1–14).\n"
        "Mavzular uchun /topics buyrug'ini yuboring."
    )


@router.errors()
async def handle_unexpected_error(event, exception: Exception) -> bool:
    logger.exception("Xabarni qayta ishlashda kutilmagan xatolik", exc_info=exception)
    update = getattr(event, "update", None)
    message = getattr(update, "message", None)
    if message:
        await message.answer("Xatolik yuz berdi. Iltimos, birozdan keyin qayta urinib ko'ring.")
    return True
