from config import get_llm
from tools.docs_rag import docs_search
from tools.pii_checker import check_pii
import json
import re


def work(task: str, user_input: str) -> str:
    llm = get_llm()

    # --- DOCS (RAG) ---
    if task == "docs":
        snippets = docs_search(user_input, top_k=5)
        if not snippets:
            return "Δεν βρέθηκαν σχετικά αποσπάσματα στα docs."

        # Αριθμημένα αποσπάσματα για το LLM
        numbered = "\n\n".join([f"[{i}] {s}" for i, s in enumerate(snippets)])
        prompt = (
            "Είσαι ελεγκτής GDPR. Μίλα ΜΟΝΟ στα Ελληνικά.\n"
            "Σου δίνω αποσπάσματα με δείκτες [i]. Θέλω να επιστρέψεις ΑΥΣΤΗΡΑ JSON:\n"
            '{"quotes":[{"i":<αριθμός>,"quote":"<αυτούσιο 30–160 χαρ.>","expl":"<έως 12 λέξεις>"}]}\n'
            "ΚΑΝΟΝΕΣ:\n"
            "- Δώσε ΑΚΡΙΒΩΣ 3 αντικείμενα στο array.\n"
            "- Κάθε 'quote' πρέπει να είναι ΑΥΤΟΥΣΙΟ κομμάτι του αποσπάσματος με δείκτη i (όχι παραφράσεις), 30–160 χαρακτήρες.\n"
            "- 'expl' σε καθαρά Ελληνικά, έως 12 λέξεις, χωρίς νέες γραμμές, χωρίς χρονικά όρια.\n\n"
            f"Αποσπάσματα:\n{numbered}\n\n"
            f"Ερώτημα:\n{user_input}\n\n"
            "ΕΠΙΣΤΡΕΨΕ ΜΟΝΟ JSON, τίποτα άλλο."
        )

        raw = (llm.invoke(prompt).content or "").strip()
        m = re.search(r"\{.*\}", raw, flags=re.S)
        raw_json = m.group(0) if m else raw

        items = []
        try:
            data = json.loads(raw_json)
            items = data.get("quotes", [])[:3]
        except Exception:
            items = []

        lines = []
        for item in items:
            try:
                i = int(item.get("i", 0))
                quote = str(item.get("quote", "")).strip()
                expl = str(item.get("expl", "")).strip()
                src = snippets[i] if 0 <= i < len(snippets) else ""
                # Επικύρωση: το quote πρέπει να υπάρχει στο αντίστοιχο απόσπασμα
                if quote and expl and quote in src:
                    lines.append(f"• «{quote}» — {expl}")
            except Exception:
                pass

        # Fallback: αν δεν έχουμε 3 έγκυρα bullets, συμπλήρωσε από τα ίδια τα αποσπάσματα
        while len(lines) < 3 and snippets:
            sn = snippets[len(lines) % len(snippets)].strip()
            first_line = sn.split("\n")[0][:160] if sn else "—"
            lines.append(f"• «{first_line}» — απόσπασμα σχετικό με το ερώτημα.")

        return "\n".join(lines[:3])

    # --- PII ---
    elif task == "pii":
        findings = check_pii(user_input)
        pii_list = findings.get("pii_hits", [])
        missing = findings.get("checklist_missing", [])

        pii_text = ", ".join(pii_list) if pii_list else "—"
        miss_text = "; ".join(missing) if missing else "—"

        prompt = (
            "Είσαι ελεγκτής GDPR. Μίλα ΜΟΝΟ στα Ελληνικά.\n"
            "Παρήγαγε ΣΥΝΤΟΜΗ αναφορά σε 3 bullets με ΑΥΤΟ το αυστηρό format:\n"
            "• PII: <λίστα ή '—'>\n"
            "• Ελλείψεις: <λίστα ή '—'>\n"
            "• Συστάσεις (3): 1) ..., 2) ..., 3) ...\n"
            "Κανόνες:\n"
            "- ΜΗΝ επαναλαμβάνεις ιδέες ή φράσεις.\n"
            "- ΜΗΝ εισάγεις αυθαίρετα χρονικά όρια ή διαδικασίες αν δεν υπάρχουν στο κείμενο.\n"
            "- Οι συστάσεις να είναι πρακτικές και γενικές (όχι SLA), 1 γραμμή η καθεμία.\n\n"
            f"PII (από κανόνες): {pii_text}\n"
            f"Ελλείψεις (checklist): {miss_text}\n"
        )
        return llm.invoke(prompt).content

    # --- GENERAL ---
       # --- GENERAL ---
    else:
        # Ανίχνευση ειδικής περίπτωσης: "ελαχισ(τοποίηση)" -> κατεύθυνση στο θέμα data minimization
        topic_hint = ""
        s = (user_input or "").lower()
        if "ελαχισ" in s or "minimiz" in s:
            topic_hint = "Θέμα: αρχή ελαχιστοποίησης δεδομένων (data minimization) στο GDPR."

        # Ζήτα αυστηρά JSON για να αποφύγουμε φλυαρία/επαναλήψεις
        prompt = (
            "Μίλα ΜΟΝΟ στα Ελληνικά.\n"
            "Δώσε ΑΚΡΙΒΩΣ 3 σύντομα, εφαρμόσιμα βήματα συμμόρφωσης GDPR για το ερώτημα μου.\n"
            "Κανόνες:\n"
            "- Επέστρεψε ΑΥΣΤΗΡΑ JSON της μορφής: {\"steps\":[\"...\",\"...\",\"...\"]}\n"
            "- Κάθε βήμα 10–16 λέξεις, πρακτικό, χωρίς επαναλήψεις, χωρίς αοριστίες/τεχνικές φλυαρίες.\n"
            "- Εστίασε σε σκοπό/νομική βάση, διαφάνεια/opt-in, καταγραφή συναίνεσης, ανάκληση, ελαχιστοποίηση, διατήρηση/διαγραφή.\n"
            "- Μην αριθμήσεις, μην προσθέσεις κείμενο εκτός JSON, μην δίνεις παραγράφους.\n\n"
            f"{topic_hint}\n"
            f"Ερώτημα:\n{user_input}\n"
        )
        raw = llm.invoke(prompt).content or ""

        # Post-processing: κράτα ΜΟΝΟ JSON και από εκεί ΑΚΡΙΒΩΣ 3 βήματα
        import json, re
        m = re.search(r"\{.*\}", raw, flags=re.S)
        raw_json = m.group(0) if m else raw
        steps = []
        try:
            data = json.loads(raw_json)
            steps = [str(x).strip() for x in (data.get("steps", []) or []) if str(x).strip()]
        except Exception:
            steps = []

        # Αν το μοντέλο δεν τήρησε το format, δώσε ασφαλές fallback (χειροκίνητο)
        if len(steps) < 3:
            steps = [
                "Συλλέξτε μόνο απολύτως αναγκαία πεδία για τον δηλωμένο σκοπό επεξεργασίας.",
                "Παρέχετε σαφή ενημέρωση, granular opt-in και εύκολη ανάκληση∙ καταγράψτε τη συναίνεση.",
                "Ορίστε περίοδο διατήρησης, διαδικασία διαγραφής/ανωνυμοποίησης και στοιχεία επικοινωνίας/DPO.",
            ]

        # Κανονικοποίηση: επέστρεψε ακριβώς 3 αριθμημένα βήματα
        steps = steps[:3]
        return "\n".join(f"{i}) {steps[i-1]}" for i in range(1, 4))

