#!/usr/bin/env python3
"""
Local Fourier Series Solver — Comprehensive Edition
Handles all standard Fourier homework problem types using SymPy only. No API.
"""
import sympy as sp
import sys

# ─────────────────────────── symbols ────────────────────────────────────────
x = sp.Symbol('x')
n = sp.Symbol('n', integer=True, positive=True)

LOCALS = {
    'x': x, 'n': n, 'pi': sp.pi, 'e': sp.E,
    'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan, 'exp': sp.exp,
    'ln': sp.ln, 'log': sp.log, 'sqrt': sp.sqrt,
    'Abs': sp.Abs, 'abs': sp.Abs,
}

# ─────────────────────────── display helpers ─────────────────────────────────
W  = 65
SEP  = "═" * W
THIN = "─" * W

def hdr(title):
    print(f"\n{SEP}\n  {title}\n{SEP}")

def sec(title):
    print(f"\n{THIN}\n  {title}\n{THIN}")

def show(label, expr):
    print(f"  {label}\n    = {sp.pretty(expr, use_unicode=True)}\n")

def rule():
    print(THIN)

# ─────────────────────────── input helpers ────────────────────────────────────
def ask_expr(prompt):
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("  ✗ Cannot be empty.")
            continue
        try:
            return sp.sympify(raw, locals=LOCALS)
        except Exception as e:
            print(f"  ✗ Parse error: {e}")

def ask_num(prompt, default=None):
    raw = input(prompt).strip()
    if not raw and default is not None:
        return default
    try:
        return sp.sympify(raw, locals=LOCALS)
    except Exception as e:
        print(f"  ✗ {e}")
        return default

def ask_int(prompt, default=5):
    raw = input(prompt).strip()
    try:
        return int(raw) if raw else default
    except ValueError:
        return default

def ask_piecewise():
    """Build a SymPy Piecewise interactively."""
    print("\n  Enter pieces as:  expression | condition")
    print("  Examples:")
    print("    -x  | (x >= -pi) & (x < 0)")
    print("     x  | (x >= 0) & (x <= pi)")
    print("  Use & for AND. Press Enter on empty line when done.\n")
    pieces = []
    while True:
        raw = input(f"  Piece {len(pieces)+1} (Enter to finish): ").strip()
        if not raw:
            if len(pieces) == 0:
                print("  Need at least one piece.")
                continue
            break
        if '|' not in raw:
            print("  ✗ Must use format:  expression | condition")
            continue
        expr_s, cond_s = raw.rsplit('|', 1)
        try:
            ep = sp.sympify(expr_s.strip(), locals=LOCALS)
            cp = sp.sympify(cond_s.strip(), locals=LOCALS)
            pieces.append((ep, cp))
            print(f"     ✓ {ep}  when  {cp}")
        except Exception as e:
            print(f"  ✗ {e}")
    return sp.Piecewise(*pieces)

def ask_function():
    print("\n  [1] Single expression  (e.g. x**2, sin(x), Abs(x))")
    print("  [2] Piecewise function")
    c = input("  Choice [1]: ").strip() or "1"
    if c == "2":
        return ask_piecewise()
    return ask_expr("  f(x) = ")

# ─────────────────────────── core computation ────────────────────────────────
def _integrate_safe(expr, var, lo, hi):
    """Integrate and catch timeouts/errors gracefully."""
    try:
        return sp.integrate(expr, (var, lo, hi))
    except Exception as e:
        print(f"  ⚠ Integration warning: {e}")
        return sp.Integral(expr, (var, lo, hi))

def _check_parity(f, a, b):
    """
    Return 'even', 'odd', or 'neither' for f on [a,b].
    Only reliable for symmetric intervals (a = -b).
    """
    if sp.simplify(a + b) != 0:
        return 'neither'          # interval not symmetric — can't use shortcuts
    try:
        f_neg = sp.simplify(f.subs(x, -x))
        if sp.simplify(f_neg - f) == 0:
            return 'even'
        if sp.simplify(f_neg + f) == 0:
            return 'odd'
    except Exception:
        pass
    return 'neither'


