import math
import random
import sympy as sp

# 1. Початкові параметри задачі
a = 0.0
b = 4.0
h = 0.5
n = int((b - a) / h)  # n = 8

def f(x):
    return (x ** 2) * math.exp(-x)

# 2. Символьне інтегрування за допомогою SymPy
x_sym = sp.Symbol('x')
f_sym = (x_sym ** 2) * sp.exp(-x_sym)
exact_integral = sp.integrate(f_sym, (x_sym, a, b))
exact_val = float(exact_integral.evalf())

print("=" * 65)
print(f"Символьне точне значення: {exact_integral}")
print(f"Аналітичне числове значення: {exact_val:.6f}")
print("=" * 65)

# -------------------------------------------------------------
# Метод центральних прямокутників
# I ≈ h * sum(f(x_i - h/2)) для i від 1 до n
# -------------------------------------------------------------
print("\n--- 1. МЕТОД ЦЕНТРАЛЬНИХ ПРЯМОКУТНИКІВ ---")
mid_terms = []
sum_mid = 0.0

for i in range(n):
    x_mid = a + (i + 0.5) * h
    term = f(x_mid)
    mid_terms.append(term)
    sum_mid += term
    print(f"Крок {i+1}: x_{i}+h/2 = {x_mid:4.2f}  -->  f(x_mid) = {term:.6f}")

integral_midpoint = h * sum_mid
print(f"\nСума значень у серединах: {sum_mid:.6f}")
print(f"Результат (h * сума): {integral_midpoint:.6f}")
print(f"Похибка: {abs(exact_val - integral_midpoint):.6f}")

# -------------------------------------------------------------
# Метод трапецій
# I ≈ h * [ (f(a) + f(b))/2 + sum(f(x_i)) для i від 1 до n-1 ]
# -------------------------------------------------------------
print("\n--- 2. МЕТОД ТРАПЕЦІЙ ---")
trap_terms = []
for i in range(n + 1):
    xi = a + i * h
    fi = f(xi)
    trap_terms.append(fi)
    print(f"Вузол x_{i} = {xi:4.2f}  -->  f(x_{i}) = {fi:.6f}")

sum_inner_trap = sum(trap_terms[1:-1])
integral_trapezoid = h * (0.5 * trap_terms[0] + sum_inner_trap + 0.5 * trap_terms[-1])

print(f"\n(f(a) + f(b)) / 2 = {(trap_terms[0] + trap_terms[-1]) / 2:.6f}")
print(f"Сума внутрішніх вузлів: {sum_inner_trap:.6f}")
print(f"Результат методу трапецій: {integral_trapezoid:.6f}")
print(f"Похибка: {abs(exact_val - integral_trapezoid):.6f}")

# -------------------------------------------------------------
# Метод Сімпсона (парабол)
# I ≈ (h / 3) * [ f(x_0) + 4*sum(непарні) + 2*sum(парні) + f(x_n) ]
# -------------------------------------------------------------
print("\n--- 3. МЕТОД СІМПСОНА ---")
sum_odd = sum(trap_terms[i] for i in range(1, n, 2))
sum_even = sum(trap_terms[i] for i in range(2, n, 2))

print(f"f(x_0) = {trap_terms[0]:.6f},  f(x_n) = {trap_terms[-1]:.6f}")
print(f"Сума доданків з непарними індексами (вага 4): {sum_odd:.6f}")
print(f"Сума доданків з парними індексами (вага 2):   {sum_even:.6f}")

integral_simpson = (h / 3.0) * (trap_terms[0] + 4 * sum_odd + 2 * sum_even + trap_terms[-1])
print(f"\nРезультат методу Сімпсона: {integral_simpson:.6f}")
print(f"Похибка: {abs(exact_val - integral_simpson):.6f}")

# -------------------------------------------------------------
# Метод Монте-Карло
# I ≈ (b - a) * (1 / N) * sum(f(x_rand))
# -------------------------------------------------------------
print("\n--- 4. МЕТОД МОНТЕ-КАРЛО ---")
random.seed(42)  # Фіксація випадкового стану для відтворюваності
N_samples = 100_000

# Демонстрація перших 5 випадкових доданків
print(f"Генерація {N_samples} точок (перші 5 доданків для прикладу):")
sample_sum = 0.0
for k in range(N_samples):
    x_rand = random.uniform(a, b)
    f_rand = f(x_rand)
    sample_sum += f_rand
    if k < 5:
        print(f"  Вибірка {k+1}: x = {x_rand:.4f}  -->  f(x) = {f_rand:.6f}")

integral_mc = (b - a) * (sample_sum / N_samples)
print(f"\nСереднє значення функції: {(sample_sum / N_samples):.6f}")
print(f"Результат методу Монте-Карло (N={N_samples}): {integral_mc:.6f}")
print(f"Похибка: {abs(exact_val - integral_mc):.6f}")

# -------------------------------------------------------------
# Зведена таблиця результатів
# -------------------------------------------------------------
print("\n" + "=" * 65)
print(f"{'Метод':<26} | {'Значення':<12} | {'Абсолютна похибка'}")
print("-" * 65)
print(f"{'Точне (SymPy)':<26} | {exact_val:<12.6f} | —")
print(f"{'Центральних прямокутників':<26} | {integral_midpoint:<12.6f} | {abs(exact_val - integral_midpoint):.6f}")
print(f"{'Трапецій':<26} | {integral_trapezoid:<12.6f} | {abs(exact_val - integral_trapezoid):.6f}")
print(f"{'Сімпсона':<26} | {integral_simpson:<12.6f} | {abs(exact_val - integral_simpson):.6f}")
print(f"{'Монте-Карло (N=100k)':<26} | {integral_mc:<12.6f} | {abs(exact_val - integral_mc):.6f}")
print("=" * 65)