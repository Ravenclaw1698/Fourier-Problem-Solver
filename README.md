# ♾ Local Fourier Series Solver

A fully **offline**, **step-by-step** Fourier series calculator powered by [SymPy](https://www.sympy.org/).  
No API. No internet. No subscription. Everything runs locally on your machine.

---

## Features

- **Parity detection first** — checks if your function is even or odd *before* computing, then applies the correct simplified formulas automatically
- **Full step-by-step working** — shows the integrand, the raw integral result, and the simplified coefficient at every stage
- **All standard problem types** supported (see below)
- **Piecewise function input** — define functions like `f(x) = { -x, x<0 ; x, x≥0 }` interactively
- **Series identity verification** — substitute a specific `x` value to prove identities like `1 - 1/4 + 1/9 - … = π²/12`
- Pure Python — only requires `sympy`

---

## Requirements

```
Python 3.8+
sympy
```

Install SymPy if you don't have it:

```bash
pip install sympy
```

---

## Usage

```bash
python local.py
```

You will be presented with a menu:

```
═══════════════════════════════════════════════════════════════════
  MAIN MENU
───────────────────────────────────────────────────────────────────
  [1]  Find the period of a function  (Problem 1 type)
  [2]  Full Fourier series  [-π,π] or custom interval/period
  [3]  Half-range cosine series  on [0, L]
  [4]  Half-range sine series    on [0, L]
  [5]  Series sum / identity verification  (Parseval, substitution)
  [6]  Function sketch & analysis
  [q]  Quit
═══════════════════════════════════════════════════════════════════
```

---

## Menu Options

### [1] Period Finder
Finds the fundamental period of functions built from `sin`, `cos`, or `tan`.

**Rules applied:**
| Function form | Period |
|---|---|
| `sin(Bx + C)`, `cos(Bx + C)` | `2π / │B│` |
| `tan(Bx + C)` | `π / │B│` |
| Sum / product of trig terms | LCM of individual periods |

**Example input:**
```
f(x) = 1952*cos(2025*x + 2026)**1971
```
**Output:** `T = 2π/2025`

---

### [2] Full Fourier Series
Expands `f(x)` as a full Fourier series with cosine **and** sine terms.

**Interval options:**
- Standard `[-π, π]` (period `2π`)
- Custom interval `[a, b]`
- Custom period `T` (interval becomes `[-T/2, T/2]`)

**Parity shortcuts applied automatically:**

| Parity | What gets skipped | Formula used |
|---|---|---|
| **Even** `f(-x) = f(x)` | All `bₙ = 0` (no sine integration) | `a₀, aₙ` via `(2/L)∫₀ᴸ` |
| **Odd** `f(-x) = -f(x)` | `a₀ = 0`, all `aₙ = 0` (no cosine integration) | `bₙ` via `(2/L)∫₀ᴸ` |
| **Neither** | Nothing skipped | Full `(1/L)∫₋ₗᴸ` for all three |

**Steps shown for each coefficient:**
1. The formula being applied
2. The integrand written out
3. The raw integral result (before the `1/L` or `2/L` factor)
4. The final simplified coefficient

**Example — `f(x) = x²` on `[-π, π]`:**
```
PARITY CHECK
  f(-x) = f(x)  →  f(x) is EVEN
  ✓  bₙ = 0 for all n  (no integration needed)
  ✓  a₀ = (2/L) ∫₀ᴸ f(x) dx
  ✓  aₙ = (2/L) ∫₀ᴸ f(x)·cos(nπx/L) dx

STEP 1 — Compute a₀
  a₀ = 2π²/3

STEP 2 — Compute aₙ
  aₙ = 4·(-1)ⁿ / n²

STEP 3 — bₙ
  f(x) is EVEN → bₙ = 0 ✓ (no integration needed)

RESULT
  f(x) ≈ π²/3 - 4cos(x) + cos(2x) - 4cos(3x)/9 + …
```

---

### [3] Half-Range Cosine Series
Expands `f(x)` defined on `[0, L]` using only cosine terms (even extension to `[-L, L]`).

**Formulas:**
```
a₀ = (2/L) ∫₀ᴸ f(x) dx
aₙ = (2/L) ∫₀ᴸ f(x)·cos(nπx/L) dx
bₙ = 0  (by construction)
```

---

### [4] Half-Range Sine Series
Expands `f(x)` defined on `[0, L]` using only sine terms (odd extension to `[-L, L]`).

**Formulas:**
```
a₀ = 0,  aₙ = 0  (by construction)
bₙ = (2/L) ∫₀ᴸ f(x)·sin(nπx/L) dx
```

**Example — `f(x) = cos(x)` on `[0, π]` as a sine series (Problem 19 type):**
```
b₂ = 8/(3π),   b₄ = 16/(15π),  …
f(x) ≈ 8sin(2x)/(3π) + 16sin(4x)/(15π) + …
```

---

### [5] Series Sum Verification
Computes the Fourier series and then:
- **Substitution**: set `x = x₀` to derive famous identities
- **Parseval's theorem**: equate `‖f‖²` with `a₀²/2 + Σ(aₙ² + bₙ²)`

**Example — prove `1 - 1/4 + 1/9 - … = π²/12`:**
```
f(x) = x/pi  on [-π, π],  substitute x = π
→  f(π) = 1  =  1 - 1/4 + 1/9 - 1/16 + …
```

---

### [6] Function Sketch & Analysis
For a given `f(x)` on `[a, b]`:
- Computes `f'(x)` and finds critical points
- Evaluates key values (`f(a)`, `f(0)`, `f(b)`)
- Detects parity (even / odd / neither)
- Prints the exact `sympy.plot(...)` command to generate a graph

---

## Piecewise Functions

Any menu option that accepts `f(x)` also accepts piecewise definitions.  
Select option `[2] Piecewise function` when prompted, then enter each piece as:

```
expression | condition
```

**Example — `f(x) = { -x, -π < x < 0 ; x, 0 ≤ x ≤ π }` (i.e. `|x|`):**
```
Piece 1: -x | (x >= -pi) & (x < 0)
Piece 2:  x | (x >= 0) & (x <= pi)
```

Use `&` for AND. Use `pi` for π, `e` for *e*, `Abs(x)` for |x|.

---

## Function Input Syntax

| Math | Type this |
|---|---|
| `x²` | `x**2` |
| `\|x\|` | `Abs(x)` |
| `eˣ` | `exp(x)` |
| `π` | `pi` |
| `sin²(x)` | `sin(x)**2` |
| `x(π − x)` | `x*(pi - x)` |
| `A − 4x/P` | `A - 4*x/P` *(use symbolic constants freely)* |

---

## Homework Problem Coverage

| Problem type | Menu option |
|---|---|
| Period of `cos¹⁹⁷¹(2025x+2026)` etc. | **[1]** |
| Fourier series on `[-π, π]` | **[2]** → option 1 |
| Fourier series on `[0, 2π]` | **[2]** → option 2, set `a=0, b=2*pi` |
| Fourier series with period 6 or 8 | **[2]** → option 3, enter `T=6` or `T=8` |
| Piecewise `f(x)` on any interval | **[2]** + piecewise input |
| Half-range cosine (even extension) | **[3]** |
| Half-range sine (odd extension) | **[4]** |
| Prove `1 − 1/4 + 1/9 − … = π²/12` | **[5]** |
| Sketch / analyse a function | **[6]** |

---

## Notes

- Computations can take a few seconds for complex functions — SymPy performs exact symbolic integration.
- If SymPy cannot evaluate an integral in closed form it will return an unevaluated `Integral(...)` object.
- For graphical plots, install `matplotlib` (`pip install matplotlib`) and use the command printed by option [6].