def fourier_full(f, a, b, N=5):
    """
    Full Fourier series of f on [a, b] with period T = b-a.
    Parity is checked FIRST; simplified half-interval formulas are used
    when the interval is symmetric and f is even or odd.
    """
    L = sp.Rational(1, 2) * (b - a)   # half-period (symbolic)

    # ── PARITY CHECK (done before any integration) ───────────────────
    parity = _check_parity(f, a, b)

    sec("PARITY CHECK  (determines which coefficients vanish)")
    if parity == 'even':
        print("  f(-x) = f(x)  →  f(x) is EVEN\n")
        print("  Rules for EVEN functions on a symmetric interval [-L, L]:")
        print("    ✓  bₙ = 0  for all n  (sine terms vanish completely)")
        print("    ✓  a₀ = (2/L) ∫₀ᴸ f(x) dx          (integrate on half-interval)")
        print("    ✓  aₙ = (2/L) ∫₀ᴸ f(x)·cos(nπx/L) dx\n")
    elif parity == 'odd':
        print("  f(-x) = -f(x)  →  f(x) is ODD\n")
        print("  Rules for ODD functions on a symmetric interval [-L, L]:")
        print("    ✓  a₀ = 0  (integral of odd function over symmetric interval = 0)")
        print("    ✓  aₙ = 0  for all n  (cosine terms vanish completely)")
        print("    ✓  bₙ = (2/L) ∫₀ᴸ f(x)·sin(nπx/L) dx\n")
    else:
        print("  f(x) has NO special parity (or interval is not symmetric)\n")
        print("  Rules: must compute a₀, aₙ, and bₙ using the full interval.\n")

    # ════════════════════════════════════════════════════════════════
    #  EVEN  →  only cosine coefficients, use half-interval
    # ════════════════════════════════════════════════════════════════
    if parity == 'even':
        sec("STEP 1 — Compute a₀")
        print(f"  Formula (even shortcut):  a₀ = (2/L) ∫[0,{sp.simplify(L)}] f(x) dx\n")
        show("Integrand", f)
        raw_a0 = _integrate_safe(f, x, sp.Integer(0), L)
        show("∫ f(x) dx on [0, L] (raw)", raw_a0)
        a0 = sp.simplify(2 * raw_a0 / L)
        show("a₀ = 2·integral/L  (simplified)", a0)

        sec("STEP 2 — Compute aₙ  (cosine coefficients)")
        print(f"  Formula (even shortcut):  aₙ = (2/L) ∫[0,{sp.simplify(L)}] f(x)·cos(nπx/L) dx\n")
        ig_an = f * sp.cos(n * sp.pi * x / L)
        show("Integrand f(x)·cos(nπx/L)", ig_an)
        raw_an = _integrate_safe(ig_an, x, sp.Integer(0), L)
        show("∫ integrand dx on [0, L] (raw)", raw_an)
        an = sp.simplify(2 * raw_an / L)
        show("aₙ (simplified)", an)

        sec("STEP 3 — bₙ  (sine coefficients)")
        print("  f(x) is EVEN  →  bₙ = 0 for all n  ✓  (no integration needed)\n")
        bn = sp.Integer(0)

        sec(f"STEP 4 — Assemble partial series  (first {N} terms)")
        print("  f(x) ≈ a₀/2 + Σ aₙ·cos(nπx/L)  [bₙ = 0]\n")
        series = a0 / 2
        for k in range(1, N + 1):
            ak = sp.simplify(an.subs(n, k))
            term = sp.simplify(ak * sp.cos(k * sp.pi * x / L))
            series += term
            print(f"  n={k}:  a{k} = {sp.pretty(ak, use_unicode=True)},  "
                  f"term = {sp.pretty(term, use_unicode=True)}\n")

    # ════════════════════════════════════════════════════════════════
    #  ODD  →  only sine coefficients, use half-interval
    # ════════════════════════════════════════════════════════════════
    elif parity == 'odd':
        sec("STEP 1 — a₀")
        print("  f(x) is ODD  →  a₀ = 0  ✓  (no integration needed)\n")
        a0 = sp.Integer(0)

        sec("STEP 2 — aₙ  (cosine coefficients)")
        print("  f(x) is ODD  →  aₙ = 0 for all n  ✓  (no integration needed)\n")
        an = sp.Integer(0)

        sec("STEP 3 — Compute bₙ  (sine coefficients)")
        print(f"  Formula (odd shortcut):  bₙ = (2/L) ∫[0,{sp.simplify(L)}] f(x)·sin(nπx/L) dx\n")
        ig_bn = f * sp.sin(n * sp.pi * x / L)
        show("Integrand f(x)·sin(nπx/L)", ig_bn)
        raw_bn = _integrate_safe(ig_bn, x, sp.Integer(0), L)
        show("∫ integrand dx on [0, L] (raw)", raw_bn)
        bn = sp.simplify(2 * raw_bn / L)
        show("bₙ (simplified)", bn)

        sec(f"STEP 4 — Assemble partial series  (first {N} terms)")
        print("  f(x) ≈ Σ bₙ·sin(nπx/L)  [a₀ = aₙ = 0]\n")
        series = sp.Integer(0)
        for k in range(1, N + 1):
            bk = sp.simplify(bn.subs(n, k))
            term = sp.simplify(bk * sp.sin(k * sp.pi * x / L))
            series += term
            print(f"  n={k}:  b{k} = {sp.pretty(bk, use_unicode=True)},  "
                  f"term = {sp.pretty(term, use_unicode=True)}\n")

    # ════════════════════════════════════════════════════════════════
    #  NEITHER  →  full computation over [a, b]
    # ════════════════════════════════════════════════════════════════
    else:
        sec("STEP 1 — Compute a₀  (constant / DC term)")
        print(f"  Formula:  a₀ = (1/L) ∫ f(x) dx  over [{a}, {b}],  L = {sp.simplify(L)}\n")
        show("Integrand", f)
        raw_a0 = _integrate_safe(f, x, a, b)
        show("∫ f(x) dx (raw)", raw_a0)
        a0 = sp.simplify(raw_a0 / L)
        show("a₀ = raw / L  (simplified)", a0)

        sec("STEP 2 — Compute aₙ  (cosine coefficients)")
        print(f"  Formula:  aₙ = (1/L) ∫ f(x)·cos(nπx/L) dx  over [{a}, {b}]\n")
        ig_an = f * sp.cos(n * sp.pi * x / L)
        show("Integrand f(x)·cos(nπx/L)", ig_an)
        raw_an = _integrate_safe(ig_an, x, a, b)
        show("∫ integrand dx (raw)", raw_an)
        an = sp.simplify(raw_an / L)
        show("aₙ (simplified)", an)

        sec("STEP 3 — Compute bₙ  (sine coefficients)")
        print(f"  Formula:  bₙ = (1/L) ∫ f(x)·sin(nπx/L) dx  over [{a}, {b}]\n")
        ig_bn = f * sp.sin(n * sp.pi * x / L)
        show("Integrand f(x)·sin(nπx/L)", ig_bn)
        raw_bn = _integrate_safe(ig_bn, x, a, b)
        show("∫ integrand dx (raw)", raw_bn)
        bn = sp.simplify(raw_bn / L)
        show("bₙ (simplified)", bn)

        sec(f"STEP 4 — Assemble partial series  (first {N} terms)")
        print("  f(x) ≈ a₀/2 + Σ [ aₙ·cos(nπx/L) + bₙ·sin(nπx/L) ]\n")
        series = a0 / 2
        for k in range(1, N + 1):
            ak = sp.simplify(an.subs(n, k))
            bk = sp.simplify(bn.subs(n, k))
            term = sp.simplify(ak * sp.cos(k * sp.pi * x / L) +
                               bk * sp.sin(k * sp.pi * x / L))
            series += term
            print(f"  n={k}:")
            print(f"    a{k} = {sp.pretty(ak, use_unicode=True)}")
            print(f"    b{k} = {sp.pretty(bk, use_unicode=True)}")
            print(f"    term = {sp.pretty(term, use_unicode=True)}\n")

    return a0, an, bn, sp.simplify(series)


