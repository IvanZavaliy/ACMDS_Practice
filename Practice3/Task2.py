import math
import matplotlib.pyplot as plt
import numpy as np

# Параметри задачі
r_top = 2.5  # м
y_top = 4.0  # м
y_out = 1.0  # м
y0 = 0.75  # м (початковий рівень)
t_start = 0.0
t_end = 8.0
h = 0.4  # крок


# Площа поверхні рідини A(y)
def A(y):
    r = r_top * (y / y_top)
    return math.pi * r**2


# Притік Q_in(t)
def Q_in(t):
    return 3.0 * (math.sin(t) ** 2)


# Відтік Q_out(y)
def Q_out(y):
    if y > y_out:
        return 3.0 * ((y - y_out) ** 1.5)
    return 0.0


# Права частина ЗДР f(t, y) = dy/dt
def f(t, y):
    return (Q_in(t) - Q_out(y)) / A(y)


# Метод Ейлера
t_values = [t_start]
y_values = [y0]

t_curr = t_start
y_curr = y0

while t_curr < t_end - 1e-9:
    dy_dt = f(t_curr, y_curr)
    y_next = y_curr + h * dy_dt
    t_next = t_curr + h

    t_values.append(round(t_next, 2))
    y_values.append(y_next)

    t_curr = t_next
    y_curr = y_next

# Вивід результатів у вигляді таблиці
print(f"{'t (дні)':>8} | {'y(t) (м)':>10} | {'Q_in':>8} | {'Q_out':>8}")
print("-" * 42)
for t, y in zip(t_values, y_values):
    print(f"{t:8.1f} | {y:10.4f} | {Q_in(t):8.4f} | {Q_out(y):8.4f}")

# Побудова графіка
plt.figure(figsize=(9, 5))
plt.plot(
    t_values,
    y_values,
    "o-",
    color="navy",
    linewidth=2,
    label="Рівень рідини $y(t)$ (Ейлер)",
)
plt.axhline(
    y=y_out, color="red", linestyle="--", label=f"Стік $y_{{out}} = {y_out}$ м"
)
plt.title("Моделювання рівня рідини в конічній ємності (Метод Ейлера)")
plt.xlabel("Час $t$ (дні)")
plt.ylabel("Глибина $y$ (м)")
plt.grid(True)
plt.legend()
plt.show()