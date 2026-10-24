import re
from typing import List, Tuple, Optional, Dict, Any
from server.models import (
    PaperHeader, QuestionItem, QuestionGroup,
    ParsedPaper, DiagramPlaceholder
)

GROUP_HEADER_PATTERN = re.compile(
    r"^(?:Q(?:uestion)?\.?\s*(\d+|[A-Za-z]+)[\).:\-]?|प्र(?:श्न)?\.?\s*(\d+|[१-९]+)[\).:\-]?)\s*(.*?)$",
    re.IGNORECASE
)

SECTION_HEADER_PATTERN = re.compile(
    r"^(SECTION\s+[A-Z]|PART\s+[A-Z0-9]+|विभाग\s+[क-हA-Z0-9]+|حصہ\s+[ا-یA-Z0-9]+)\s*[\—\-\:]?\s*(.*?)$",
    re.IGNORECASE
)

MARKS_BREAKDOWN_PATTERN = re.compile(
    r"\(\s*(\d+)\s*(?:[×x*]\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)|[+]\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)|Marks?|marks?)?\s*\)",
    re.IGNORECASE
)

ANY_N_PATTERN = re.compile(
    r"\(\s*(?:any|Any|किन्हीं|कोणतेही|کوئی)\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten|[१-९]+)\s*\)",
    re.IGNORECASE
)

WORD_NUMS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "१": 1, "२": 2, "३": 3, "४": 4, "५": 5, "६": 6, "७": 7, "८": 8, "९": 9
}

SUB_Q_PATTERN = re.compile(
    r"^(?:(\d+)\.|\((\d+)\)|([a-z])\.|([ivx]+)\.|\((\w+)\))\s+(.*)$",
    re.IGNORECASE
)

DIAGRAM_KEYWORDS = ["figure", "diagram", "आकृती", "चित्र", "تصویر", "خاکہ"]
MAP_KEYWORDS = ["map", "outline map", "नकाशा", "نقشہ"]

def normalize_text(text: str) -> str:
    """Universal rules U-01, U-03, U-04 from specs/GRAMMAR-RULES.md"""
    # Collapse multiple spaces, clean trailing/leading
    text = re.sub(r"[ \t]+", " ", text).strip()
    # Normalize blanks
    text = re.sub(r"_{3,}|\.{3,}|…|--+", "____________", text)
    # Normalize brackets spacing
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    return text

def parse_marks_from_heading(heading_line: str) -> Tuple[str, Optional[str], Optional[int], float, float]:
    """
    Extracts (clean_heading, marks_display, any_n, marks_per_q, total_marks)
    e.g. 'Answer in brief. (any 5) (5 × 2 = 10)'
    """
    any_n = None
    any_match = ANY_N_PATTERN.search(heading_line)
    if any_match:
        val_str = any_match.group(1).lower()
        any_n = WORD_NUMS.get(val_str, int(val_str) if val_str.isdigit() else None)

    marks_display = None
    marks_per_q = 1.0
    total_marks = 0.0

    # Look for patterns like (10 × 1 = 10) or (3 + 3 = 6) or (5)
    paren_matches = list(re.finditer(r"\(([^\)]+)\)", heading_line))
    for m in reversed(paren_matches):
        inner = m.group(1).strip()
        # count × marks = total
        mult_match = re.match(r"(\d+)\s*[×x*]\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)", inner)
        if mult_match:
            marks_display = f"({mult_match.group(1)} × {mult_match.group(2)} = {mult_match.group(3)})"
            marks_per_q = float(mult_match.group(2))
            total_marks = float(mult_match.group(3))
            heading_line = heading_line[:m.start()] + heading_line[m.end():]
            break
        # 3 + 3 = 6
        sum_match = re.match(r"(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)", inner)
        if sum_match:
            marks_display = f"({sum_match.group(1)} + {sum_match.group(2)} = {sum_match.group(3)})"
            total_marks = float(sum_match.group(3))
            marks_per_q = float(sum_match.group(1))
            heading_line = heading_line[:m.start()] + heading_line[m.end():]
            break
        # (5) or (5 Marks)
        single_match = re.match(r"^(\d+(?:\.\d+)?)\s*(?:Marks?|marks?|गुण|نمرات)?$", inner)
        if single_match and not any_match:
            total_marks = float(single_match.group(1))
            marks_display = f"({int(total_marks) if total_marks.is_integer() else total_marks})"
            marks_per_q = total_marks
            heading_line = heading_line[:m.start()] + heading_line[m.end():]
            break

    # If any_n was removed from heading line or kept
    clean_heading = normalize_text(heading_line)
    return clean_heading, marks_display, any_n, marks_per_q, total_marks

