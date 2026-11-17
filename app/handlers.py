import asyncio
import io
import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.logic_solver import solve_logic_text
from app.ocr_utils import answer_from_text, extract_text_from_image, extract_text_from_pdf
from app.topics import TOPICS

router = Router()
logger = logging.getLogger(__name__)
MAX_DOCUMENT_BYTES = 15 * 1024 * 1024


def build_topics_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for topic_id, topic in TOPICS.items():
        builder.button(text=f"{topic_id}. {topic['title'][:45]}", callback_data=f"topic:{topic_id}")
    builder.adjust(1)
    return builder.as_markup()


def format_topic(topic_id: int) -> str:
    topic = TOPICS[topic_id]
    return f"<b>{topic['title']}</b>\n\n{topic['summary']}\n\n<b>{topic['answer']}</b>"


async def respond_to_recognized_text(message: Message, text: str) -> None:
    solved = solve_logic_text(text)
    if solved:
        await message.answer(f"Topilgan mantiqiy ifodalar: {len(solved)} ta. Har biri uchun rostlik jadvali:")
        for answer in solved:
            await message.answer(answer)
        return
    await message.answer(answer_from_text(text))


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Assalomu alaykum! Bu bot Diskret tuzilmalar fanini o'rganishga yordam beradi.\n\n"
        "Mavzuni menyudan tanlang yoki mantiqiy masala, rasm/PDF yuboring. "
        "Mantiqiy ifodalar uchun bot rostlik jadvalini tuzadi.",
        reply_markup=build_topics_keyboard(),
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer("/start — boshlash\n/topics — mavzular\n/help — yordam")


@router.message(Command("topics"))
async def topics_command(message: Message) -> None:
    await message.answer("Mavzular:", reply_markup=build_topics_keyboard())


@router.callback_query(F.data.startswith("topic:"))
async def topic_callback(callback: CallbackQuery) -> None:
    try:
        topic_id = int((callback.data or "").split(":", maxsplit=1)[1])
    except (IndexError, ValueError):
        await callback.answer("Mavzu raqami noto'g'ri.", show_alert=True)
        return
    if topic_id not in TOPICS:
        await callback.answer("Bunday mavzu yo'q.", show_alert=True)
        return
    if callback.message:
        await callback.message.answer(format_topic(topic_id), reply_markup=build_topics_keyboard())
    await callback.answer()


@router.message(F.photo)
async def photo_message(message: Message) -> None:
    await message.answer("Rasm o'qilmoqda, biroz kuting...")
    try:
        telegram_file = await message.bot.get_file(message.photo[-1].file_id)
        if not telegram_file.file_path:
            raise ValueError("Telegram file path is empty")
        buffer = io.BytesIO()
        await message.bot.download_file(telegram_file.file_path, destination=buffer)
        extracted = await asyncio.to_thread(extract_text_from_image, buffer.getvalue())
    except Exception:
        logger.exception("Rasmni yuklash yoki OCR qilishda xatolik")
        await message.answer("Rasmni o'qishda xatolik bo'ldi. Savolni matn shaklida yuboring.")
        return

    if not extracted:
        await message.answer("Rasmdan matn topilmadi. Rasmni tiniqroq yuboring yoki savolni matn qiling.")
        return
    await respond_to_recognized_text(message, extracted)


@router.message(F.document)
async def document_message(message: Message) -> None:
    document = message.document
    if document is None:
        return
    if document.file_size and document.file_size > MAX_DOCUMENT_BYTES:
        await message.answer("Fayl juda katta. 15 MB dan kichik PDF yuboring.")
        return
    if not (document.file_name or "").lower().endswith(".pdf"):
        await message.answer("Hozircha faqat PDF hujjatlar qo'llab-quvvatlanadi.")
        return

    await message.answer("PDF o'qilmoqda, biroz kuting...")
    try:
        telegram_file = await message.bot.get_file(document.file_id)
        if not telegram_file.file_path:
            raise ValueError("Telegram file path is empty")
        buffer = io.BytesIO()
        await message.bot.download_file(telegram_file.file_path, destination=buffer)
        extracted = await asyncio.to_thread(extract_text_from_pdf, buffer.getvalue())
    except Exception:
        logger.exception("PDF yuklash yoki o'qishda xatolik")
        await message.answer("PDFni o'qishda xatolik bo'ldi. Matnli savol yuboring.")
        return

    if not extracted:
        await message.answer("PDFdan matn olinmadi. Skan qilingan PDF sahifasini rasm qilib yuboring.")
        return
    await respond_to_recognized_text(message, extracted)


@router.message(F.text)
async def text_message(message: Message) -> None:
    text = (message.text or "").strip()
    if text.isdecimal() and int(text) in TOPICS:
        await message.answer(format_topic(int(text)), reply_markup=build_topics_keyboard())
        return
    solved = solve_logic_text(text)
    if solved:
        for answer in solved:
            await message.answer(answer)
        return
    await message.answer(answer_from_text(text))
