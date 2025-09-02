\# GDPR Micro-Auditor (2 agents / 2 tools)



Μικρό multi-agent σύστημα για ελέγχους GDPR:

\- \*\*Agent Router\*\*: αποφασίζει `pii` / `docs` / `general`.

\- \*\*Agent Worker\*\*: εκτελεί το task και καλεί τα εργαλεία.

\- \*\*Tool 1 — DocsRAG (offline)\*\*: keyword RAG πάνω σε τοπικά αρχεία `docs/` με BM25.

\- \*\*Tool 2 — PII Checker\*\*: απλοί κανόνες/regex για PII + checklist ελλείψεων πολιτικής.



\## 1) Προαπαιτούμενα

\- Python 3.10+

\- Windows CMD/PowerShell (ή macOS/Linux shell)

\- (Προαιρετικά) VS Code



\## 2) Εγκατάσταση

```bash

\# δημιουργία venv

python -m venv .venv

\# ενεργοποίηση (Windows)

.\\.venv\\Scripts\\activate



\# βιβλιοθήκες

pip install -r requirements.txt

pip install rank-bm25