def fourier_cosine(f, L_val, N=5):
    """Half-range cosine series of f on [0, L_val]."""
    sec("STEP 1 — Compute a₀")
    print(f"  Formula:  a₀ = (2/L) ∫[0,{L_val}] f(x) dx\n")
    show("Integrand", f)
    raw_a0 = _integrate_safe(f, x, 0, L_val)
    show("∫ f(x) dx", raw_a0)
    a0 = sp.simplify(2 * raw_a0 / L_val)
    show("a₀ = 2·integral/L (simplified)", a0)

    sec("STEP 2 — Compute aₙ  (cosine coefficients)")
    print(f"  Formula:  aₙ = (2/L) ∫[0,{L_val}] f(x)·cos(nπx/L) dx\n")
    ig = f * sp.cos(n * sp.pi * x / L_val)
    show("Integrand", ig)
    raw_an = _integrate_safe(ig, x, 0, L_val)
    show("∫ integrand dx", raw_an)
    an = sp.simplify(2 * raw_an / L_val)
    show("aₙ (simplified)", an)

    sec(f"STEP 3 — Assemble cosine series  (first {N} terms)")
    print("  f(x) ≈ a₀/2 + Σ aₙ·cos(nπx/L)  (bₙ = 0 by even extension)\n")
    series = a0 / 2
    for k in range(1, N + 1):
        ak = sp.simplify(an.subs(n, k))
        term = sp.simplify(ak * sp.cos(k * sp.pi * x / L_val))
        series += term
        print(f"  n={k}:  a{k} = {sp.pretty(ak, use_unicode=True)},  "
              f"term = {sp.pretty(term, use_unicode=True)}\n")

    return a0, an, sp.Integer(0), sp.simplify(series)


