import math

from Practice4.Task1.a import ChainedHashTableDivision, create_element


class ChainedHashTableMultiplication(ChainedHashTableDivision):
    def __init__(self, m: int, A: float = (math.sqrt(5) - 1) / 2):
        super().__init__(m)
        self.A = A

    def h(self, k: int) -> int:
        """Хеш-функція: метод множення h(k) = floor(m * (k * A mod 1))."""
        fractional_part = (k * self.A) % 1.0
        return int(math.floor(self.m * fractional_part))


# Приклад тестування:
ht_mul = ChainedHashTableMultiplication(m=8)

e1 = create_element(61, "val61")
e2 = create_element(62, "val62")
e3 = create_element(63, "val63")

ht_mul.chained_hash_insert(e1)
ht_mul.chained_hash_insert(e2)
ht_mul.chained_hash_insert(e3)

res = ht_mul.chained_hash_search(62)
print(f"Метод множення, знайдено: ключ={res.key}, слот={ht_mul.h(62)}")