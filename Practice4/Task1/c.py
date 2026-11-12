class OpenAddressingHashTable:
    DELETED = object()  # Маркер вилученого елемента для збереження ланцюжка проб

    def __init__(self, m: int):
        self.m = m
        self.T = [None] * m

    def h_prime(self, k: int) -> int:
        """Базова допоміжна хеш-функція."""
        return k % self.m

    def h(self, k: int, i: int) -> int:
        """Хеш-функція з лінійним дослідженням: h(k, i) = (h'(k) + i) mod m."""
        return (self.h_prime(k) + i) % self.m

    def hash_insert(self, k: int) -> int:
        """
        Hash-Insert(T, k)
        Вставка ключа k у таблицю згідно з наведеним алгоритмом.
        """
        i = 0
        while True:
            j = self.h(k, i)
            if self.T[j] is None or self.T[j] is self.DELETED:
                self.T[j] = k
                return j
            else:
                i += 1
            if i == self.m:
                break
        raise OverflowError("Переповнення хеш-таблиці")

    def hash_search(self, k: int) -> int | None:
        """
        Hash-Search(T, k)
        Пошук слота з ключем k. Повертає індекс j або None (NIL).
        """
        i = 0
        while True:
            j = self.h(k, i)
            if self.T[j] == k:
                return j
            i += 1
            if self.T[j] is None or i == self.m:
                break
        return None

    def hash_delete(self, k: int) -> bool:
        """Видалення ключа шляхом встановлення маркера DELETED."""
        j = self.hash_search(k)
        if j is not None:
            self.T[j] = self.DELETED
            return True
        return False


# Приклад тестування:
oa_table = OpenAddressingHashTable(m=7)

# Вставка
keys_to_insert = [10, 17, 24]  # 10%7=3, 17%7=3 (колізія -> слот 4), 24%7=3 (колізія -> слот 5)
for key in keys_to_insert:
    slot = oa_table.hash_insert(key)
    print(f"Ключ {key} вставлено в слот {slot}")

# Пошук
search_key = 17
idx = oa_table.hash_search(search_key)
print(f"Пошук ключа {search_key}: знайдено в слоті {idx}")

# Пошук відсутнього ключа
print(f"Пошук ключа 99: {oa_table.hash_search(99)}")