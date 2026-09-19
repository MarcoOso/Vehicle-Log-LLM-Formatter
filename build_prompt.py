"""
build_prompt.py

Demonstrates the final step: turning a cleaned LLM-ready event chunk into
an actual prompt suitable for sending to an LLM (e.g. for automated fault
diagnosis, anomaly explanation, or maintenance-report generation).

This intentionally does NOT call a live LLM API (no key required to run
this project) — it prints exactly the prompt string that *would* be sent,
so the formatting logic itself is the deliverable and stays runnable by
anyone without needing credentials.
"""

import json

EVENTS_PATH = "output/llm_ready_events.json"

SYSTEM_PROMPT = (
    "You are an automotive diagnostics assistant. You will be given a "
    "structured JSON summary of a single diagnostic trouble code (DTC) "
    "event, including sensor readings at the moment of the event and "
    "summarized sensor behavior in the seconds immediately before and "
    "after. Explain in plain language what likely happened and what a "
    "technician should check first."
)


def build_prompt_for_event(event: dict) -> str:
    """Combine a system instruction with a single structured event chunk,
    formatted as labeled JSON the model can parse unambiguously."""
    user_content = (
        f"DTC Event Data:\n"
        f"{json.dumps(event, indent=2)}\n\n"
        f"Question: What is the most likely cause of this fault code, and "
        f"what should be inspected first?"
    )
    return f"[SYSTEM]\n{SYSTEM_PROMPT}\n\n[USER]\n{user_content}"


def main():
    with open(EVENTS_PATH) as f:
        events = json.load(f)

    if not events:
        print("No events found — run clean_and_format.py first.")
        return

    # Show the first event as a worked example
    prompt = build_prompt_for_event(events[0])
    print(prompt)
    print(f"\n\n--- ({len(events)} total events available; this shows event 1) ---")


if __name__ == "__main__":
    main()
