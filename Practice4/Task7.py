import time

# ----------------------------------------------------------------------
# 1. КОНСТРУЮВАННЯ АЛФАВІТУ ТА ПРЕФІКС-ФУНКЦІЇ
# ----------------------------------------------------------------------
U = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
L = "abcdefghijklmnopqrstuvwxyz"
D = "0123456789"
SIGMA2 = U + L + D + " _`(){}[];,.=+-*/:<>!&"


def compute_prefix_function(P: str) -> list[int]:
    """Обчислення префікс-функції pi для шаблону P."""
    m = len(P)
    pi = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and P[k] != P[i]:
            k = pi[k - 1]
        if P[k] == P[i]:
            k += 1
        pi[i] = k
    return pi


def build_dfa_transitions(P: str, alphabet: str) -> dict:
    """Побудова повної функції переходів детермінованого скінченного автомата."""
    m = len(P)
    delta = {}
    for q in range(m + 1):
        for ch in alphabet:
            combined = P[:q] + ch
            k = min(m, q + 1)
            while k > 0:
                if combined.endswith(P[:k]):
                    break
                k -= 1
            delta[(q, ch)] = k
    return delta


# ----------------------------------------------------------------------
# 2. АЛГОРИТМИ ПОШУКУ
# ----------------------------------------------------------------------
def kmp_matcher(T: str, P: str, pi: list[int]):
    """Класичний алгоритм Кнута-Морріса-Пратта."""
    n = len(T)
    m = len(P)
    q = 0
    comparisons = 0
    pi_transitions = 0
    occurrences = []

    for i in range(n):
        comparisons += 1
        while q > 0 and P[q] != T[i]:
            pi_transitions += 1
            q = pi[q - 1]
            comparisons += 1

        if P[q] == T[i]:
            q += 1

        if q == m:
            occurrences.append(i - m + 1)
            q = pi[q - 1]

    return occurrences, comparisons, pi_transitions


def dfa_matcher(T: str, P: str, delta: dict):
    """Пошук детермінованим скінченним автоматом."""
    m = len(P)
    q = 0
    delta_transitions = 0
    occurrences = []

    for i, ch in enumerate(T):
        q = delta.get((q, ch), 0)
        delta_transitions += 1
        if q == m:
            occurrences.append(i - m + 1)

    return occurrences, delta_transitions


def kmp_stream_matcher(T: str, P: str, pi: list[int], block_size: int):
    """Потоковий пошук КМП фіксованими блоками із збереженням стану q."""
    m = len(P)
    q = 0
    total_processed = 0
    occurrences = []

    for start in range(0, len(T), block_size):
        block = T[start:start + block_size]
        for idx_in_block, ch in enumerate(block):
            abs_idx = total_processed + idx_in_block
            while q > 0 and P[q] != ch:
                q = pi[q - 1]
            if P[q] == ch:
                q += 1
            if q == m:
                occurrences.append(abs_idx - m + 1)
                q = pi[q - 1]
        total_processed += len(block)

    return occurrences


# ----------------------------------------------------------------------
# 3. ОСНОВНИЙ БЛОК ТА КОНТРОЛЬНІ ВИПРОБУВАННЯ
# ----------------------------------------------------------------------
def main():
    v = 3
    P = "std::"
    m = len(P)
    n = 100_000
    positions = [1000, 25000, 50000, 75000, 95000]

    # Генерація тексту T0
    s = v
    chars_T0 = []
    mod_sigma = len(SIGMA2)
    for _ in range(n):
        s = (1664525 * s + 1013904223) & 0xFFFFFFFF
        chars_T0.append(SIGMA2[s % mod_sigma])

    for pos in positions:
        for idx, ch in enumerate(P):
            chars_T0[pos + idx] = ch
    T0 = "".join(chars_T0)

    # Генерація тексту T1 (частий збіг префікса)
    # X — перший символ SIGMA2, що не дорівнює P[m-1] (':') -> 'A'
    X = next(ch for ch in SIGMA2 if ch != P[-1])
    block_B = P[:m - 1] + X  # "std:" + "A" = "std:A"
    repeats = (n // len(block_B)) + 2
    chars_T1 = list((block_B * repeats)[:n])
    for pos in positions:
        for idx, ch in enumerate(P):
            chars_T1[pos + idx] = ch
    T1 = "".join(chars_T1)

    # Таблиці попередньої обробки
    pi = compute_prefix_function(P)
    delta = build_dfa_transitions(P, SIGMA2)

    print("=== ТАБЛИЦЯ ПРЕФІКС-ФУНКЦІЇ pi ===")
    for idx, ch in enumerate(P):
        print(f"pi[{idx}] (P[{idx}]='{ch}') = {pi[idx]}")

    # Перевірка потокового пошуку КМП (пункт д)
    print("\n=== РЕЗУЛЬТАТИ ПОТОКОВОЇ ПЕРЕВІРКИ (T0) ===")
    occ_standard, _, _ = kmp_matcher(T0, P, pi)
    for b_size in [17, 257, 4096]:
        occ_stream = kmp_stream_matcher(T0, P, pi, b_size)
        exact_match = (occ_stream == occ_standard)
        print(f"Блок {b_size:4d} символів: {len(occ_stream)} входжень | "
              f"Точний збіг зі звичайним КМП: {exact_match}")

    # Контрольні тести (пункт е)
    print("\n=== КОНТРОЛЬНІ ТЕСТИ (п. е) ===")
    tests = [
        ("ABABABA", "ABA", [0, 2, 4]),
        ("AAAAAA", "AAA", [0, 1, 2, 3]),
        ("ABCDEF", "GHI", []),
        ("A", "AAAA", [0, 1, 2, 3]),
        ("TOOLONG", "SHORT", [])
    ]
    for text_sample, pat_sample, expected in tests:
        pi_t = compute_prefix_function(pat_sample)
        res, _, _ = kmp_matcher(text_sample, pat_sample, pi_t)
        print(f"Текст '{text_sample:7s}' | Шаблон '{pat_sample:5s}' | "
              f"Знайдено: {str(res):15s} | Очікувалось: {str(expected):15s} | "
              f"Успіх: {res == expected}")


if __name__ == "__main__":
    main()