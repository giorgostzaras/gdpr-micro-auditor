from graph import build_graph

def main():
    app = build_graph()
    print("GDPR Micro-Auditor — 2 agents / 2 tools. Πληκτρολόγησε 'exit' για έξοδο.")
    while True:
        q = input("Εσύ: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        state = {"input": q, "task": "", "answer": ""}
        out = app.invoke(state)
        print("\nAgent:\n" + (out.get("answer") or "(χωρίς απάντηση)") + "\n")

if __name__ == "__main__":
    main()
