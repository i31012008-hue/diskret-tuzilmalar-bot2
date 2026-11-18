import io
import logging
import re
from typing import Optional

from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import fitz
import pytesseract

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("\n", " ")
    text = re.sub(r"[^\w\s\+\-\*\(\)\[\]\{\}\|/&=><^~!%.,:;]+", " ", text)
    return " ".join(text.split())


def find_best_topic_match(query: str) -> Optional[int]:
    if not query:
        return None

    from app.topics import TOPICS

    query_norm = normalize_text(query)
    tokens = set(word for word in query_norm.split() if len(word) >= 3)
    if not tokens:
        return None

    ranked: list[tuple[int, int]] = []
    for topic_id, topic in TOPICS.items():
        topic_text = normalize_text(f"{topic['title']} {topic['summary']} {topic['answer']}")
        topic_tokens = set(word for word in topic_text.split() if len(word) >= 3)
        score = len(tokens & topic_tokens)
        if score > 0:
            ranked.append((topic_id, score))

    if not ranked:
        return None

    ranked.sort(key=lambda item: item[1], reverse=True)
    return ranked[0][0]


def answer_from_text(query: str) -> str:
    from app.logic_solver import LogicSyntaxError, solve_expression, solve_logic_text
    from app.topics import TOPICS

    answers = solve_logic_text(query)
    if not answers:
        try:
            answers = [solve_expression(query)]
        except LogicSyntaxError:
            answers = []
    if answers:
        return "\n\n".join(answers)

    topic_id = find_best_topic_match(query)
    if topic_id is None:
        return (
            "Mavzu tanlang yoki raqamini yuboring (1-14).\n\n"
            "Masalan: /topics yoki 5\n"
            "Mantiqiy formula yuborsangiz, rostlik jadvali tuziladi. Masalan: A -> B"
        )

    topic = TOPICS[topic_id]
    return (
        f"<b>{topic['title']}</b>\n\n"
        f"{topic['summary']}\n\n"
        f"<b>{topic['answer']}</b>"
    )


def extract_text_from_image(image_bytes: bytes) -> str:
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            image = ImageOps.grayscale(image)
            image = ImageOps.autocontrast(image)
            image = ImageEnhance.Contrast(image).enhance(1.8)
            image = image.filter(ImageFilter.SHARPEN)
            if image.width < 1800:
                scale = 1800 / image.width
                image = image.resize((1800, max(1, int(image.height * scale))))
            recognized = pytesseract.image_to_string(image, lang="uzb+eng", config="--psm 6")
            return recognized.strip()
    except Exception:
        logger.exception("Image OCR failed")
        return ""


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
            pages = [page.get_text() for page in pdf[:20]]
        return "\n".join(pages).strip()
    except Exception:
        logger.exception("PDF OCR failed")
        return ""
