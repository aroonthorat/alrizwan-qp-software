import json
import sqlite3
import hashlib
import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from server.database import get_db_connection
from server.models import ParsedPaper, QuestionGroup, QuestionItem, PaperHeader

def generate_question_id(text: str, class_name: str, subject: str, q_type: str) -> str:
    slug = f"{class_name}-{subject}-{q_type}-{text[:30]}".lower()
    h = hashlib.sha256(slug.encode("utf-8")).hexdigest()[:8].upper()
    sub_code = "".join([w[0] for w in subject.split()[:2]]).upper() or "GEN"
    cls_code = "".join([c for c in class_name if c.isdigit()]) or "X"
    return f"{sub_code}{cls_code}-{q_type[:3]}-{h}"

def save_question_to_db(q: Dict[str, Any], conn: Optional[sqlite3.Connection] = None) -> str:
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    cur = conn.cursor()
    q_id = q.get("id") or generate_question_id(q["text"], q.get("class", "9"), q.get("subject", "General"), q.get("type", "SHORT"))
    
    cur.execute("""
    INSERT INTO questions (
        id, class, subject, chapter, section, lang, type, sub_type, marks,
        text, options_json, answer_json, diagram_id, needs_source, difficulty,
        grammar_checked, created_by, created_on
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        class=excluded.class,
        subject=excluded.subject,
        chapter=excluded.chapter,
        section=excluded.section,
        lang=excluded.lang,
        type=excluded.type,
        marks=excluded.marks,
        text=excluded.text,
        options_json=excluded.options_json,
        answer_json=excluded.answer_json,
        grammar_checked=excluded.grammar_checked
    """, (
        q_id,
        q.get("class", "Class 9th"),
        q.get("subject", "Social Science"),
        q.get("chapter", "General"),
        q.get("section"),
        q.get("lang", "en"),
        q.get("type", "SHORT"),
        q.get("sub_type"),
        float(q.get("marks", 1.0)),
        q["text"],
        json.dumps(q.get("options")) if q.get("options") else None,
        json.dumps(q.get("answer")) if q.get("answer") is not None else None,
        q.get("diagram_id"),
        1 if q.get("needs_source") else 0,
        q.get("difficulty", "medium"),
        1 if q.get("grammar_checked") else 0,
        q.get("created_by", "teacher"),
        q.get("created_on", datetime.now().strftime("%Y-%m-%d"))
    ))

    if close_conn:
        conn.commit()
        conn.close()

    return q_id