def fourier_sine(f, L_val, N=5):
    """Half-range sine series of f on [0, L_val]."""
    sec("STEP 1 — Compute bₙ  (sine coefficients)")
    print(f"  Formula:  bₙ = (2/L) ∫[0,{L_val}] f(x)·sin(nπx/L) dx\n")
    ig = f * sp.sin(n * sp.pi * x / L_val)
    show("Integrand", ig)
    raw_bn = _integrate_safe(ig, x, 0, L_val)
    show("∫ integrand dx", raw_bn)
    bn = sp.simplify(2 * raw_bn / L_val)
    show("bₙ (simplified)", bn)

    sec(f"STEP 2 — Assemble sine series  (first {N} terms)")
    print("  f(x) ≈ Σ bₙ·sin(nπx/L)  (a₀ = aₙ = 0 by odd extension)\n")
    series = sp.Integer(0)
    for k in range(1, N + 1):
        bk = sp.simplify(bn.subs(n, k))
        term = sp.simplify(bk * sp.sin(k * sp.pi * x / L_val))
        series += term
        print(f"  n={k}:  b{k} = {sp.pretty(bk, use_unicode=True)},  "
              f"term = {sp.pretty(term, use_unicode=True)}\n")

    return sp.Integer(0), sp.Integer(0), bn, sp.simplify(series)


def parity_check(f):
    sec("Parity / Symmetry Check")
    try:
        f_neg = sp.simplify(f.subs(x, -x))
        if sp.simplify(f_neg - f) == 0:
            print("  f(x) is EVEN  →  all bₙ = 0  (pure cosine series)")
        elif sp.simplify(f_neg + f) == 0:
            print("  f(x) is ODD   →  a₀ = 0, all aₙ = 0  (pure sine series)")
        else:
            print("  f(x) has NO special parity  (both sine & cosine terms present)")
    except Exception:
        print("  (Parity check skipped for this function type)")


# ─────────────────────────── problem-type solvers ────────────────────────────

def menu_period():
    """Problem 1: Find the period of trig-based functions."""
    hdr("PERIOD FINDER")
    print("""
  Rules applied:
    sin(Bx+C), cos(Bx+C)  →  period = 2π / |B|
    tan(Bx+C)              →  period = π  / |B|
    f(x)^p with even p     →  period may halve (but standard = base period)
    Sum / product          →  LCM of individual periods

  Examples from homework:
    f(x) = 1952*cos(2025*x + 2026)**1971
    f(x) = 2025*sin(2025*x + 2026)**2024
    f(x) = 2025*tan(2024*x + 2023)**2025
""")
    f_expr = ask_expr("  f(x) = ")
    sec("Scanning for trig functions")

    found = []
    for sub in sp.preorder_traversal(f_expr):
        if isinstance(sub, (sp.sin, sp.cos, sp.tan)):
            arg = sub.args[0]
            B = arg.coeff(x)
            if B == 0:
                continue
            B_abs = sp.Abs(B)
            base = sp.pi / B_abs if isinstance(sub, sp.tan) else 2 * sp.pi / B_abs
            name = type(sub).__name__
            print(f"  {name}({arg})  →  B = {B},  base period = {sp.simplify(base)}")
            found.append(sp.simplify(base))

    if not found:
        print("  No trig functions detected. Function may not be periodic.")
        return

    if len(found) == 1:
        T = found[0]
    else:
        T = found[0]
        for p in found[1:]:
            T = sp.lcm(T, p)
        T = sp.simplify(T)

    sec("Result")
    print(f"  Period  T = {sp.pretty(T, use_unicode=True)}")
    try:
        print(f"          T ≈ {float(T):.6f}")
    except Exception:
        pass


