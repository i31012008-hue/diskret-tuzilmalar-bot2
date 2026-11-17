import logging
from typing import Dict, Optional

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover
    fitz = None

try:
    import pytesseract
    from PIL import Image
except Exception:  # pragma: no cover
    pytesseract = None
    Image = None


logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    return " ".join(text.lower().replace("\n", " ").split())


def find_best_topic_match(query: str) -> Optional[int]:
    if not query:
        return None

    from app.topics import TOPICS

    query_norm = normalize_text(query)
    ranked: list[tuple[int, int]] = []

    for topic_id, topic in TOPICS.items():
        haystack = normalize_text(f"{topic['title']} {topic['summary']} {topic['answer']}")
        score = 0
        for keyword in query_norm.split():
            if len(keyword) < 3:
                continue
            if keyword in haystack:
                score += 2
        if query_norm in haystack:
            score += 5
        if score > 0:
            ranked.append((topic_id, score))

    if not ranked:
        return None

    ranked.sort(key=lambda item: item[1], reverse=True)
    return ranked[0][0]


def answer_from_text(query: str) -> str:
    from app.topics import TOPICS

    topic_id = find_best_topic_match(query)
    if topic_id is None:
        return (
            "Mavzu tanlang yoki raqamini yuboring (1-14).\n\n"
            "Masalan: /topics yoki 5"
        )

    topic = TOPICS[topic_id]
    return (
        f"<b>{topic['title']}</b>\n\n"
        f"{topic['summary']}\n\n"
        f"<b>{topic['answer']}</b>"
    )


def extract_text_from_image(image_bytes: bytes) -> str:
    if pytesseract is None or Image is None:
        return ""

    try:
        image = Image.open(__import__('io').BytesIO(image_bytes))
        text = pytesseract.image_to_string(image, lang="uzb+eng")
        return (text or "").strip()
    except Exception as exc:  # pragma: no cover
        logger.exception("OCR image read failed: %s", exc)
        return ""


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    if fitz is None:
        return ""

    try:
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages: list[str] = []
        for page in pdf:
            pages.append(page.get_text())
        return "\n".join(pages).strip()
    except Exception as exc:  # pragma: no cover
        logger.exception("PDF text extraction failed: %s", exc)
        return ""
