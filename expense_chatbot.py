import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env


def read_expense_report() -> str:
    filepath = "expenses.csv"
    print(f"=== Expense Report Analyzer ===")
    print(f"Loading report from {filepath}...\n")
    with open(filepath, "r") as f:
        return f.read()


def chat(expense_report: str) -> None:
    print("\n✓ Report loaded! Ask me anything about it. Type 'quit' to exit.\n")

    messages = []

    # The system prompt holds the expense report with cache_control.
    # Because the report never changes across turns, Claude API caches it
    # after the first request — subsequent questions are ~90% cheaper.
    system = [
        {
            "type": "text",
            "text": (
                "You are an expert financial analyst who specializes in expense reports. "
                "Answer questions clearly and concisely. Calculate totals when asked, "
                "identify the biggest expenses, flag unusual items, and give actionable insights.\n\n"
                f"EXPENSE REPORT:\n{expense_report}"
            ),
            "cache_control": {"type": "ephemeral"},
        }
    ]

    while True:
        question = input("You: ").strip()

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": question})

        print("Assistant: ", end="", flush=True)
        response_text = ""

        with client.messages.stream(
            model="claude-opus-4-7",
            max_tokens=1024,
            system=system,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                response_text += text

        print("\n")
        messages.append({"role": "assistant", "content": response_text})


def main():
    expense_report = read_expense_report()

    if not expense_report.strip():
        print("No report provided. Exiting.")
        return

    chat(expense_report)


if __name__ == "__main__":
    main()
