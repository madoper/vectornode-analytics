import io

from pypdf import PdfReader


def parse_pdf(raw_bytes: bytes, min_fragment_len: int = 50) -> list[str]:
    reader = PdfReader(io.BytesIO(raw_bytes))
    fragments = []
    for page in reader.pages:
        text = page.extract_text()
        if not text:
            continue
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) >= min_fragment_len]
        fragments.extend(paragraphs)
    return fragments


NOISE_RU = {"в", "на", "с", "по", "из", "от", "для", "что", "как", "это", "так", "был", "его", "или", "еще", "уже", "там", "при", "под", "без", "над", "кто"}


def filter_noise(text: str, min_ratio: float = 0.2) -> bool:
    words = text.split()
    if len(words) < 5:
        return False
    significant = sum(1 for w in words if w.lower() not in NOISE_RU)
    return (significant / max(len(words), 1)) >= min_ratio


NEW_SOURCES = [
    {"domain": "nalog.gov.ru", "name": "ФНС России", "priority": "high", "selector": ".content, #article"},
    {"domain": "rosfinmonitoring.ru", "name": "Росфинмониторинг", "priority": "high", "selector": ".article-content", "pdf": True},
    {"domain": "minfin.gov.ru", "name": "Минфин России", "priority": "high", "selector": ".document-content"},
    {"domain": "cbr.ru", "name": "Банк России", "priority": "medium", "selector": ".stat-table, .macro"},
    {"domain": "sudact.ru", "name": "Судебные акты", "priority": "medium", "selector": ".decision-text"},
    {"domain": "ach.gov.ru", "name": "Счётная палата", "priority": "low", "selector": ".report-body", "pdf": True},
]
