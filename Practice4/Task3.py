import random
import string
import time


def rabin_karp(text: str, pattern: str, p: int, q: int):
    n = len(text)
    m = len(pattern)

    # Вага старшого розряду: p^(m-1) mod q
    h = pow(p, m - 1, q)

    # Обчислення початкових хешів шаблону та першого вікна тексту
    p_hash = 0
    t_hash = 0
    for i in range(m):
        p_hash = (p_hash * p + ord(pattern[i])) % q
        t_hash = (t_hash * p + ord(text[i])) % q

    occurrences = []
    hash_matches = 0
    collisions = 0

    # Послідовний зсув вікна
    for s in range(n - m + 1):
        if p_hash == t_hash:
            hash_matches += 1
            # Посимвольна перевірка при збігу хешів
            if text[s:s + m] == pattern:
                occurrences.append(s)
            else:
                collisions += 1

        # Обчислення ковзного хешу для наступного вікна
        if s < n - m:
            t_hash = ((t_hash - ord(text[s]) * h) * p + ord(text[s + m])) % q
            if t_hash < 0:
                t_hash += q

    return occurrences, hash_matches, len(occurrences), collisions


def main():
    seed = 3
    pattern = "SEARCH"
    text_len = 100_000
    insert_positions = [1000, 25000, 50000, 75000, 95000]

    p = 43
    q1 = 1019
    q2 = 10193  # Найближче просте число до 1019 * 10 = 10190

    # Генерація псевдовипадкового тексту
    random.seed(seed)
    chars = random.choices(string.ascii_uppercase, k=text_len)

    # Вставка шаблону у вказані позиції
    for pos in insert_positions:
        for offset, ch in enumerate(pattern):
            chars[pos + offset] = ch

    text = "".join(chars)

    # Тестування для двох модулів
    for q_name, q_val in [("Початковий (q = 1019)", q1), ("Збільшений (q = 10193)", q2)]:
        # Вимірювання медіанного часу з 10 запусків
        times = []
        for _ in range(10):
            t0 = time.perf_counter()
            res = rabin_karp(text, pattern, p, q_val)
            t1 = time.perf_counter()
            times.append(t1 - t0)

        times.sort()
        median_time = times[len(times) // 2]

        occ, total_hm, true_cnt, coll = res
        print(f"=== {q_name} ===")
        print(f"Позиції входжень: {occ}")
        print(f"Загальна кількість збігів хешів: {total_hm}")
        print(f"Кількість фактичних входжень:    {true_cnt}")
        print(f"Кількість колізій:               {coll}")
        print(f"Медіанний час виконання:         {median_time * 1000:.3f} мс\n")


if __name__ == "__main__":
    main()