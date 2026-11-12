import math
import time
import numpy as np

# 1. Генерація даних
n = 1_000_000
n_queries = 10_000
p_target = 0.01
v = 3

# Генерація унікальних 10.a.b.c (діапазон 10.0.0.0/8)
np.random.seed(42)
table = np.random.choice(
    np.arange(10 << 24, 11 << 24, dtype=np.uint32),
    size=n,
    replace=False
)

# 10 000 адрес із 192.168.0.0/16, гарантовано відсутніх у таблиці
queries = np.random.choice(
    np.arange((192 << 24) | (168 << 16), (192 << 24) | (169 << 16), dtype=np.uint32),
    size=n_queries,
    replace=False
)

# 2. Розрахунок параметрів фільтра
m = int(round(-n * math.log(p_target) / (math.log(2) ** 2))) # 9 585 058
k = int(round((m / n) * math.log(2)))                        # 7

P = 4294967311
a1 = 2654435761 + 10007 * v
b1 = 1013904223 + 104729 * v
a2 = 2246822519 + 65537 * v
b2 = 3266489917 + 8191 * v

# 3. Алгоритми пошуку
def naive_search(t_arr, x):
    """Послідовний лінійний пошук елемента в масиві без прискорення."""
    for i in range(len(t_arr)):
        if t_arr[i] == x:
            return i
    return -1

class BloomFilter:
    def __init__(self, size, k_hashes):
        self.m = size
        self.k = k_hashes
        self.bit_array = np.zeros(size, dtype=np.bool_)

    def insert(self, x):
        h1 = ((a1 * int(x) + b1) % P) % self.m
        h2 = 1 + ((a2 * int(x) + b2) % P) % (self.m - 1)
        for i in range(self.k):
            pos = (h1 + i * h2) % self.m
            self.bit_array[pos] = True

    def contains(self, x):
        h1 = ((a1 * int(x) + b1) % P) % self.m
        h2 = 1 + ((a2 * int(x) + b2) % P) % (self.m - 1)
        for i in range(self.k):
            pos = (h1 + i * h2) % self.m
            if not self.bit_array[pos]:
                return False
        return True

def filtered_search(t_arr, bloom, x):
    """Каскадний пошук: фільтр Блума -> послідовний пошук при FP."""
    if not bloom.contains(x):
        return -1
    return naive_search(t_arr, x)