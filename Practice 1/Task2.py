import math

# Точка обчислення: x = pi / 6
x = math.pi / 6
true_val = math.cos(x)  # Істинне значення: sqrt(3)/2

# Критерій зупинки Скарборо для n = 2 значущих цифр:
# eps_s = 0.5 * 10^(2 - n)% = 0.5 * 10^(2 - 2)% = 0.5%
n_sig_figs = 2
eps_s = 0.5 * 10 ** (2 - n_sig_figs)

current_val = 0.0
k = 0  # порядковий номер члена ряду (0, 1, 2, ...)

print(f"Істинне значення cos(pi/6) = {true_val:.8f}")
print(f"Критерій зупинки (|eps_a| < {eps_s}%):\n")
print(f"{'Ітерація':<10} | {'Член ряду':<14} | {'Оцінка cos(x)':<14} | {'eps_t (%)':<14} | {'eps_a (%)':<14}")
print("-" * 75)

while True:
    term = ((-1) ** k) * (x ** (2 * k)) / math.factorial(2 * k)
    prev_val = current_val
    current_val += term

    # Істинна відносна похибка: eps_t = |(true - approx) / true| * 100%
    eps_t = abs((true_val - current_val) / true_val) * 100.0

    # Наближена відносна похибка: eps_a = |(current - prev) / current| * 100%
    if k == 0:
        eps_a_str = "—"
    else:
        eps_a = abs((current_val - prev_val) / current_val) * 100.0
        eps_a_str = f"{eps_a:.6f}%"

    print(f"{k + 1:<10} | {term:<+14.6f} | {current_val:<14.8f} | {eps_t:<13.6f}% | {eps_a_str:<14}")

    if k > 0 and eps_a < eps_s:
        print("-" * 75)
        print(f"Критерій зупинки досягнуто на ітерації {k + 1} (|eps_a| = {eps_a:.6f}% < {eps_s}%).")
        break

    k += 1