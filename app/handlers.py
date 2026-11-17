from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.ocr_utils import answer_from_text, extract_text_from_image, extract_text_from_pdf
from app.topics import TOPICS

router = Router()


def build_topics_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for topic_id in sorted(TOPICS.keys()):
        builder.button(text=f"{topic_id}", callback_data=f"topic:{topic_id}")
    builder.adjust(4)
    return builder.as_markup()


@router.message(Command("start"))
async def start(message: Message) -> None:
    text = (
        "Diskret tuzilmalar botiga xush kelibsiz!\n\n"
        "Mavzuni tanlang yoki raqamini yozing.\n\n"
        "Masalan: 8\n"
        "Yoki /topics buyrug'ini yuboring."
    )
    await message.answer(text, reply_markup=build_topics_keyboard())


@router.message(Command("topics"))
async def topics(message: Message) -> None:
    await message.answer("Mavzular ro'yxati:", reply_markup=build_topics_keyboard())


@router.callback_query(F.data.startswith("topic:"))
async def handle_topic_callback(callback: CallbackQuery) -> None:
    topic_id = int(callback.data.split(":", 1)[1])
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


@router.message(F.photo)
async def handle_photo(message: Message) -> None:
    try:
        file = await message.bot.get_file(message.photo[-1].file_id)
        image_bytes = await message.bot.download_file(file.file_path)
        text = extract_text_from_image(image_bytes)
        if not text:
            await message.answer("Rasmdan matn o'qib bo'lmadi. Savolni matnli yuboring yoki mavzuni tanlang.")
            return
        await message.answer(answer_from_text(text))
    except Exception:
        await message.answer("Rasmni o'qish vaqtida xatolik yuz berdi. Savolni matnli yuboring.")


@router.message(F.document)
async def handle_document(message: Message) -> None:
    doc = message.document
    if not doc or not (doc.file_name or "").lower().endswith(".pdf"):
        await message.answer("Hozircha faqat PDF fayllar ishlaydi. Mavzuni tanlang yoki matnli savol yuboring.")
        return
    try:
        file = await message.bot.get_file(doc.file_id)
        pdf_bytes = await message.bot.download_file(file.file_path)
        text = extract_text_from_pdf(pdf_bytes)
        if not text:
            await message.answer("PDFdan matn o'qib bo'lmadi. Mavzuni tanlang yoki matnli savol yuboring.")
            return
        await message.answer(answer_from_text(text))
    except Exception:
        await message.answer("PDFni o'qishda xatolik yuz berdi. Mavzuni tanlang yoki matnli savol yuboring.")


@router.message(F.text)
async def handle_text(message: Message) -> None:
    text = (message.text or "").strip()
    if not text:
        return

    if text.isdigit() and int(text) in TOPICS:
        topic = TOPICS[int(text)]
        await message.answer(
            f"<b>{topic['title']}</b>\n\n"
            f"<i>{topic['summary']}</i>\n\n"
            f"{topic['answer']}"
        )
        return

    await message.answer(answer_from_text(text))
