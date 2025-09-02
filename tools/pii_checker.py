import re
from typing import Dict, List

# Απλά regex για πιθανά PII (ενδεικτικά)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?(?:\d{10,})")
IBAN_RE = re.compile(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}")
ID_RE = re.compile(r"\b[A-Z]{1,2}\d{5,10}\b")

# Μικρή checklist για πολιτικές/κείμενα GDPR
CHECKLIST = [
    "Αναφέρεται ρητά ο σκοπός επεξεργασίας;",
    "Υπάρχει νόμιμη βάση (π.χ. συναίνεση, σύμβαση);",
    "Περιγράφεται χρόνος διατήρησης;",
    "Περιγράφονται δικαιώματα υποκειμένου (πρόσβαση, διόρθωση, διαγραφή);",
]

def check_pii(text: str) -> Dict[str, List[str]]:
    """Εντοπίζει απλά PII και επιστρέφει τι λείπει από βασική GDPR checklist."""
    pii = []
    pii += [f"email: {m}" for m in EMAIL_RE.findall(text)]
    pii += [f"phone: {m}" for m in PHONE_RE.findall(text) if len(m) >= 10]
    pii += [f"iban: {m}" for m in IBAN_RE.findall(text)]
    pii += [f"id: {m}" for m in ID_RE.findall(text)]

    # Τι λείπει από το κείμενο, πολύ απλά/ενδεικτικά
    lower = text.lower()
    missing = []
    if not any(k in lower for k in ["σκοπ", "purpose"]):
        missing.append(CHECKLIST[0])
    if not any(k in lower for k in ["νομική βάση", "legal basis", "συναίνεσ", "consent", "σύμβασ", "contract"]):
        missing.append(CHECKLIST[1])
    if not any(k in lower for k in ["διατήρησ", "retention", "χρόνο", "διάρκ", "period"]):
        missing.append(CHECKLIST[2])
    if not any(k in lower for k in ["δικαιώμα", "rights", "πρόσβαση", "διαγραφή", "διόρθωσ"]):
        missing.append(CHECKLIST[3])

    return {"pii_hits": pii, "checklist_missing": missing}
