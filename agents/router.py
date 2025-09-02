def route(user_input: str) -> str:
    """Κανόνες ταξινόμησης: 'pii' / 'docs' / 'general'."""
    s = (user_input or "").lower()

    # PII: email, τηλέφωνο, IBAN, κ.λπ.
    pii_kw = ["pii", "@", "email", "e-mail", "τηλεφ", "iban", "ταυτότ", "id ", "αφμ"]
    if any(k in s for k in pii_kw):
        return "pii"

    # DOCS: ζητά πληροφορία από σημειώσεις/έγγραφα ή GDPR έννοιες
    docs_kw = [
        "τι αναφέρει", "τι λέει", "docs", "σημειώ", "checklist", "βρες", "αναζήτ",
        "περίοδος διατήρησης", "νομική βάση", "δικαιώματα υποκειμένου",
        "data retention", "retention"
    ]
    if any(k in s for k in docs_kw):
        return "docs"

    return "general"