OPTION_MARKER_REGEX = re.compile(
    r"(?:(?<=\s)|^)(?:\(([1-4]|[A-Da-d]|[क-घ]|[१-४])\)|([A-Da-d]|[क-घ])[\).])\s*"
)

def extract_mcq_options(lines: List[str], start_idx: int) -> Tuple[List[str], int]:
    """
    Looks ahead from start_idx to extract options.
    Handles multiple options per line (e.g. 2x2 grid) and handles
    text containing inner parentheses (e.g. K2 (Godwin Austen)).
    Returns (options_list, lines_consumed).
    """
    options = []
    consumed = 0
    idx = start_idx

    while idx < len(lines):
        line = lines[idx].strip()
        if not line:
            idx += 1
            consumed += 1
            continue

        # Look for option markers
        matches = list(OPTION_MARKER_REGEX.finditer(line))
        if not matches:
            break

        # Check if the line begins with the first marker (ignoring leading whitespace)
        if matches[0].start() > 2:
            # Marker is somewhere deep in a sentence, not starting an option
            break

        line_options = []
        for i in range(len(matches)):
            start_pos = matches[i].end()
            end_pos = matches[i+1].start() if i + 1 < len(matches) else len(line)
            opt_text = line[start_pos:end_pos].strip()
            if opt_text:
                line_options.append(opt_text)

        if line_options:
            options.extend(line_options)
            idx += 1
            consumed += 1
            if len(options) >= 4:
                break
        else:
            break

    if len(options) > 0:
        return options, consumed
    return [], 0



def detect_diagram_placeholder(text: str) -> Optional[DiagramPlaceholder]:
    """
    Checks for diagram / figure / map references in question or group text.
    Returns DiagramPlaceholder if found.
    """
    text_lower = text.lower()
    for kw in MAP_KEYWORDS:
        if kw in text_lower:
            caption = "OUTLINE MAP OF INDIA / (attach / paste)"
            if "[" in text and "]" in text:
                custom = text[text.find("[")+1:text.find("]")].strip()
                if custom:
                    caption = custom.upper() + "\n(attach / paste)"
            return DiagramPlaceholder(
                kind="map",
                caption=caption,
                width_px=560,
                height_px=620,
                placement="below"
            )

    for kw in DIAGRAM_KEYWORDS:
        if kw in text_lower:
            caption = "FIGURE / (paste diagram here)"
            if "[" in text and "]" in text:
                custom = text[text.find("[")+1:text.find("]")].strip()
                if custom:
                    caption = custom.upper() + "\n(paste diagram here)"
            return DiagramPlaceholder(
                kind="figure",
                caption=caption,
                width_px=280,
                height_px=175,
                placement="side"
            )

    return None

def detect_question_type(text: str, has_options: bool, group_heading: str) -> str:
    combined = (text + " " + group_heading).lower()
    if has_options or "choose the correct" in combined or "योग्य पर्याय" in combined or "सही विकल्प" in combined:
        return "MCQ"
    if "outline map" in combined or "map work" in combined or "नकाशा" in combined:
        return "MAP_MARK"
    if "figure" in combined or "diagram" in combined or "आकृती" in combined:
        return "FIGURE_QA"
    if "fill in the blank" in combined or "रिक्त स्थान" in combined or "गाळलेल्या जागा" in combined or "______" in text:
        return "FILL_BLANK"
    if "true or false" in combined or "चूक की बरोबर" in combined or "सही या गलत" in combined or "true / false" in combined:
        return "TRUE_FALSE"
    if "match" in combined or "जोड्या जुळवा" in combined or "जोड़ियाँ" in combined:
        return "MATCH"
    if "one sentence" in combined or "एका वाक्यात" in combined or "एक वाक्य" in combined:
        return "ONE_SENTENCE"
    if "one word" in combined or "एका शब्दात" in combined:
        return "ONE_WORD"
    if "brief" in combined or "थोडक्यात" in combined:
        return "SHORT"
    if "detail" in combined or "सविस्तर" in combined or "विस्तार" in combined:
        return "LONG"
    if "reason" in combined or "कारणे" in combined or "कारण" in combined:
        return "REASON"
    if "distinguish" in combined or "difference" in combined or "फरक" in combined:
        return "DIFFERENCE"
    return "SHORT"

