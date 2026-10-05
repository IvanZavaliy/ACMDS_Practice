import numpy as np
import matplotlib.pyplot as plt

# Діапазон параметра t від 0 до 2*pi (використовуємо достатньо точок через доданок 200t)
t = np.linspace(0, 2 * np.pi, 2048)

# Розрахунок r за точною формулою з двох зображень
r = (
    (1 + 0.9 * np.cos(8 * t))
    * (1 + 0.1 * np.cos(24 * t))
    * (1 + np.sin(t))
    * (1 - 0.02 * np.sin(200 * t))
)

# Побудова графіка в полярних координатах
plt.figure(figsize=(7, 7))
ax = plt.axes(polar=True)

# Поворот для класичного вертикального відображення кривої
ax.set_theta_zero_location("E")
ax.set_theta_direction(1)

ax.plot(t, r, color="darkgreen", linewidth=1.2, label="Каннабола")

plt.title("Графік кривої «Каннабола» в полярних координатах", va="bottom", fontsize=12)
plt.legend(loc="upper right")
plt.grid(True, linestyle="--", alpha=0.6)

plt.show()