def list_bank_questions(
    class_filter: Optional[str] = None,
    subject_filter: Optional[str] = None,
    chapter_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    lang_filter: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    conn = get_db_connection()
    cur = conn.cursor()

    conditions = []
    params = []

    if class_filter:
        conditions.append("class = ?")
        params.append(class_filter)
    if subject_filter:
        conditions.append("subject = ?")
        params.append(subject_filter)
    if chapter_filter:
        conditions.append("chapter = ?")
        params.append(chapter_filter)
    if type_filter:
        conditions.append("type = ?")
        params.append(type_filter)
    if lang_filter:
        conditions.append("lang = ?")
        params.append(lang_filter)
    if search_query:
        conditions.append("text LIKE ?")
        params.append(f"%{search_query}%")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # Count total
    cur.execute(f"SELECT COUNT(*) FROM questions {where_clause}", params)
    total_count = cur.fetchone()[0]

    # Fetch rows
    query = f"""
    SELECT id, class, subject, chapter, section, lang, type, sub_type, marks,
           text, options_json, answer_json, diagram_id, difficulty, grammar_checked,
           created_by, created_on
    FROM questions
    {where_clause}
    ORDER BY created_on DESC, id ASC
    LIMIT ? OFFSET ?
    """
    cur.execute(query, params + [limit, offset])
    rows = cur.fetchall()

    questions = []
    for r in rows:
        q_dict = dict(r)
        q_dict["options"] = json.loads(r["options_json"]) if r["options_json"] else None
        q_dict["answer"] = json.loads(r["answer_json"]) if r["answer_json"] else None

        # Fetch usage history
        cur.execute("""
        SELECT paper_id, exam_name, date
        FROM usage
        WHERE question_id = ?
        ORDER BY date DESC
        """, (r["id"],))
        usage_rows = cur.fetchall()
        q_dict["used_in"] = [dict(u) for u in usage_rows]

        questions.append(q_dict)

    conn.close()
    return {"total": total_count, "items": questions}

def save_paper_and_record_usage(paper: ParsedPaper, docx_path: str = "") -> str:
    conn = get_db_connection()
    cur = conn.cursor()

    today_str = datetime.now().strftime("%Y-%m-%d")
    unique_suffix = uuid.uuid4().hex[:6]
    paper_id = f"P-{paper.template}-{paper.header.class_name[:2]}-{paper.header.subject[:2]}-{unique_suffix}"

    # 1. Insert Paper
    cur.execute("""
    INSERT INTO papers (
        id, school, class, subject, exam_name, month_year, marks, time, template,
        created_by, created_on, docx_path
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        paper_id,
        paper.header.school,
        paper.header.class_name,
        paper.header.subject,
        paper.header.paper_name,
        paper.header.month_year,
        paper.header.marks,
        paper.header.time,
        paper.template,
        "teacher",
        today_str,
        docx_path
    ))

    # 2. Save Questions & Usage
    order_no = 0
    for grp in paper.groups:
        for q in grp.questions:
            order_no += 1
            # Save or ensure question exists in bank
            q_id = q.id or generate_question_id(q.text, paper.header.class_name, paper.header.subject, q.type)
            
            save_question_to_db({
                "id": q_id,
                "class": paper.header.class_name,
                "subject": paper.header.subject,
                "chapter": grp.section_name or grp.heading,
                "section": grp.section_name,
                "type": q.type,
                "marks": q.marks,
                "text": q.text,
                "options": q.options
            }, conn=conn)

            # Link paper item
            cur.execute("""
            INSERT OR REPLACE INTO paper_items (paper_id, question_id, q_group, order_no)
            VALUES (?, ?, ?, ?)
            """, (paper_id, q_id, grp.group_id, order_no))

            # Record usage
            cur.execute("""
            INSERT INTO usage (question_id, paper_id, exam_name, date)
            VALUES (?, ?, ?, ?)
            """, (q_id, paper_id, paper.header.paper_name, paper.header.date or today_str))

    conn.commit()
    conn.close()
    return paper_id

def check_paper_repetition_warnings(paper: ParsedPaper) -> List[str]:
    """
    Rule engine from specs/QUESTION-TYPES.md §8:
    1. Warn when a question was used in the same class & subject within the last 2 exams.
    2. Never repeat a question inside the same paper.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    warnings = []

    seen_texts = set()

    for grp in paper.groups:
        for q in grp.questions:
            # Check internal paper duplicate
            norm_q = q.text.strip().lower()
            if norm_q in seen_texts:
                warnings.append(f"Question repeated within this paper: '{q.text[:45]}...'")
            seen_texts.add(norm_q)

            # Check historical exams in SQLite
            q_id = q.id
            if not q_id:
                # Look up by text
                cur.execute("SELECT id FROM questions WHERE text = ? LIMIT 1", (q.text,))
                row = cur.fetchone()
                if row:
                    q_id = row[0]

            if q_id:
                # Find recent exams where it was used
                cur.execute("""
                SELECT u.exam_name, u.date, p.class, p.subject
                FROM usage u
                JOIN papers p ON u.paper_id = p.id
                WHERE u.question_id = ? AND p.class = ? AND p.subject = ?
                ORDER BY u.date DESC
                LIMIT 2
                """, (q_id, paper.header.class_name, paper.header.subject))
                recent_uses = cur.fetchall()
                if recent_uses:
                    exam_list = ", ".join([f"{u['exam_name']} ({u['date']})" for u in recent_uses])
                    warnings.append(
                        f"Question {q.q_num} ('{q.text[:35]}...') was previously used in recent exam(s): {exam_list}."
                    )

    conn.close()
    return warnings

def auto_pick_from_bank(
    header: PaperHeader,
    template: str = "3a",
    question_count: int = 10,
    preferred_type: Optional[str] = None
) -> ParsedPaper:
    """
    Auto-pick mode per specs/QUESTION-TYPES §8 and SOFTWARE-PLAN §3 step 9b:
    Prefers questions with oldest used_in date (least recently used) or never used,
    matching the class and subject.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    type_clause = "AND q.type = ?" if preferred_type else ""
    params = [header.class_name, header.subject]
    if preferred_type:
        params.append(preferred_type)

    query = f"""
    SELECT q.id, q.type, q.marks, q.text, q.options_json, q.chapter, q.section,
           MAX(u.date) as last_used
    FROM questions q
    LEFT JOIN usage u ON q.id = u.question_id
    WHERE q.class = ? AND q.subject = ? {type_clause}
    GROUP BY q.id
    ORDER BY last_used ASC NULLS FIRST, RANDOM()
    LIMIT ?
    """
    cur.execute(query, params + [question_count])
    rows = cur.fetchall()
    conn.close()

    if not rows:
        raise ValueError(f"No questions found in bank for {header.class_name} - {header.subject}")

    # Build ParsedPaper
    groups = []
    if template == "3b":
        # MCQ paper: group by section or single section
        group = QuestionGroup(
            group_id="SEC-1",
            heading="SECTION A — GENERAL",
            is_section=True,
            section_name="SECTION A — GENERAL",
            marks_per_q=1.0,
            questions=[]
        )
        for i, r in enumerate(rows, 1):
            opts = json.loads(r["options_json"]) if r["options_json"] else ["A", "B", "C", "D"]
            group.questions.append(QuestionItem(
                id=r["id"],
                q_num=str(i),
                text=r["text"],
                type="MCQ",
                marks=1.0,
                options=opts
            ))
        group.count = len(group.questions)
        group.total_marks = float(group.count)
        groups.append(group)
    else:
        # Theory paper: single or multiple groups
        group = QuestionGroup(
            group_id="Q.1",
            heading="Answer the following.",
            marks_display=f"({len(rows)} × 1 = {len(rows)})",
            marks_per_q=1.0,
            total_marks=float(len(rows)),
            count=len(rows),
            questions=[]
        )
        for i, r in enumerate(rows, 1):
            group.questions.append(QuestionItem(
                id=r["id"],
                q_num=str(i),
                text=r["text"],
                type=r["type"],
                marks=float(r["marks"])
            ))
        groups.append(group)

    total_marks = sum(g.total_marks for g in groups)
    header.marks = int(total_marks)

    return ParsedPaper(
        header=header,
        template=template,
        groups=groups,
        total_marks_calculated=total_marks,
        is_valid=True,
        validation_errors=[],
        validation_warnings=[]
    )