def parse_raw_text(raw_text: str, header: PaperHeader, template_override: Optional[str] = None) -> ParsedPaper:
    """
    Parses pasted text into QuestionGroups and Questions.
    Follows QUESTION-TYPES.md §1 & QUESTION-PAPER-TEMPLATE.md.
    """
    raw_text = raw_text.replace("\r\n", "\n")
    # If the user pasted a combined paper with PART 1 / PART 2 markers, we can handle it
    lines = raw_text.split("\n")

    groups: List[QuestionGroup] = []
    current_group: Optional[QuestionGroup] = None
    current_section: Optional[str] = None

    idx = 0
    total_q_count = 0
    mcq_count = 0

    while idx < len(lines):
        line = lines[idx].strip()
        if not line:
            idx += 1
            continue

        # Check for section header: e.g. SECTION A — HISTORY
        sec_match = SECTION_HEADER_PATTERN.match(line)
        if sec_match:
            sec_tag = sec_match.group(1).strip()
            sec_title = sec_match.group(2).strip()
            full_sec = f"{sec_tag} — {sec_title}" if sec_title else sec_tag
            current_section = full_sec
            current_group = None
            idx += 1
            continue

        # Check for Q group header: e.g. Q.1) Answer the following. (10 × 1 = 10)
        grp_match = GROUP_HEADER_PATTERN.match(line)
        if grp_match and not (current_section and not line.upper().startswith("Q")):
            q_num_str = grp_match.group(1) or grp_match.group(2)
            group_id = f"Q.{q_num_str}"
            rest_of_heading = grp_match.group(3)

            clean_head, marks_disp, any_n, marks_per_q, total_m = parse_marks_from_heading(rest_of_heading)

            current_group = QuestionGroup(
                group_id=group_id,
                heading=clean_head,
                marks_display=marks_disp,
                any_n=any_n,
                marks_per_q=marks_per_q,
                total_marks=total_m,
                questions=[],
                is_section=False,
                section_name=current_section
            )
            groups.append(current_group)
            idx += 1
            continue

        # Check if line is a question stem
        sub_match = SUB_Q_PATTERN.match(line)
        if sub_match or (current_section and re.match(r"^\d+\.", line)):
            q_num = ""
            q_text = ""
            if sub_match:
                q_num = next(g for g in sub_match.groups()[:5] if g is not None)
                q_text = sub_match.group(6).strip()
            else:
                parts = line.split(".", 1)
                q_num = parts[0].strip()
                q_text = parts[1].strip() if len(parts) > 1 else ""

            # Check if this question line has placeholder tag [FIGURE 1: ...] or [MAP 1: ...]
            q_diag = detect_diagram_placeholder(q_text)
            if "[" in q_text and "]" in q_text:
                q_text = re.sub(r"\[.*?\]", "", q_text).strip()

            # Look ahead for options
            options, consumed = extract_mcq_options(lines, idx + 1)
            has_options = bool(options)
            if has_options:
                mcq_count += 1
            total_q_count += 1

            # Detect diagram if not found yet
            if not q_diag and current_group:
                q_diag = detect_diagram_placeholder(current_group.heading)

            # Determine type
            group_head = current_group.heading if current_group else (current_section or "")
            q_type = detect_question_type(q_text, has_options, group_head)

            q_item = QuestionItem(
                id=f"{current_group.group_id if current_group else 'SEC'}-{q_num}",
                q_num=q_num,
                text=normalize_text(q_text),
                type=q_type,
                marks=current_group.marks_per_q if current_group else 1.0,
                options=options if has_options else None,
                diagram=q_diag
            )

            # Ensure we have an active group
            if not current_group:
                if current_section:
                    # Check if there is already a group for this section
                    matching = next((g for g in groups if g.section_name == current_section), None)
                    if matching:
                        current_group = matching
                    else:
                        current_group = QuestionGroup(
                            group_id=f"SEC-{len(groups)+1}",
                            heading=current_section,
                            is_section=True,
                            section_name=current_section,
                            marks_per_q=1.0,
                            questions=[]
                        )
                        groups.append(current_group)
                else:
                    current_group = QuestionGroup(
                        group_id="Q.1",
                        heading="Questions",
                        marks_per_q=1.0,
                        questions=[]
                    )
                    groups.append(current_group)

            current_group.questions.append(q_item)
            idx += 1 + consumed
            continue

        # Standalone diagram bracket in text, e.g. [FIGURE 1: Layers of the atmosphere]
        diag_match = detect_diagram_placeholder(line)
        if diag_match and current_group and current_group.questions:
            current_group.questions[-1].diagram = diag_match
            idx += 1
            continue

        # If we have an existing question, append text (continuation line)
        if current_group and current_group.questions:
            current_group.questions[-1].text += " " + normalize_text(line)
        elif current_group:
            current_group.heading += " " + normalize_text(line)

        idx += 1

    # Post-process groups and calculate marks
    template = template_override
    if not template:
        # Majority MCQ -> 3b, else 3a
        if total_q_count > 0 and (mcq_count / total_q_count) >= 0.5:
            template = "3b"
        else:
            template = "3a"

    # Compute group counts and totals
    total_calculated = 0.0
    for grp in groups:
        grp.count = len(grp.questions)
        effective_count = grp.any_n if grp.any_n else grp.count
        if grp.total_marks == 0.0:
            grp.total_marks = effective_count * grp.marks_per_q
        total_calculated += grp.total_marks

    # Validation
    validation_errors: List[str] = []
    validation_warnings: List[str] = []

    # 1. Check marks total equals header marks
    if abs(total_calculated - header.marks) > 0.01:
        validation_errors.append(
            f"Marks mismatch: Total calculated marks from questions ({total_calculated:g}) "
            f"does not match header Max Marks ({header.marks})."
        )

    # 2. Check MCQ options count: MCQ needs exactly 4 options
    for grp in groups:
        for q in grp.questions:
            if q.type == "MCQ" or q.options:
                if not q.options or len(q.options) != 4:
                    validation_errors.append(
                        f"Question {q.q_num} in {grp.heading or grp.group_id} is marked as MCQ but has "
                        f"{len(q.options) if q.options else 0} options (exactly 4 required)."
                    )

    is_valid = len(validation_errors) == 0

    return ParsedPaper(
        header=header,
        template=template,
        groups=groups,
        total_marks_calculated=total_calculated,
        is_valid=is_valid,
        validation_errors=validation_errors,
        validation_warnings=validation_warnings
    )

