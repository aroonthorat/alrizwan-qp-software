import re
import unicodedata
from typing import List, Dict, Any, Tuple

# Urdu Arabic-to-Urdu replacements (specs/GRAMMAR-RULES.md §5.1)
URDU_REPLACEMENTS = [
    ("\u064A", "\u06CC"),  # Arabic Yeh -> Urdu Yeh
    ("\u0649", "\u06CC"),  # Alef Maksura -> Urdu Yeh
    ("\u0643", "\u06A9"),  # Arabic Kaf -> Urdu Keheh
    ("\u0647", "\u06C1"),  # Arabic Heh -> Goal Heh
    ("?", "\u061F"),        # ? -> Urdu question mark
    (",", "\u060C"),        # , -> Urdu comma
    (";", "\u061B"),        # ; -> Urdu semicolon
]

def apply_auto_rules(text: str, lang: str = "en") -> Tuple[str, List[Dict[str, Any]]]:
    """
    Applies silent AUTO rules and logs them according to specs/GRAMMAR-RULES.md §0 & §1.
    """
    logs = []
    original = text

    # U-05: Unicode normalise to NFC
    nfc_text = unicodedata.normalize("NFC", text)
    if nfc_text != text:
        logs.append({"rule": "U-05", "level": "AUTO", "note": "Unicode normalized to NFC"})
        text = nfc_text

    # U-01: Collapse multiple spaces
    trimmed = re.sub(r"[ \t]+", " ", text).strip()
    if trimmed != text:
        logs.append({"rule": "U-01", "level": "AUTO", "note": "Collapsed multiple spaces"})
        text = trimmed

    # U-03: Normalize blanks to 12 underscores
    norm_blanks = re.sub(r"_{3,}|\.{3,}|…|--+", "____________", text)
    if norm_blanks != text:
        logs.append({"rule": "U-03", "level": "AUTO", "note": "Normalized blank to 12 underscores"})
        text = norm_blanks

    # U-04: Bracket spacing
    b_text = re.sub(r"\(\s+", "(", text)
    b_text = re.sub(r"\s+\)", ")", b_text)
    # Marks pattern 10x1=10 -> 10 × 1 = 10
    b_text = re.sub(r"(\d+)\s*[xX]\s*(\d+)\s*=\s*(\d+)", r"\1 × \2 = \3", b_text)
    if b_text != text:
        logs.append({"rule": "U-04", "level": "AUTO", "note": "Standardized bracket spacing and multiplication symbol"})
        text = b_text

    # Language-specific AUTO rules
    if lang == "en":
        # EN-02: standalone 'i' -> 'I'
        i_fixed = re.sub(r"\bi\b", "I", text)
        if i_fixed != text:
            logs.append({"rule": "EN-02", "level": "AUTO", "note": "Capitalized standalone 'i' to 'I'"})
            text = i_fixed
        # EN-01: Capitalize first letter if lowercase
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
            logs.append({"rule": "EN-01", "level": "AUTO", "note": "Capitalized leading character"})

    elif lang == "hi":
        # HI-01: Sentence end uses । instead of .
        hi_end = re.sub(r"\.(?=\s|$)", "।", text)
        if hi_end != text:
            logs.append({"rule": "HI-01", "level": "AUTO", "note": "Replaced full stop with Purna Viram (।)"})
            text = hi_end

    elif lang == "mr":
        # MR-01: Modern Marathi uses . instead of ।
        mr_end = text.replace("।", ".")
        if mr_end != text:
            logs.append({"rule": "MR-01", "level": "AUTO", "note": "Replaced Purna Viram with full stop (.)"})
            text = mr_end

    elif lang == "ur":
        # UR-01: Urdu Unicode normalization
        for src, dst in URDU_REPLACEMENTS:
            if src in text:
                text = text.replace(src, dst)
                logs.append({"rule": "UR-01", "level": "AUTO", "note": f"Urdu character normalization {src} -> {dst}"})

    return text, logs
