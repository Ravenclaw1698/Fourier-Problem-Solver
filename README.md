# ♾ Fourier Series Step-by-Step Solver

A terminal-based Python tool that solves Fourier Series problems with full step-by-step mathematical working — powered by **free AI models via [OpenRouter](https://openrouter.ai)**.

No web browser needed. Just run it in your terminal, enter a function, and get a detailed solution printed right there.

---

## What it does

- Accepts any mathematical function as input (e.g. `x^2`, `pi - x`, `|x|`, `cos(x)`, piecewise functions)
- Supports all major Fourier series types
- Shows every step: identifying parameters, computing a₀, aₙ, bₙ, integration by parts, and the final series
- Comes with 7 built-in presets from a real MAT216 worksheet
- Automatically falls back to another free model if one is rate-limited
- Loops so you can solve multiple problems in one session
- Color-coded terminal output for easy reading

---

## Supported series types

| Type | Description |
|------|-------------|
| General Fourier Series | For any function on (−L, L) |
| Even Function — Cosine Series | When f(x) is even on (−L, L) |
| Odd Function — Sine Series | When f(x) is odd on (−L, L) |
| Half-Range Cosine Series | For f(x) defined on (0, L) |
| Half-Range Sine Series | For f(x) defined on (0, L) |

---

## Requirements

- Python 3.7 or higher
- A **free** OpenRouter API key → get one at [openrouter.ai/keys](https://openrouter.ai/keys) (sign up with Google or GitHub)

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/Ravenclaw1698/Fourier-Problem-Solver.git
cd Fourier-Problem-Solver
```

**2. Install the dependency**

```bash
pip install openai
```

> The script will also auto-install `openai` on first run if it's missing.

**3. (Optional) Set your API key as an environment variable**

On Linux / macOS:
```bash
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

On Windows (Command Prompt):
```cmd
set OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

On Windows (PowerShell):
```powershell
$env:OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

> If you skip this step, the script will ask you to paste the key when it starts.

---

## Usage

```bash
python fourier_solver.py
```

You will see a menu like this:

```
════════════════════════════════════════════════════════════════
   ♾  Fourier Series Step-by-Step Solver
   Powered by OpenRouter (Free Models)
════════════════════════════════════════════════════════════════

Enter OpenRouter API key: <paste your key>

Quick presets:
   1. π − x  on (−π, π)
   2. |x|    on (−π, π)
   3. x²     on (−π, π)
   4. x²     on (−3, 3)
   5. x      on (−1, 5), period 6
   6. cos x  (half-range sine)
   7. x      on (0, 2) (half cosine)
   0. Enter manually

Select preset (0 to type manually):
```

### Option A — Use a preset

Pick a number from `1` to `7` to instantly solve a standard example.

### Option B — Enter manually

Pick `0` and provide:
- The function, e.g. `pi - x` or `x^2` or `|x|`
- The interval, e.g. `-pi to pi` or `0 to 3`
- The series type (pick from numbered menu)
- Optional extra context (e.g. for piecewise functions)

---

## Example output

```
════════════════════════════════════════════════════════════════
  Solution
════════════════════════════════════════════════════════════════

  Step 1: Identify parameters
──────────────────────────────────────────────────────────────
  The function f(x) = π − x is defined on (−π, π),
  so L = π and the period is 2π.

    L = π,   interval = (−π, π),   period = 2π

  Step 2: State the Fourier formula
──────────────────────────────────────────────────────────────
  Since no special symmetry applies, we use the general formula.

    f(x) = a₀/2 + Σ [aₙ cos(nπx/L) + bₙ sin(nπx/L)]

  Step 3: Compute a₀
──────────────────────────────────────────────────────────────
  Integrate f(x) over one full period and divide by L.

    a₀ = (1/π) ∫[-π to π] (π − x) dx
       = (1/π) [πx − x²/2] from −π to π
       = (1/π) [(π² − π²/2) − (−π² + π²/2)]
       = (1/π) · π² = π

  ...

  Step 7: Final Fourier Series
──────────────────────────────────────────────────────────────
  Substituting all computed coefficients:

    f(x) = π/2 + 2 Σ (1/n) sin(nx),   n = 1, 2, 3, ...
```

---

## Input format tips

| What you want | How to type it |
|---------------|----------------|
| π | `pi` |
| x² | `x^2` |
| \|x\| | `|x|` |
| sin(x), cos(x) | `sin(x)`, `cos(x)` |
| eˣ | `e^x` |
| Piecewise function | Use the "extra context" field, e.g. `f(x) = -x for x < 0, x for x >= 0` |
| Interval −π to π | `-pi to pi` |
| Interval 0 to 2π | `0 to 2pi` |

---

## How it works

1. You pick a preset or enter a function, interval, and series type
2. The script builds a structured prompt describing the problem
3. It sends the prompt to a **free AI model** via the OpenRouter API
4. The model returns a JSON array of steps (title, explanation, math working)
5. The script parses and renders each step with color formatting in your terminal

The tool does **not** compute integrals locally — the AI model performs all mathematical reasoning and returns fully worked solutions.

### Free models used (in priority order)

If one model is rate-limited, the script automatically tries the next:

1. `google/gemma-3-27b-it:free`
2. `nousresearch/hermes-3-llama-3.1-405b:free`
3. `meta-llama/llama-3.3-70b-instruct:free`
4. `nvidia/nemotron-3-super-120b-a12b:free`
5. `meta-llama/llama-3.2-3b-instruct:free`

---

## File structure

```
Fourier-Problem-Solver/
├── fourier_solver.py   # Main script
└── README.md           # This file
```

---

## Course context

This tool was built as a study aid for **MAT216: Linear Algebra and Fourier Analysis** at BRAC University. The presets are taken directly from the MAT216 homework sheet on Fourier Series, Even/Odd functions, and Half-Range Series.

---

## License

MIT License — free to use, modify, and distribute.

---

## Acknowledgements

- [OpenRouter](https://openrouter.ai) for providing access to free AI models
- MAT216 course material, Department of Mathematics and Natural Sciences, BRAC University