def parse_paper_parts(raw_text: str, header: PaperHeader) -> Dict[str, ParsedPaper]:
    """
    If the text contains separate parts (e.g. === PART 1: THEORY === and === PART 2: MCQ ===),
    parses both into separate ParsedPaper instances.
    Otherwise returns {"default": parse_raw_text(raw_text, header)}.
    """
    part_split = re.split(r"===\s*PART\s*\d+[^=\n]*===", raw_text, flags=re.IGNORECASE)
    if len(part_split) > 1:
        # We have multiple parts
        results = {}
        headers = re.findall(r"===\s*(PART\s*\d+[^=\n]*)===", raw_text, flags=re.IGNORECASE)
        for i, chunk in enumerate(part_split[1:]):
            label = headers[i].strip() if i < len(headers) else f"Part {i+1}"
            chunk_clean = chunk.strip()
            if not chunk_clean:
                continue
            is_mcq = "MCQ" in label.upper() or "(1)" in chunk_clean
            t_override = "3b" if is_mcq else "3a"
            key = "mcq" if is_mcq else "theory"
            results[key] = parse_raw_text(chunk_clean, header, template_override=t_override)
        if results:
            return results

    # Single paper
    parsed = parse_raw_text(raw_text, header)
    key = "mcq" if parsed.template == "3b" else "theory"
    return {key: parsed}

