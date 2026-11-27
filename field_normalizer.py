"""Çalışma alanlarını (TR/EN, kısaltma ve yazım farkları) normalize etme modülü."""

from difflib import get_close_matches
import re


# Yaygın Bilgisayar Mühendisliği (CS/CENG) alanları için standart eşleme tablosu
FIELD_SYNONYMS = {
    # Artificial Intelligence
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "yapay zeka": "Artificial Intelligence",
    # Machine Learning
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "makine ogrenmesi": "Machine Learning",
    "makine ogrenimi": "Machine Learning",
    # Deep Learning
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "derin ogrenme": "Deep Learning",
    # Natural Language Processing
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "dogal dil isleme": "Natural Language Processing",
    # Computer Vision & Image Processing
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "bilgisayarli goru": "Computer Vision",
    "bilgisayarli gorme": "Computer Vision",
    "image processing": "Image Processing",
    "goruntu isleme": "Image Processing",
    # Data Science / Mining / Big Data
    "data science": "Data Science",
    "veri bilimi": "Data Science",
    "data mining": "Data Mining",
    "veri madenciligi": "Data Mining",
    "big data": "Big Data",
    "buyuk veri": "Big Data",
    # Cyber Security & Networks
    "cyber security": "Cyber Security",
    "cybersecurity": "Cyber Security",
    "siber guvenlik": "Cyber Security",
    "information security": "Information Security",
    "bilgi guvenligi": "Information Security",
    "network security": "Network Security",
    "ag guvenligi": "Network Security",
    "computer networks": "Computer Networks",
    "bilgisayar aglari": "Computer Networks",
    "wireless networks": "Wireless Networks",
    "kablosuz aglar": "Wireless Networks",
    "cryptography": "Cryptography",
    "kriptografi": "Cryptography",
    # Robotics & Embedded & IoT
    "robotics": "Robotics",
    "robotik": "Robotics",
    "iot": "Internet of Things",
    "internet of things": "Internet of Things",
    "nesnelerin interneti": "Internet of Things",
    "embedded systems": "Embedded Systems",
    "gomulu sistemler": "Embedded Systems",
    # Software & Systems & Cloud
    "software engineering": "Software Engineering",
    "yazilim muhendisligi": "Software Engineering",
    "cloud computing": "Cloud Computing",
    "bulut bilisim": "Cloud Computing",
    "distributed systems": "Distributed Systems",
    "dagitik sistemler": "Distributed Systems",
    "operating systems": "Operating Systems",
    "isletim sistemleri": "Operating Systems",
    "database systems": "Database Systems",
    "veritabani sistemleri": "Database Systems",
    "veritabani": "Database Systems",
    "human computer interaction": "Human-Computer Interaction",
    "hci": "Human-Computer Interaction",
    "insan bilgisayar etkilesimi": "Human-Computer Interaction",
    "bioinformatics": "Bioinformatics",
    "biyoinformatik": "Bioinformatics",
    "blockchain": "Blockchain",
    "blokzincir": "Blockchain",
    "blok zincir": "Blockchain",
}

_TR_MAP = str.maketrans("çğıöşüâîû", "cgiosuaiu")
_CANONICAL_VALUES = sorted(set(FIELD_SYNONYMS.values()))


def _simplify(text):
    """Karşılaştırma için metni küçültür, Türkçe karakter ve noktalama farklarını giderir."""
    lowered = str(text).replace("İ", "i").replace("I", "i").lower()
    ascii_like = lowered.translate(_TR_MAP)
    cleaned = re.sub(r"[^a-z0-9\s]", " ", ascii_like)
    return " ".join(cleaned.split())


def normalize_field(raw_field, known_fields=None, cutoff=0.86):
    """Tek bir çalışma alanı adını standart biçime dönüştürür."""
    text = str(raw_field).strip()
    if not text:
        return ""

    key = _simplify(text)
    if not key:
        return ""

    # 1. Tam sözlük eşleşmesi (TR/EN/kısaltma)
    if key in FIELD_SYNONYMS:
        return FIELD_SYNONYMS[key]

    # 2. Standart sözlük anahtarlarına yakın (fuzzy) eşleşme
    synonym_match = get_close_matches(key, FIELD_SYNONYMS.keys(), n=1, cutoff=cutoff)
    if synonym_match:
        return FIELD_SYNONYMS[synonym_match[0]]

    # 3. Veri setinde daha önce görülen alanlara yakın (fuzzy) eşleşme
    if known_fields:
        simplified_known = {_simplify(item): item for item in known_fields}
        known_match = get_close_matches(
            key, simplified_known.keys(), n=1, cutoff=cutoff
        )
        if known_match:
            return simplified_known[known_match[0]]

    # 4. Yeni bir alansa temizleyip baş harflerini büyüt
    return " ".join(text.split()).title()


def normalize_dataset(academics, cutoff=0.86):
    """Tüm akademisyen listesinin 'fields' alanlarını normalize edip yeni liste döndürür."""
    seen_fields = list(_CANONICAL_VALUES)
    normalized_records = []

    for academic in academics:
        record = dict(academic)
        cleaned = []
        for raw_field in academic.get("fields", []):
            norm = normalize_field(raw_field, known_fields=seen_fields, cutoff=cutoff)
            if norm:
                if norm not in seen_fields:
                    seen_fields.append(norm)
                if norm not in cleaned:
                    cleaned.append(norm)
        record["fields"] = cleaned
        normalized_records.append(record)

    return normalized_records


if __name__ == "__main__":
    test_fields = [
        "Makine Öğrenmesi",
        "ML",
        "Machine Learning",
        "Yapay Zekâ",
        "AI",
        "Cybersecurity",
        "Siber Güvenlik",
        "Doğal Dil İşleme",
        "NLP",
        "Deep Learnings",
    ]
    for item in test_fields:
        print(f"{item:<20} -> {normalize_field(item)}")