# Початкові дані з умови задачі
num_students = 35  # кількість студентів
length, width, height = 10.0, 7.0, 3.0  # розміри аудиторії, м
power_per_student = 80.0  # тепловиділення одного студента, Вт (Дж/с)
time_minutes = 15.0  # час, хв

c_v = 0.718  # питома теплоємність при сталому об'ємі, кДж/(кг·К)
t_celsius = 20.0  # початкова температура, °C
pressure = 101.325  # тиск, кПа
mwt = 28.97  # молекулярна маса повітря, кг/кмоль
r_const = 8.314  # універсальна газова стала, (кПа·м³)/(кмоль·К)

# 1. Розрахунок об'єму кімнати (V)
volume = length * width * height  # м³

# 2. Переведення одиниць
t_kelvin = t_celsius + 273.15  # абсолютна температура, К
time_seconds = time_minutes * 60  # час у секундах

# 3. Визначення маси повітря в кімнаті з рівняння ідеального газу
# PV = (m / Mwt) * R * T  =>  m = (P * V * Mwt) / (R * T)
mass_air = (pressure * volume * mwt) / (r_const * t_kelvin)  # кг

# 4. Розрахунок кількості виділеного тепла (Q)
# Q = N * P * t (переводимо з Дж у кДж)
q_joules = num_students * power_per_student * time_seconds
q_kj = q_joules / 1000.0  # кДж

# 5. Розрахунок підвищення температури (delta_T)
# Q = m * C_v * delta_T  =>  delta_T = Q / (m * C_v)
delta_t = q_kj / (mass_air * c_v)

print(f"Об'єм аудиторії: {volume:.2f} м³")
print(f"Маса повітря: {mass_air:.2f} кг")
print(f"Загальне виділене тепло: {q_kj:.2f} кДж")
print(f"Підвищення температури (ΔT): {delta_t:.2f} °C (або K)")