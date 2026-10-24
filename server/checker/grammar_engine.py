import re
import unicodedata
from typing import List, Dict, Any, Tuple, Optional
from server.models import QuestionItem, ParsedPaper

# US -> UK English dictionary (specs/GRAMMAR-RULES.md §2 EN-08)
US_TO_UK_SPELLINGS = {
    "color": "colour",
    "colors": "colours",
    "colored": "coloured",
    "coloring": "colouring",
    "center": "centre",
    "centers": "centres",
    "centered": "centred",
    "organization": "organisation",
    "organizations": "organisations",
    "labor": "labour",
    "labors": "labours",
    "meter": "metre",
    "meters": "metres",
    "program": "programme",
    "programs": "programmes",
    "neighbor": "neighbour",
    "neighbors": "neighbours",
    "favor": "favour",
    "favors": "favours",
    "honor": "honour",
    "honors": "honours",
    "behavior": "behaviour"
}

# English common confusions (EN-06)
EN_CONFUSIONS = [
    (r"\bits\s+a\b", "it's a", "Did you mean 'it is' (it's)?"),
    (r"\btheir\s+is\b", "there is", "Did you mean 'there is'?"),
    (r"\bthere\s+book\b", "their book", "Did you mean possessive 'their'?"),
    (r"\bloose\s+the\s+match\b", "lose the match", "Did you mean 'lose' (opposite of win)?"),
    (r"\bprincipal\s+of\s+physics\b", "principle of physics", "Did you mean scientific 'principle'?")
]

# Hindi standard forms (HI-03, HI-08)
HINDI_REPLACEMENTS = {
    "गयी": ("गई", "केंद्रीय हिंदी निदेशालय standard form (HI-03)"),
    "लिये": ("लिए", "Standard form (HI-03)"),
    "हुये": ("हुए", "Standard form (HI-03)"),
    "चाहिये": ("चाहिए", "Standard form (HI-03)"),
    "क्रपया": ("कृपया", "Correct matra for kripaya (HI-08)"),
    "उज्वल": ("उज्ज्वल", "Standard spelling (HI-08)"),
    "आशिर्वाद": ("आशीर्वाद", "Standard spelling (HI-08)"),
    "सामग्रि": ("सामग्री", "Standard spelling (HI-08)")
}

# Marathi standard forms (MR-03, MR-07)
MARATHI_REPLACEMENTS = {
    "आणी": ("आणि", "महाराष्ट्र शासन मान्य नियम - आणि (MR-03)"),
    "पाहीजे": ("पाहिजे", "Standard Marathi spelling (MR-03)"),
    "काहि": ("काही", "Long final vowel (MR-03, MR-04)"),
    "नाहि": ("नाही", "Long final vowel (MR-03, MR-04)"),
    "और": ("आणि", "Marathi uses आणि instead of Hindi और (MR-07)"),
    "है": ("आहे", "Marathi uses आहे instead of Hindi है (MR-07)")
}

# Urdu standard forms (UR-01, UR-02)
URDU_REPLACEMENTS = {
    "کیجئے": ("کیجیے", "Standard Urdu form (UR-02)"),
    "لئے": ("لیے", "Standard Urdu form (UR-02)"),
    "دیجئے": ("دیجیے", "Standard Urdu form (UR-02)"),
    "گئے": ("گئے", "Standard Urdu form (UR-02)")
}

URDU_UNICODE_MAP = [
    ("\u064A", "\u06CC"),  # Arabic Yeh -> Urdu Yeh
    ("\u0649", "\u06CC"),  # Alef Maksura -> Urdu Yeh
    ("\u0643", "\u06A9"),  # Arabic Kaf -> Urdu Keheh
    ("\u0647", "\u06C1"),  # Arabic Heh -> Goal Heh
    ("?", "\u061F"),        # ? -> Urdu question mark
    (",", "\u060C"),        # , -> Urdu comma
    (";", "\u061B"),        # ; -> Urdu semicolon
]

def detect_language(text: str) -> str:
    """Detects script/language: en, hi, mr, ur"""
    arabic_count = len(re.findall(r"[\u0600-\u06FF]", text))
    devanagari_count = len(re.findall(r"[\u0900-\u097F]", text))
    
    if arabic_count > devanagari_count and arabic_count > 5:
        return "ur"
    elif devanagari_count > 5:
        # Check for Marathi specific characters or words
        if "आहे" in text or "नाही" in text or "आणि" in text or "ऱ्" in text:
            return "mr"
        return "hi"
    return "en"

