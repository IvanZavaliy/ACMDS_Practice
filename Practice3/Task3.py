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


# Площа поверхні A(y)
def A(y):
    r = r_top * (y / y_top)
    return math.pi * r**2


# Функції притоку та відтоку
def Q_in(t):
    return 3.0 * (math.sin(t) ** 2)


def Q_out(y):
    if y > y_out:
        return 3.0 * ((y - y_out) ** 1.5)
    return 0.0


# Права частина ЗДР f(t, y)
def f(t, y):
    return (Q_in(t) - Q_out(y)) / A(y)


# 1. Модифікований метод Ейлера (метод серединної точки)
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


# 2. Вдосконалений метод Ейлера (метод Ейлера-Коші)
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


# Обчислення
t_m, y_m = euler_modified(t_start, t_end, h, y0)
t_i, y_i = euler_improved(t_start, t_end, h, y0)

# Побудова порівняльного графіка
plt.figure(figsize=(10, 6))
plt.plot(
    t_m,
    y_m,
    "s-",
    label="Модифікований Ейлер (серединна точка, 2-й порядок)",
    color="tab:green",
    linewidth=2,
)
plt.plot(
    t_i,
    y_i,
    "^--",
    label="Вдосконалений Ейлер (Ейлера-Коші, 2-й порядок)",
    color="tab:blue",
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
    "Порівняння модифікованого та вдосконаленого методів Ейлера ($h = 0.4$)"
)
plt.xlabel("Час $t$ (дні)")
plt.ylabel("Глибина $y$ (м)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Друк порівняльної таблиці
print(f"{'t (дні)':>8} | {'Модифікований (м)':>20} | {'Вдосконалений (м)':>20}")
print("-" * 55)
for t, ym, yi in zip(t_m, y_m, y_i):
    print(f"{t:8.1f} | {ym:20.4f} | {yi:20.4f}")