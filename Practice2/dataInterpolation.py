import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# Вхідні дані (Варіант 3)
t = np.array([0, 1, 2, 3, 4], dtype=float)
v = np.array([1.35, 1.15, 1.05, 1.00, 0.40], dtype=float)


# 1. Поліном Лагранжа 4-го порядку
def lagrange_poly_4(x_val, t_nodes, v_nodes):
    total = 0.0
    n = len(t_nodes)
    for i in range(n):
        term = v_nodes[i]
        for j in range(n):
            if i != j:
                term *= (x_val - t_nodes[j]) / (t_nodes[i] - t_nodes[j])
        total += term
    return total


# 2. Поліном Ньютона 4-го порядку (метод розділених різниць)
def newton_divided_diff(t_nodes, v_nodes):
    n = len(t_nodes)
    coef = np.zeros((n, n))
    coef[:, 0] = v_nodes
    for j in range(1, n):
        for i in range(n - j):
            coef[i, j] = (coef[i + 1, j - 1] - coef[i, j - 1]) / (t_nodes[i + j] - t_nodes[i])
    return coef[0, :]


def newton_poly_4(x_val, t_nodes, coef):
    n = len(coef)
    result = coef[0]
    prod = 1.0
    for i in range(1, n):
        prod *= (x_val - t_nodes[i - 1])
        result += coef[i] * prod
    return result


# 3. Лінійний сплайн
def linear_spline(x_val, t_nodes, v_nodes):
    x_val = np.asarray(x_val)
    y = np.zeros_like(x_val)
    for i in range(len(t_nodes) - 1):
        mask = (x_val >= t_nodes[i]) & (x_val <= t_nodes[i + 1])
        if i == len(t_nodes) - 2:
            mask = (x_val >= t_nodes[i]) & (x_val <= t_nodes[i + 1])
        m = (v_nodes[i + 1] - v_nodes[i]) / (t_nodes[i + 1] - t_nodes[i])
        y[mask] = v_nodes[i] + m * (x_val[mask] - t_nodes[i])
    return y


# 4. Квадратичний сплайн (c_0 = 0)
def quadratic_spline(x_val, t_nodes, v_nodes):
    n = len(t_nodes) - 1
    a = np.copy(v_nodes[:-1])
    b = np.zeros(n)
    c = np.zeros(n)

    # Boundary condition c[0] = 0
    c[0] = 0.0
    b[0] = (v_nodes[1] - v_nodes[0]) - c[0]

    for i in range(1, n):
        b[i] = b[i - 1] + 2 * c[i - 1]
        c[i] = (v_nodes[i + 1] - v_nodes[i]) - b[i]

    x_val = np.asarray(x_val)
    y = np.zeros_like(x_val)
    for i in range(n):
        mask = (x_val >= t_nodes[i]) & (x_val <= t_nodes[i + 1])
        dx = x_val[mask] - t_nodes[i]
        y[mask] = a[i] + b[i] * dx + c[i] * (dx ** 2)
    return y


# 5. Природний кубічний сплайн
cs = CubicSpline(t, v, bc_type='natural')

# Сітка для побудови гладких графіків
t_dense = np.linspace(0, 4, 300)

# Обчислення значень
v_lagrange = [lagrange_poly_4(xi, t, v) for xi in t_dense]
newton_coefs = newton_divided_diff(t, v)
v_newton = [newton_poly_4(xi, t, newton_coefs) for xi in t_dense]
v_linear = linear_spline(t_dense, t, v)
v_quad = quadratic_spline(t_dense, t, v)
v_cubic = cs(t_dense)

# Побудова графіків
plt.figure(figsize=(11, 7))

# Експериментальні точки
plt.plot(t, v, 'ko', markersize=8, label='Експериментальні дані (Вз. 3)', zorder=6)

# Графіки інтерполянтів
plt.plot(t_dense, v_lagrange, 'r--', linewidth=2, label='Поліном Лагранжа 4-го порядку')
plt.plot(t_dense, v_newton, 'm:', linewidth=2, label='Поліном Ньютона 4-го порядку')
plt.plot(t_dense, v_linear, 'g-', linewidth=1.5, label='Лінійний сплайн')
plt.plot(t_dense, v_quad, 'c-', linewidth=2, label='Квадратичний сплайн')
plt.plot(t_dense, v_cubic, 'b-', linewidth=2, label='Кубічний сплайн (природний)')

plt.title('Порівняння поліноміальної та сплайн-інтерполяції (Варіант 3)', fontsize=13)
plt.xlabel('Час t (години)', fontsize=11)
plt.ylabel('Напруга v (Вольти)', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=10, loc='best')
plt.tight_layout()
plt.show()