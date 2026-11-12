class Node:
    """Елемент зв'язного списку хеш-таблиці."""
    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.next = None

def create_element(key, value=None) -> Node:
    """Функція для створення нового елемента хеш-таблиці."""
    return Node(key, value)

class ChainedHashTableDivision:
    def __init__(self, m: int):
        self.m = m
        self.T = [None] * m  # Створюємо масив покажчиків на списки розміру m

    def h(self, k: int) -> int:
        """Хеш-функція: метод ділення h(k) = k mod m."""
        return k % self.m

    def chained_hash_insert(self, x: Node):
        """Chained-Hash-Insert(T, x): вставка x у заголовок списку T[h(x.key)]."""
        j = self.h(x.key)
        x.next = self.T[j]
        self.T[j] = x

    def chained_hash_search(self, k: int) -> Node | None:
        """Chained-Hash-Search(T, k): пошук елемента з ключем k у списку T[h(k)]."""
        j = self.h(k)
        current = self.T[j]
        while current is not None:
            if current.key == k:
                return current
            current = current.next
        return None

    def chained_hash_delete(self, x: Node):
        """Chained-Hash-Delete(T, x): видалення елемента x зі списку T[h(x.key)]."""
        j = self.h(x.key)
        current = self.T[j]
        prev = None

        while current is not None:
            if current is x:  # Порівняння за посиланням на об'єкт
                if prev is None:
                    self.T[j] = current.next
                else:
                    prev.next = current.next
                current.next = None
                return
            prev = current
            current = current.next


# Приклад тестування:
ht_div = ChainedHashTableDivision(m=10)

# Створення елементів через окрему функцію
item1 = create_element(15, "Дані A")
item2 = create_element(25, "Дані B")  # Колізія: 15 % 10 == 25 % 10 == 5
item3 = create_element(33, "Дані C")

# Вставка
ht_div.chained_hash_insert(item1)
ht_div.chained_hash_insert(item2)
ht_div.chained_hash_insert(item3)

# Пошук
found = ht_div.chained_hash_search(25)
print(f"Знайдено: ключ={found.key}, значення={found.value}")

# Видалення
ht_div.chained_hash_delete(item1)
print(f"Пошук 15 після видалення: {ht_div.chained_hash_search(15)}")