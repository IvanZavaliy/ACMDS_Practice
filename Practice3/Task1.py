import math
import matplotlib.pyplot as plt
import numpy as np


# Визначення функції c(t) та рівняння f(t) = 0
def c(t):
    return 2 * t * math.exp(-t / 3)


def f(t):
    return c(t) - 0.25


def df(t):
    return 2 * math.exp(-t / 3) * (1 - t / 3)


# 1. Метод половинного поділу (Bisection Method)
def bisection(a, b, eps=1e-4):
    iters = 0
    while (b - a) / 2 > eps:
        iters += 1
        mid = (a + b) / 2
        if f(mid) == 0:
            return mid, iters
        elif f(a) * f(mid) < 0:
            b = mid
        else:
            a = mid
    return (a + b) / 2, iters


# 2. Метод хорд (Chord / Secant Method)
def chord(a, b, eps=1e-4, max_iter=100):
    iters = 0
    x0, x1 = a, b
    while iters < max_iter:
        iters += 1
        x2 = x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))
        if abs(x2 - x1) < eps:
            return x2, iters
        x0, x1 = x1, x2
    return x1, iters


# 3. Метод простих ітерацій (Fixed-Point Iteration)
# Перетворення: 2*t*e^(-t/3) = 0.25 => e^(t/3) = 8*t => t = 3 * ln(8 * t)
def g(t):
    return 3 * math.log(8 * t)


def simple_iteration(t0, eps=1e-4, max_iter=100):
    iters = 0
    t_curr = t0
    while iters < max_iter:
        iters += 1
        t_next = g(t_curr)
        if abs(t_next - t_curr) < eps:
            return t_next, iters
        t_curr = t_next
    return t_curr, iters


# 4. Метод Ньютона (Newton-Raphson Method)
def newton(t0, eps=1e-4, max_iter=100):
    iters = 0
    t_curr = t0
    while iters < max_iter:
        iters += 1
        t_next = t_curr - f(t_curr) / df(t_curr)
        if abs(t_next - t_curr) < eps:
            return t_next, iters
        t_curr = t_next
    return t_curr, iters


# --- Побудова графіка ---
t_vals = np.linspace(0, 18, 500)
c_vals = [c(t) for t in t_vals]

plt.figure(figsize=(9, 5))
plt.plot(t_vals, c_vals, label=r"$c(t) = 2t e^{-t/3}$", color="blue", lw=2)
plt.axhline(
    y=0.25,
    color="red",
    linestyle="--",
    label="Критична концентрація ($0.25$ мг/мл)",
)
plt.axvline(
    x=3,
    color="green",
    linestyle=":",
    label="Максимум ($t = 3$ год, $c = 2.21$ мг/мл)",
)

# Позначення точок перетину
plt.plot(14.197, 0.25, "ro")
plt.annotate(
    "Новий укол\n($t ≈ 14.20$ год)",
    xy=(14.197, 0.25),
    xytext=(11, 0.7),
    arrowprops=dict(facecolor="black", shrink=0.05, width=1, headwidth=6),
)

plt.title("Динаміка концентрації ліків у крові")
plt.xlabel("Час $t$ (години)")
plt.ylabel("Концентрація $c(t)$ (мг/мл)")
plt.grid(True)
plt.legend()
plt.show()

# --- Обчислення чисельними методами ---
eps = 1e-4  # точність для хвилин (1/60 год ≈ 0.016, тож 1e-4 надає достатню точність)

t_bis, it_bis = bisection(12, 16, eps)
t_chord, it_chord = chord(12, 16, eps)
t_iter, it_iter = simple_iteration(14.0, eps)
t_newton, it_newton = newton(14.0, eps)


def format_time(t_hours):
    hours = int(t_hours)
    minutes = round((t_hours - hours) * 60)
    return f"{t_hours:.4f} год ({hours} год {minutes} хв)"


print("=== Результати обчислень ===")
print(
    f"1. Метод половинного поділу : t = {format_time(t_bis)}, Ітерацій: {it_bis}"
)
print(
    f"2. Метод хорд               : t = {format_time(t_chord)}, Ітерацій: {it_chord}"
)
print(
    f"3. Метод простих ітерацій   : t = {format_time(t_iter)}, Ітерацій: {it_iter}"
)
print(
    f"4. Метод Ньютона            : t = {format_time(t_newton)}, Ітерацій: {it_newton}"
)