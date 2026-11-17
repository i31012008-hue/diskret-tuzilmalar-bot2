import io
import logging
import re
from typing import Optional

import fitz
import pytesseract
from PIL import Image, ImageOps

from app.topics import TOPICS

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    return " ".join(re.findall(r"[\w]+", text.lower(), flags=re.UNICODE))


def find_best_topic_match(query: str) -> Optional[int]:
    tokens = {word for word in normalize_text(query).split() if len(word) >= 3}
    if not tokens:
        return None

    ranked: list[tuple[int, int]] = []
    for topic_id, topic in TOPICS.items():
        topic_text = normalize_text(f"{topic['title']} {topic['summary']} {topic['answer']}")
        topic_tokens = set(topic_text.split())
        score = len(tokens & topic_tokens)
        if score:
            ranked.append((topic_id, score))
    if not ranked:
        return None
    ranked.sort(key=lambda result: result[1], reverse=True)
    return ranked[0][0]


def answer_from_text(query: str) -> str:
    topic_id = find_best_topic_match(query)
    if topic_id is None:
        return (
            "Savolni aniqroq yozing yoki mavzuni 1–14 raqami bilan tanlang.\n"
            "Mavzular: /topics"
        )
    topic = TOPICS[topic_id]
    return f"<b>{topic['title']}</b>\n\n{topic['summary']}\n\n<b>{topic['answer']}</b>"


def extract_text_from_image(image_bytes: bytes) -> str:
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            image = ImageOps.grayscale(image)
            return pytesseract.image_to_string(image, lang="uzb+eng").strip()
    except Exception:
        logger.exception("OCR image extraction failed")
        return ""


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
            # Bound resource usage on small hosting plans.
            page_text = [page.get_text() for page in list(pdf)[:20]]
        return "\n".join(page_text).strip()
    except Exception:
        logger.exception("PDF text extraction failed")
        return ""