def menu_full_fourier():
    """Full Fourier series — standard [-π,π] or custom interval/period."""
    hdr("FULL FOURIER SERIES")
    print("  [1]  Interval [-π, π]  (period 2π)")
    print("  [2]  Custom interval  [a, b]")
    print("  [3]  Custom period  T  (interval will be [-T/2, T/2])")
    c = input("  Choice [1]: ").strip() or "1"

    if c == "1":
        a_val, b_val = -sp.pi, sp.pi
    elif c == "2":
        print("  Enter interval endpoints (e.g.  0  and  2*pi):")
        a_val = ask_num("    a = ", default=-sp.pi)
        b_val = ask_num("    b = ", default=sp.pi)
    else:
        T = ask_num("  Period T = ", default=2 * sp.pi)
        a_val, b_val = -T / 2, T / 2

    print(f"\n  Interval: [{sp.simplify(a_val)}, {sp.simplify(b_val)}]"
          f"   L = {sp.simplify((b_val-a_val)/2)}   Period = {sp.simplify(b_val-a_val)}")

    f = ask_function()
    N = ask_int("  Terms to display [5]: ", 5)

    print("\n  Computing … (may take a moment for complex functions)\n")
    a0, an, bn, series = fourier_full(f, a_val, b_val, N)

    sec("RESULT — Fourier Series")
    print(f"  f(x) ≈  {sp.pretty(series, use_unicode=True)}\n")


def menu_half_range():
    """Half-range cosine or sine series on [0, L]."""
    hdr("HALF-RANGE FOURIER SERIES")
    print("""
  A half-range series expands f defined on [0, L] using only cosines or sines:
    • Cosine series: even extension to [-L, L]  →  a₀, aₙ only
    • Sine series  : odd  extension to [-L, L]  →  bₙ only
""")
    print("  [1]  Half-range Cosine series")
    print("  [2]  Half-range Sine series")
    c = input("  Choice [1]: ").strip() or "1"
    stype = "cosine" if c == "1" else "sine"

    L_val = ask_num("  Upper limit L of [0, L] = ", default=sp.pi)
    f = ask_function()
    N = ask_int("  Terms to display [5]: ", 5)

    print("\n  Computing …\n")
    if stype == "cosine":
        a0, an, bn, series = fourier_cosine(f, L_val, N)
    else:
        a0, an, bn, series = fourier_sine(f, L_val, N)

    sec(f"RESULT — Half-Range {stype.capitalize()} Series  on [0, {sp.simplify(L_val)}]")
    print(f"  f(x) ≈  {sp.pretty(series, use_unicode=True)}\n")


def menu_verify():
    """
    Compute series then substitute x=x₀ to derive sum identities
    e.g. prove  1 - 1/4 + 1/9 - … = π²/12
    """
    hdr("SERIES SUM VERIFICATION  (Substitution + Parseval)")
    print("""
  After computing the Fourier series, substituting a special x value
  often yields famous identities.  For example:
    f(x)=x on [-π,π]:  at x=π  →  1 - 1/3 + 1/5 - … = π/4
    f(x)=x² on [-π,π]: at x=π  →  1 + 1/4 + 1/9 + … = π²/6
    Parseval's theorem gives sum of squares of coefficients.
""")
    f = ask_function()
    print("  Interval for the series:")
    a_val = ask_num("    a = ", default=-sp.pi)
    b_val = ask_num("    b = ", default=sp.pi)
    N = ask_int("  Terms [10]: ", 10)

    print("\n  Computing …\n")
    a0, an, bn, series = fourier_full(f, a_val, b_val, N)

    sec("RESULT — Partial Series")
    print(f"  f(x) ≈  {sp.pretty(series, use_unicode=True)}\n")

    # Substitution
    sec("Substitution Identity")
    print("  Enter x₀ to substitute (e.g. pi, 0, pi/2) — or press Enter to skip:")
    x0_str = input("  x₀ = ").strip()
    if x0_str:
        try:
            x0 = sp.sympify(x0_str, locals=LOCALS)
            lhs = sp.simplify(f.subs(x, x0))
            rhs = sp.simplify(series.subs(x, x0))
            print(f"\n  f({x0}) = {sp.pretty(lhs, use_unicode=True)}")
            print(f"  Series({x0}) = {sp.pretty(rhs, use_unicode=True)}")
            print(f"\n  ∴  {sp.pretty(lhs, use_unicode=True)} = {sp.pretty(rhs, use_unicode=True)}")
        except Exception as e:
            print(f"  ✗ {e}")

    # Parseval
    sec("Parseval's Theorem")
    print("  (1/L) ∫|f|² dx  =  a₀²/2 + Σ(aₙ² + bₙ²)\n")
    try:
        L = (b_val - a_val) / 2
        norm_sq = sp.simplify(sp.integrate(f**2, (x, a_val, b_val)) / L)
        show("‖f‖² = (1/L)∫|f(x)|² dx", norm_sq)
        print("  Equate with  a₀²/2 + Σ(aₙ²+bₙ²)  to derive sum identities.\n")
    except Exception as e:
        print(f"  (Skipped: {e})")


