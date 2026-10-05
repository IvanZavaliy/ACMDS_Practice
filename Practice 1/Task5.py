import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

# 1. Підбір значень та генерація сітки
x_min, x_max = -2.0, 2.0
y_min, y_max = -2.0, 2.0
points_count = 100

x = np.linspace(x_min, x_max, points_count)
y = np.linspace(y_min, y_max, points_count)
X, Y = np.meshgrid(x, y)

# 2. Обчислення значень z за рівнянням Мавпячого сідла
Z = X**3 - 3 * X * (Y**2)

# 3. Відображення значень, що використовувалися при побудові
print("=" * 60)
print("ПАРАМЕТРИ ТА ЗНАЧЕННЯ ДЛЯ ПОБУДОВИ ПОВЕРХНІ:")
print("=" * 60)
print(f"Поверхня: Мавпяче сідло (z = x^3 - 3*x*y^2)")
print(f"Діапазон x: [{x_min}, {x_max}], кількість точок: {points_count}")
print(f"Діапазон y: [{y_min}, {y_max}], кількість точок: {points_count}")
print(f"Діапазон z: [{Z.min():.4f}, {Z.max():.4f}]")
print("\nФрагмент сітки координат X (перші 3x3 точки):")
print(np.round(X[:3, :3], 3))
print("\nФрагмент сітки координат Y (перші 3x3 точки):")
print(np.round(Y[:3, :3], 3))
print("\nФрагмент розрахованих значень Z (перші 3x3 точки):")
print(np.round(Z[:3, :3], 3))
print("=" * 60)

# 4. Побудова графіка поверхні
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Побудова 3D-поверхні
surf = ax.plot_surface(
    X, Y, Z,
    cmap=cm.coolwarm,
    rstride=2,
    cstride=2,
    edgecolor='none',
    alpha=0.9
)

# Додавання каркасних ліній (wireframe) для кращого сприйняття форми
ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10, color='black', linewidth=0.5, alpha=0.4)

# Підписи осей і заголовок
ax.set_title("Поверхня «Мавпяче сідло»: $z = x^3 - 3xy^2$", fontsize=14, pad=15)
ax.set_xlabel("Вісь X", labelpad=8)
ax.set_ylabel("Вісь Y", labelpad=8)
ax.set_zlabel("Вісь Z", labelpad=8)

# Колірна шкала (colorbar)
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label="Значення Z")

# Початковий ракурс огляду
ax.view_init(elev=25, azim=45)

plt.tight_layout()
plt.show()