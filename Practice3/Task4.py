import math
import matplotlib.pyplot as plt
import numpy as np

# Параметри задачі
r_top = 2.5  # м
y_top = 4.0  # м
y_out = 1.0  # м
y0 = 0.75  # м
t_start = 0.0
t_end = 8.0
h = 0.4  # крок


# Площа поверхні рідини A(y)
def A(y):
    r = r_top * (y / y_top)
    return math.pi * r**2


# Притік Q_in(t) та відтік Q_out(y)
def Q_in(t):
    return 3.0 * (math.sin(t) ** 2)


def Q_out(y):
    if y > y_out:
        return 3.0 * ((y - y_out) ** 1.5)
    return 0.0


# Права частина ЗДР f(t, y) = dy/dt
def f(t, y):
    return (Q_in(t) - Q_out(y)) / A(y)


# 1. Модифікований метод Ейлера (серединна точка)
def euler_modified(t_start, t_end, h, y0):
    t_vals, y_vals = [t_start], [y0]
    t, y = t_start, y0
    while t < t_end - 1e-9:
        t_mid = t + h / 2.0
        y_mid = y + (h / 2.0) * f(t, y)
        y_next = y + h * f(t_mid, y_mid)
        t_next = t + h
        t_vals.append(round(t_next, 2))
        y_vals.append(y_next)
        t, y = t_next, y_next
    return t_vals, y_vals


# 2. Вдосконалений метод Ейлера (Ейлера-Коші)
def euler_improved(t_start, t_end, h, y0):
    t_vals, y_vals = [t_start], [y0]
    t, y = t_start, y0
    while t < t_end - 1e-9:
        t_next = t + h
        y_pred = y + h * f(t, y)
        y_next = y + (h / 2.0) * (f(t, y) + f(t_next, y_pred))
        t_vals.append(round(t_next, 2))
        y_vals.append(y_next)
        t, y = t_next, y_next
    return t_vals, y_vals


# 3. Метод Рунге-Кутти 4-го порядку (RK4)
def runge_kutta_4(t_start, t_end, h, y0):
    t_vals, y_vals = [t_start], [y0]
    t, y = t_start, y0
    while t < t_end - 1e-9:
        k1 = f(t, y)
        k2 = f(t + h / 2.0, y + (h / 2.0) * k1)
        k3 = f(t + h / 2.0, y + (h / 2.0) * k2)
        k4 = f(t + h, y + h * k3)

        y_next = y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        t_next = t + h

        t_vals.append(round(t_next, 2))
        y_vals.append(y_next)
        t, y = t_next, y_next
    return t_vals, y_vals


# Обчислення розв'язків
t_m, y_m = euler_modified(t_start, t_end, h, y0)
t_i, y_i = euler_improved(t_start, t_end, h, y0)
t_rk, y_rk = runge_kutta_4(t_start, t_end, h, y0)

# Побудова графіків
plt.figure(figsize=(10, 6))
plt.plot(
    t_m,
    y_m,
    "s-",
    label="Модифікований Ейлер (2-й порядок)",
    color="tab:green",
    alpha=0.75,
)
plt.plot(
    t_i,
    y_i,
    "^--",
    label="Вдосконалений Ейлер (2-й порядок)",
    color="tab:blue",
    alpha=0.75,
)
plt.plot(
    t_rk,
    y_rk,
    "o-",
    label="Рунге-Кутта 4-го порядку (RK4)",
    color="tab:red",
    linewidth=2,
)

plt.axhline(
    y=y_out,
    color="black",
    linestyle=":",
    linewidth=1.2,
    label=f"Рівень стоку $y_{{out}} = {y_out}$ м",
)
plt.title(
    "Порівняння методів Ейлера та Рунге-Кутти 4-го порядку ($h = 0.4$)",
    fontsize=12,
)
plt.xlabel("Час $t$ (дні)")
plt.ylabel("Глибина $y$ (м)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Друк порівняльної таблиці
print(
    f"{'t (дні)':>8} | {'Модифікований (м)':>18} | {'Вдосконалений (м)':>18} | {'Рунге-Кутта 4 (м)':>18}"
)
print("-" * 70)
for t, ym, yi, yrk in zip(t_m, y_m, y_i, y_rk):
    print(f"{t:8.1f} | {ym:18.4f} | {yi:18.4f} | {yrk:18.4f}")