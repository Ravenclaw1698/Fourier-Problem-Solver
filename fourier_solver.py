#!/usr/bin/env python3
"""
Fourier Series Step-by-Step Solver
Now uses OpenRouter FREE API instead of Anthropic
"""

import os
import json
import sys

try:
    from openai import OpenAI
except ImportError:
    print("Installing openai library...")
    os.system(f"{sys.executable} -m pip install openai -q")
    from openai import OpenAI


# ── ANSI colors ─────────────────────────────────────────
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


# Free models to try in order — if one is rate-limited, the next is used
FREE_MODELS = [
    "google/gemma-3-27b-it:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
]

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
]


def clear_line():
    print("\r" + " " * 70 + "\r", end="", flush=True)


def hr(char="─", color=C.DIM):
    print(f"{color}{char * 64}{C.RESET}")


def banner():
    print()
    print(f"{C.CYAN}{C.BOLD}{'═' * 64}{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}   ♾  Fourier Series Step-by-Step Solver{C.RESET}")
    print(f"{C.DIM}   Powered by OpenRouter (Free Models){C.RESET}")
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
    interval = input(f"  {C.CYAN}Interval:{C.RESET} ").strip()
    stype, type_label = choose_series_type()
    ctx = input(f"  {C.CYAN}Extra context:{C.RESET} ").strip()
    return func, interval, stype, type_label, ctx


def build_prompt(func, interval, type_label, ctx):
    extra = f"Additional context: {ctx}" if ctx else ""
    return f"""You are a mathematics tutor. Solve this Fourier Series problem with FULL working, showing every calculation in detail.

Problem:
  f(x) = {func}
  Interval: {interval}
  Series type: {type_label}
  {extra}

You MUST include ALL of the following steps (each as a separate object):
  1. Identify the function and interval; state L and the period T = 2L
  2. Write the general Fourier Series formula for this type
  3. Compute a0: write the integral, evaluate it fully showing every integration step
  4. Compute an: write the integral, apply integration by parts or standard technique, simplify fully
  5. Compute bn: write the integral, evaluate fully (if applicable for the series type)
  6. Simplify coefficients — substitute n values, identify patterns (even/odd n), cancel terms
  7. Write the final Fourier Series with the computed coefficients substituted in

Rules:
- For each step, show the FULL integral setup AND evaluation — do not skip algebra
- Use plain ASCII math (no LaTeX backslashes): use sin(nx), cos(nx), pi, integral notation like int_a^b
- DO NOT return fewer than 6 steps
- Return ONLY a valid JSON array. No markdown, no code fences, no text outside the array.

Each element must be an object with EXACTLY these keys:
  "title"       : step name (string)
  "explanation" : full working for this step — every line of algebra (string, at least 3 sentences)
  "math"        : the key formula or final result of this step (string)

JSON array format (start immediately with '[', end with ']'):
[
  {{"title": "Step name", "explanation": "Full detailed working...", "math": "formula"}},
  ...
]"""


def render_solution(steps):
    print()
    hr("═", C.CYAN)
    print(f"{C.CYAN}{C.BOLD}  Solution{C.RESET}")
    hr("═", C.CYAN)

    for i, step in enumerate(steps, 1):
        print(f"\n{C.BLUE}{C.BOLD}  Step {i}: {step.get('title','')}{C.RESET}")
        hr("─", C.DIM)
        print(step.get("explanation", ""))
        if step.get("math"):
            print(f"\n{C.YELLOW}{step['math']}{C.RESET}")


def solve(client, func, interval, type_label, ctx):
    prompt = build_prompt(func, interval, type_label, ctx)

    raw = None
    for model in FREE_MODELS:
        print(f"\n{C.DIM}  Trying {model} ...{C.RESET}")
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            raw = completion.choices[0].message.content
            print(f"{C.GREEN}  ✓ Using {model}{C.RESET}")
            break  # success — stop trying
        except Exception as e:
            err = str(e)
            if "429" in err or "rate" in err.lower():
                print(f"{C.YELLOW}  Rate-limited, trying next model...{C.RESET}")
            else:
                print(f"{C.RED}  API Error: {e}{C.RESET}")
                return

    if raw is None:
        print(f"{C.RED}  All models are rate-limited. Please wait a minute and try again.{C.RESET}")
        return

    clean = raw.strip()

    # Strip markdown code fences if model wrapped response in ```json ... ```
    if clean.startswith("```"):
        lines = clean.splitlines()
        clean = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        clean = clean.strip()

    # If there's preamble text, find the JSON array
    start = clean.find("[")
    end   = clean.rfind("]")
    if start != -1 and end != -1 and end > start:
        clean = clean[start:end+1]

    try:
        steps = json.loads(clean)
        if not isinstance(steps, list) or len(steps) == 0:
            raise ValueError("Empty or non-list JSON")
    except Exception as ex:
        print(f"{C.YELLOW}  JSON parse failed ({ex}). Raw output:{C.RESET}")
        print(raw[:1200])
        return

    render_solution(steps)


def main():
    banner()

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        api_key = input("Enter OpenRouter API key: ").strip()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    while True:
        result = show_presets()
        if result is None:
            result = get_input()
        func, interval, stype, type_label, ctx = result

        solve(client, func, interval, type_label, ctx)

        if input("\nAgain? (y/n): ").lower() != "y":
            break


if __name__ == "__main__":
    main()