def check_question_grammar(
    q_id: str,
    text: str,
    lang: Optional[str] = None
) -> Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Checks grammar, spelling, punctuation, and Unicode for a question text.
    Returns:
        (auto_cleaned_text, auto_logs, suggestions)
    """
    if not lang:
        lang = detect_language(text)

    auto_logs: List[Dict[str, Any]] = []
    suggestions: List[Dict[str, Any]] = []

    # --- 1. Universal AUTO Rules ---
    # U-05: Unicode normalize to NFC
    nfc = unicodedata.normalize("NFC", text)
    if nfc != text:
        auto_logs.append({
            "rule": "U-05", "level": "AUTO",
            "original": text, "suggestion": nfc,
            "note": "Unicode normalized to NFC"
        })
        text = nfc

    # U-01: Collapse multiple spaces
    collapsed = re.sub(r"[ \t]+", " ", text).strip()
    if collapsed != text:
        auto_logs.append({
            "rule": "U-01", "level": "AUTO",
            "original": text, "suggestion": collapsed,
            "note": "Collapsed multiple spaces"
        })
        text = collapsed

    # U-03: Blanks normalization
    blanks_fixed = re.sub(r"_{3,}|\.{3,}|…|--+", "____________", text)
    if blanks_fixed != text:
        auto_logs.append({
            "rule": "U-03", "level": "AUTO",
            "original": text, "suggestion": blanks_fixed,
            "note": "Normalized blank to 12 underscores"
        })
        text = blanks_fixed

    # U-04: Bracket & multiplication normalization
    b_text = re.sub(r"\(\s+", "(", text)
    b_text = re.sub(r"\s+\)", ")", b_text)
    b_text = re.sub(r"(\d+)\s*[xX]\s*(\d+)\s*=\s*(\d+)", r"\1 × \2 = \3", b_text)
    if b_text != text:
        auto_logs.append({
            "rule": "U-04", "level": "AUTO",
            "original": text, "suggestion": b_text,
            "note": "Standardized bracket spacing and multiplication symbol"
        })
        text = b_text

    # --- 2. Language-Specific Rules ---

    if lang == "en":
        # EN-01: Capitalize first letter
        if text and text[0].islower():
            cap = text[0].upper() + text[1:]
            auto_logs.append({
                "rule": "EN-01", "level": "AUTO",
                "original": text[0], "suggestion": text[0].upper(),
                "note": "Capitalized first letter"
            })
            text = cap

        # EN-02: Standalone 'i' -> 'I'
        i_fixed = re.sub(r"\bi\b", "I", text)
        if i_fixed != text:
            auto_logs.append({
                "rule": "EN-02", "level": "AUTO",
                "original": "i", "suggestion": "I",
                "note": "Capitalized standalone pronoun 'i'"
            })
            text = i_fixed

        # EN-03: Wh-questions should end with '?'
        wh_match = re.match(r"^(?:What|Why|How|Which|Who|When|Where|Whose|Whom)\b", text, re.IGNORECASE)
        if wh_match and not text.endswith("?"):
            suggestions.append({
                "question_id": q_id,
                "lang": "en",
                "level": "FIX",
                "rule": "EN-03",
                "original": text[-1] if text else "",
                "suggestion": text + "?",
                "note": "Wh-questions must end with a question mark (?)"
            })

        # EN-08: US -> UK Indian English
        for us_word, uk_word in US_TO_UK_SPELLINGS.items():
            pattern = rf"\b{us_word}\b"
            if re.search(pattern, text, re.IGNORECASE):
                suggestions.append({
                    "question_id": q_id,
                    "lang": "en",
                    "level": "STYLE",
                    "rule": "EN-08",
                    "original": us_word,
                    "suggestion": uk_word,
                    "note": f"British/Indian English spelling: '{uk_word}' instead of '{us_word}'"
                })

        # EN-06: Common confusions
        for pattern, repl, note in EN_CONFUSIONS:
            if re.search(pattern, text, re.IGNORECASE):
                suggestions.append({
                    "question_id": q_id,
                    "lang": "en",
                    "level": "FIX",
                    "rule": "EN-06",
                    "original": text,
                    "suggestion": repl,
                    "note": note
                })

    elif lang == "hi":
        # HI-01: Full stop -> Purna Viram (।)
        if text.endswith("."):
            hi_end = text[:-1] + "।"
            auto_logs.append({
                "rule": "HI-01", "level": "AUTO",
                "original": ".", "suggestion": "।",
                "note": "Replaced full stop with Purna Viram (।)"
            })
            text = hi_end

        # HI-03 / HI-08 replacements
        for wrong, (correct, note) in HINDI_REPLACEMENTS.items():
            if wrong in text:
                suggestions.append({
                    "question_id": q_id,
                    "lang": "hi",
                    "level": "FIX",
                    "rule": "HI-03",
                    "original": wrong,
                    "suggestion": correct,
                    "note": note
                })

    elif lang == "mr":
        # MR-01: Convert । to . for modern Marathi
        if "।" in text:
            mr_end = text.replace("।", ".")
            auto_logs.append({
                "rule": "MR-01", "level": "AUTO",
                "original": "।", "suggestion": ".",
                "note": "Modern Marathi uses full stop (.)"
            })
            text = mr_end

        # MR-03 / MR-07 replacements
        for wrong, (correct, note) in MARATHI_REPLACEMENTS.items():
            if wrong in text:
                suggestions.append({
                    "question_id": q_id,
                    "lang": "mr",
                    "level": "FIX",
                    "rule": "MR-03",
                    "original": wrong,
                    "suggestion": correct,
                    "note": note
                })

    elif lang == "ur":
        # UR-01: Arabic Unicode normalization
        for src, dst in URDU_UNICODE_MAP:
            if src in text:
                replaced = text.replace(src, dst)
                auto_logs.append({
                    "rule": "UR-01", "level": "AUTO",
                    "original": src, "suggestion": dst,
                    "note": f"Urdu Arabic letter normalization ({src} -> {dst})"
                })
                text = replaced

        # UR-02 replacements
        for wrong, (correct, note) in URDU_REPLACEMENTS.items():
            if wrong in text:
                suggestions.append({
                    "question_id": q_id,
                    "lang": "ur",
                    "level": "FIX",
                    "rule": "UR-02",
                    "original": wrong,
                    "suggestion": correct,
                    "note": note
                })

    # U-12: Unclosed brackets or quotation marks
    for open_b, close_b in [("(", ")"), ("[", "]"), ("{", "}"), ('"', '"'), ("'", "'")]:
        if open_b == close_b:
            if text.count(open_b) % 2 != 0:
                suggestions.append({
                    "question_id": q_id,
                    "lang": lang,
                    "level": "CHECK",
                    "rule": "U-12",
                    "original": text,
                    "suggestion": None,
                    "note": f"Possible unclosed quote {open_b}"
                })
        else:
            if text.count(open_b) != text.count(close_b):
                suggestions.append({
                    "question_id": q_id,
                    "lang": lang,
                    "level": "CHECK",
                    "rule": "U-12",
                    "original": text,
                    "suggestion": None,
                    "note": f"Unbalanced brackets {open_b} and {close_b}"
                })

    return text, auto_logs, suggestions

def audit_paper_grammar(paper: ParsedPaper) -> Dict[str, Any]:
    """
    Audits every question in the paper and produces a complete suggestions report.
    """
    all_auto_logs = []
    all_suggestions = []

    for grp in paper.groups:
        for q in grp.questions:
            cleaned_text, a_logs, suggs = check_question_grammar(q.id or q.q_num, q.text)
            # Update cleaned text if auto rules applied
            q.text = cleaned_text
            all_auto_logs.extend(a_logs)
            all_suggestions.extend(suggs)

            # Check options if MCQ
            if q.options:
                cleaned_opts = []
                for opt in q.options:
                    cl_opt, o_logs, o_suggs = check_question_grammar(q.id or q.q_num, opt)
                    cleaned_opts.append(cl_opt)
                    all_auto_logs.extend(o_logs)
                    all_suggestions.extend(o_suggs)
                q.options = cleaned_opts

    return {
        "auto_logs": all_auto_logs,
        "suggestions": all_suggestions,
        "total_auto_fixed": len(all_auto_logs),
        "total_suggestions": len(all_suggestions)
    }
