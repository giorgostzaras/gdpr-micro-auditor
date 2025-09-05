import os, re
from typing import List
from rank_bm25 import BM25Okapi




_snippets: List[str] = []
_bm25 = None

# Λέξεις-κλειδιά για GDPR/retention (βοηθούν στη στόχευση πρότασης)
RETENTION_HINTS = [
    "διατήρησ", "retention", "χρον", "διάρκ", "ανωνυμο", "διαγραφ", "περίοδος"
]

def _expand_query(q: str) -> str:
    s = (q or "").lower()
    extra = []
    if "ελαχισ" in s:
        extra += ["data minimization", "ελαχιστοποίηση δεδομένων"]
    if "διατήρησ" in s or "περίοδο" in s or "retention" in s:
        extra += ["data retention"]
    return (q + " " + " ".join(extra)).strip()

def _tokenize(text: str) -> List[str]:
    # Απλά tokens με ελληνικά
    return re.findall(r"[A-Za-zΑ-Ωα-ω0-9άέήίόύώϊϋΐΰ]+", text.lower())

def _clean_markdown(text: str) -> str:
    # βγάζει headers/κώδικα, κρατά bullets/απλό κείμενο
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            lines.append("")  # κρατάμε κενές για παραγράφους
            continue
        if s.startswith("#"):        # headings έξω
            continue
        if s.startswith("```"):      # code fences έξω
            continue
        s = re.sub(r"[*_`>]+", "", s)   # απλός καθαρισμός markup
        lines.append(s)
    # συμπύκνωση πολλαπλών κενών γραμμών
    out, blank = [], False
    for s in lines:
        if s == "":
            if not blank:
                out.append("")
            blank = True
        else:
            out.append(s)
            blank = False
    return "\n".join(out).strip()

def _split_paragraphs(text: str, min_len: int = 40, max_len: int = 500) -> List[str]:
    paras = re.split(r"\n\s*\n", text)
    chunks, cur = [], ""
    for p in paras:
        p = p.strip()
        if not p:
            continue
        # ενώσε μικρές παραγράφους μέχρι max_len
        if len(cur) + len(p) + 1 <= max_len:
            cur = (cur + "\n" + p).strip()
        else:
            if len(cur) >= min_len:
                chunks.append(cur)
            cur = p
    if len(cur) >= min_len:
        chunks.append(cur)
    return chunks

def _build_index():
    global _snippets, _bm25
    _snippets = []
    docs_dir = os.path.join(os.getcwd(), "docs")
    for root, _, files in os.walk(docs_dir):
        for fn in files:
            if fn.lower().endswith((".md", ".txt")):
                path = os.path.join(root, fn)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        raw = f.read()
                    cleaned = _clean_markdown(raw)
                    _snippets.extend(_split_paragraphs(cleaned))
                except Exception:
                    pass
    tokenized = [_tokenize(s) for s in _snippets] if _snippets else []
    _bm25 = BM25Okapi(tokenized) if tokenized else None

def _ensure_index():
    if _bm25 is None:
        _build_index()

def _best_sentences(snippet: str, query: str, max_sents: int = 2) -> str:
    # Βρες προτάσεις μέσα στο snippet που ταιριάζουν σε hints ή query
    sents = re.split(r"(?<=[.!;…])\s+|\n", snippet)
    qs = set([t for t in _tokenize(query) if len(t) >= 4])
    def score(sent: str) -> int:
        sc = sum(h in sent.lower() for h in RETENTION_HINTS)
        sc += sum(1 for t in qs if t in sent.lower())
        return sc
    ranked = sorted((s for s in sents if len(s.strip()) >= 20), key=score, reverse=True)
    picked = [s.strip() for s in ranked[:max_sents] if score(s) > 0]
    return "\n".join(picked) if picked else snippet

def docs_search(query: str, top_k: int = 3) -> List[str]:
    """Offline αναζήτηση στα docs/ (BM25) με καθαρισμό markdown και στοχευμένα αποσπάσματα."""
    _ensure_index()
    if not _bm25 or not _snippets:
        return []
    q_tokens = _tokenize(_expand_query(query))
    scores = _bm25.get_scores(q_tokens)
    idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:max(1, top_k)]
    results = []
    for i in idxs:
        sn = _snippets[i]
        focused = _best_sentences(sn, query, max_sents=2)
        results.append(focused)
    return results