def menu_sketch():
    """ASCII sketch / description of a function on an interval."""
    hdr("FUNCTION SKETCH (text description)")
    print("  Note: For full graphical plots, run:  pip install matplotlib\n")
    f = ask_function()
    a_val = ask_num("  Left endpoint a = ", default=-sp.pi)
    b_val = ask_num("  Right endpoint b = ", default=sp.pi)

    sec("Function Analysis")
    show("f(x)", f)

    # Key values
    points = [a_val, sp.Integer(0), b_val]
    print("  Key values:")
    for pt in points:
        try:
            val = sp.simplify(f.subs(x, pt))
            print(f"    f({sp.simplify(pt)}) = {sp.pretty(val, use_unicode=True)}")
        except Exception:
            pass

    # Derivative for monotonicity
    try:
        df = sp.diff(f, x)
        sec("Derivative f'(x)")
        show("f'(x)", sp.simplify(df))
        crit = sp.solve(df, x)
        if crit:
            print(f"  Critical points: {[sp.simplify(c) for c in crit]}")
    except Exception:
        pass

    parity_check(f)

    sec("Tip")
    print("  To get a visual plot, run this in Python:")
    print("    import sympy as sp")
    print(f"    x = sp.Symbol('x')")
    print(f"    sp.plot({f}, (x, {sp.simplify(a_val)}, {sp.simplify(b_val)}))")


# ─────────────────────────── main menu ───────────────────────────────────────
MENU = [
    ("1", "Find the period of a function  (Problem 1 type)", menu_period),
    ("2", "Full Fourier series  [-π,π] or custom interval/period", menu_full_fourier),
    ("3", "Half-range cosine series  on [0, L]", menu_half_range),
    ("4", "Half-range sine series    on [0, L]", menu_half_range),
    ("5", "Series sum / identity verification  (Parseval, substitution)", menu_verify),
    ("6", "Function sketch & analysis", menu_sketch),
    ("q", "Quit", None),
]


def main():
    print(SEP)
    print("  ♾  Local Fourier Series Solver  —  Comprehensive Edition")
    print("  All computations via SymPy  |  No internet  |  No API")
    print(SEP)
    print("""
  Problem types covered:
    1  Period of trig functions (e.g. cos^1971(2025x+2026))
    2  Full Fourier series on any interval with full steps
    3  Half-range cosine series (even extension)
    4  Half-range sine series   (odd extension)
    5  Prove identities like 1-1/4+1/9-…=π²/12 via substitution
    6  Analyse / sketch a function (derivatives, parity, key values)

  All functions accept piecewise input.
""")

    while True:
        print(SEP)
        print("  MAIN MENU")
        print(THIN)
        for key, label, _ in MENU:
            print(f"  [{key}]  {label}")
        print(SEP)

        choice = input("\n  Select: ").strip().lower()

        if choice in ('q', 'quit', 'exit'):
            print("\n  Goodbye!\n")
            break

        # Menu option 4 also calls menu_half_range but with sine pre-selected
        if choice == "4":
            hdr("HALF-RANGE SINE SERIES")
            L_val = ask_num("  Upper limit L of [0, L] = ", default=sp.pi)
            f = ask_function()
            N = ask_int("  Terms to display [5]: ", 5)
            print("\n  Computing …\n")
            _, _, bn, series = fourier_sine(f, L_val, N)
            sec(f"RESULT — Half-Range Sine Series  on [0, {sp.simplify(L_val)}]")
            print(f"  f(x) ≈  {sp.pretty(series, use_unicode=True)}\n")
        else:
            matched = next((fn for k, _, fn in MENU if k == choice and fn), None)
            if matched:
                try:
                    matched()
                except KeyboardInterrupt:
                    print("\n  (Interrupted)")
            else:
                print("  ✗ Invalid choice.")

        input("\n  [Press Enter to return to main menu] ")


if __name__ == "__main__":
    main()