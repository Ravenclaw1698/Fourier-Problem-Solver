#!/usr/bin/env python3
"""
Fourier Series Step-by-Step Solver
Uses the Anthropic API to generate detailed solutions in the terminal.
"""

import os
import json
import sys

try:
    import anthropic
except ImportError:
    print("Installing anthropic library...")
    os.system(f"{sys.executable} -m pip install anthropic -q")
    import anthropic


# ── ANSI colors ────────────────────────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    CYAN   = "\033[96m"
    BLUE   = "\033[94m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    MAGENTA= "\033[95m"
    WHITE  = "\033[97m"


SERIES_TYPES = {
    "1": ("general",      "General Fourier Series"),
    "2": ("even",         "Even Function — Cosine Series"),
    "3": ("odd",          "Odd Function — Sine Series"),
    "4": ("half-cosine",  "Half-Range Cosine Series"),
    "5": ("half-sine",    "Half-Range Sine Series"),
}

PRESETS = [
    ("π − x  on (−π, π)",           "pi - x",    "-pi to pi",  "general",     ""),
    ("|x|    on (−π, π)",            "|x|",       "-pi to pi",  "even",        "piecewise: -x for x<0, x for x>=0"),
    ("x²     on (−π, π)",            "x^2",       "-pi to pi",  "general",     "use result to show π²/6 and π²/12"),
    ("x²     on (−3, 3)",            "x^2",       "-3 to 3",    "even",        ""),
    ("x      on (−1, 5), period 6",  "x",         "-1 to 5",    "general",     "period 6"),
    ("cos x  (half-range sine)",     "cos(x)",    "0 to pi",    "half-sine",   ""),
    ("x      on (0, 2) (half cosine)","x",         "0 to 2",     "half-cosine", ""),
    ("piecewise ±2  on (0, 2π)",     "piecewise", "0 to 2pi",   "general",
        "piecewise: f(x) = -2 for 0 <= x < pi, f(x) = 2 for pi <= x < 2pi"),
    ("x(π−x) on (0, π) — sine",     "x*(pi-x)",  "0 to pi",    "half-sine",   "use result to show π³/32"),
    ("3 sin x (half-range cosine)",  "3*sin(x)",  "0 to pi",    "half-cosine", ""),
]


def clear_line():
    print("\r" + " " * 70 + "\r", end="", flush=True)


def hr(char="─", color=C.DIM):
    print(f"{color}{char * 64}{C.RESET}")


def banner():
    print()
    print(f"{C.CYAN}{C.BOLD}{'═' * 64}{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}   ♾  Fourier Series Step-by-Step Solver{C.RESET}")
    print(f"{C.DIM}   Powered by Claude (Anthropic API){C.RESET}")
    print(f"{C.CYAN}{C.BOLD}{'═' * 64}{C.RESET}")
    print()


def choose_series_type():
    print(f"{C.BOLD}Series type:{C.RESET}")
    for k, (_, label) in SERIES_TYPES.items():
        print(f"  {C.YELLOW}{k}{C.RESET}. {label}")
    while True:
        choice = input(f"\n{C.BOLD}Select [1-5]: {C.RESET}").strip()
        if choice in SERIES_TYPES:
            return SERIES_TYPES[choice]
        print(f"{C.RED}  Please enter a number between 1 and 5.{C.RESET}")


def show_presets():
    print(f"\n{C.BOLD}Quick presets:{C.RESET}")
    for i, (label, *_) in enumerate(PRESETS, 1):
        print(f"  {C.YELLOW}{i:>2}{C.RESET}. {label}")
    print(f"  {C.YELLOW} 0{C.RESET}. Enter manually")
    while True:
        choice = input(f"\n{C.BOLD}Select preset (0 to type manually): {C.RESET}").strip()
        if choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(PRESETS):
            label, func, interval, stype, ctx = PRESETS[int(choice) - 1]
            _, type_label = next(v for v in SERIES_TYPES.values() if v[0] == stype)
            return func, interval, stype, type_label, ctx
        print(f"{C.RED}  Invalid choice.{C.RESET}")


def get_input():
    print(f"\n{C.BOLD}Manual input:{C.RESET}")
    func = input(f"  {C.CYAN}f(x) ={C.RESET} ").strip()
    if not func:
        print(f"{C.RED}  Function cannot be empty.{C.RESET}")
        return None
    interval = input(f"  {C.CYAN}Interval (e.g. -pi to pi):{C.RESET} ").strip()
    if not interval:
        print(f"{C.RED}  Interval cannot be empty.{C.RESET}")
        return None
    stype, type_label = choose_series_type()
    ctx = input(f"  {C.CYAN}Extra context (optional, press Enter to skip):{C.RESET} ").strip()
    return func, interval, stype, type_label, ctx


def build_prompt(func, interval, type_label, ctx):
    system = """You are an expert mathematics tutor specializing in Fourier Series.
Solve Fourier Series problems with complete, detailed step-by-step working.

Return your solution ONLY as a valid JSON array. No markdown, no extra text.
Each element is a step object with these keys:
  "title"       : short step heading (e.g. "Identify parameters", "Compute a₀")
  "explanation" : 1-3 sentence explanation of what you're doing and why
  "math"        : the mathematical working, using Unicode symbols (π ∫ Σ ∞ ² ³ √ ± ≠ ≤ ≥).
                  Write integrals as ∫[a to b] f(x) dx.
                  Separate equations with newlines.
                  Leave empty string "" if no math for this step.

Always include (where applicable):
1. Identify type, L value, period
2. State the Fourier formula being used
3. Check even/odd symmetry
4. Compute a₀ with full integration
5. Compute aₙ with full integration (include integration by parts if needed)
6. Compute bₙ with full integration
7. Write the complete final Fourier series
8. Any special deductions (π²/6, π³/32, etc.)

Be thorough. Show every integral evaluation step."""

    user = (
        f"Find the {type_label} for f(x) = {func} on the interval {interval}."
        + (f"\nAdditional info: {ctx}" if ctx else "")
    )
    return system, user


def render_solution(steps):
    print()
    hr("═", C.CYAN)
    print(f"{C.CYAN}{C.BOLD}  Solution{C.RESET}")
    hr("═", C.CYAN)

    for i, step in enumerate(steps, 1):
        print()
        # Step header
        print(f"{C.BLUE}{C.BOLD}  Step {i}: {step.get('title', '')}{C.RESET}")
        hr("─", C.DIM)

        # Explanation
        explanation = step.get("explanation", "").strip()
        if explanation:
            for line in explanation.splitlines():
                print(f"  {C.WHITE}{line}{C.RESET}")

        # Math block
        math = step.get("math", "").strip()
        if math:
            print()
            for line in math.splitlines():
                print(f"  {C.YELLOW}  {line}{C.RESET}")

    print()
    hr("═", C.CYAN)
    print(f"{C.GREEN}{C.BOLD}  ✓ Solution complete{C.RESET}")
    hr("═", C.CYAN)
    print()


def solve(client, func, interval, type_label, ctx):
    system, user = build_prompt(func, interval, type_label, ctx)

    print(f"\n{C.DIM}  Solving ", end="", flush=True)
    spinner = ["|", "/", "─", "\\"]
    import threading, time

    stop_spin = threading.Event()

    def spin():
        i = 0
        while not stop_spin.is_set():
            print(f"\r{C.DIM}  Generating solution {spinner[i % 4]}{C.RESET}", end="", flush=True)
            i += 1
            time.sleep(0.12)

    t = threading.Thread(target=spin, daemon=True)
    t.start()

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        raw = "".join(b.text for b in response.content if hasattr(b, "text"))
    finally:
        stop_spin.set()
        t.join()
        clear_line()

    # Parse JSON
    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    try:
        steps = json.loads(clean)
    except json.JSONDecodeError as e:
        print(f"{C.RED}  Failed to parse response: {e}{C.RESET}")
        print(f"{C.DIM}  Raw output:\n{raw[:500]}{C.RESET}")
        return

    render_solution(steps)


def main():
    banner()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print(f"{C.YELLOW}  No ANTHROPIC_API_KEY found in environment.{C.RESET}")
        api_key = input(f"  {C.BOLD}Enter your Anthropic API key: {C.RESET}").strip()
        if not api_key:
            print(f"{C.RED}  API key required. Exiting.{C.RESET}")
            sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    while True:
        print(f"\n{C.BOLD}{'─' * 64}{C.RESET}")
        print(f"{C.BOLD}New problem{C.RESET}  (or type {C.YELLOW}exit{C.RESET} to quit)")
        print(f"{'─' * 64}")

        use_preset = input(f"\n{C.BOLD}Use a preset example? [y/n]: {C.RESET}").strip().lower()
        if use_preset in ("exit", "quit", "q"):
            break

        if use_preset == "y":
            result = show_presets()
            if result is None:
                result = get_input()
        else:
            result = get_input()

        if result is None:
            continue

        func, interval, stype, type_label, ctx = result

        print(f"\n  {C.DIM}f(x) = {C.RESET}{C.WHITE}{C.BOLD}{func}{C.RESET}")
        print(f"  {C.DIM}Interval: {C.RESET}{C.WHITE}{interval}{C.RESET}")
        print(f"  {C.DIM}Type:     {C.RESET}{C.WHITE}{type_label}{C.RESET}")
        if ctx:
            print(f"  {C.DIM}Context:  {C.RESET}{C.WHITE}{ctx}{C.RESET}")

        try:
            solve(client, func, interval, type_label, ctx)
        except anthropic.AuthenticationError:
            print(f"{C.RED}  Authentication failed. Check your API key.{C.RESET}")
        except anthropic.APIConnectionError:
            print(f"{C.RED}  Connection error. Check your internet connection.{C.RESET}")
        except Exception as e:
            print(f"{C.RED}  Error: {e}{C.RESET}")

        again = input(f"\n{C.BOLD}Solve another problem? [y/n]: {C.RESET}").strip().lower()
        if again != "y":
            break

    print(f"\n{C.CYAN}  Goodbye!{C.RESET}\n")


if __name__ == "__main__":
    main()
