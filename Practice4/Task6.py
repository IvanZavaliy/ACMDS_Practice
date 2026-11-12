import string
import time


def build_last(P: str) -> dict:
    """Побудова таблиці останніх входжень символів last(c)."""
    last = {c: -1 for c in string.ascii_uppercase}
    for idx, c in enumerate(P):
        last[c] = idx
    return last


def build_good_suffix(P: str) -> list:
    """Побудова масиву допустимих зсувів GS за сильною евристикою хорошого суфікса."""
    m = len(P)
    GS = [0] * (m + 1)
    border = [0] * (m + 1)
    i = m
    j = m + 1
    border[i] = j

    while i > 0:
        while j <= m and P[i - 1] != P[j - 1]:
            if GS[j] == 0:
                GS[j] = j - i
            j = border[j]
        i -= 1
        j -= 1
        border[i] = j

    j = border[0]
    for i in range(m + 1):
        if GS[i] == 0:
            GS[i] = j
        if i == j:
            j = border[j]

    return GS


def naive_matcher(T: str, P: str):
    """Наївний пошук зліва направо."""
    n = len(T)
    m = len(P)
    comparisons = 0
    occurrences = []

    for s in range(n - m + 1):
        matched = True
        for j in range(m):
            comparisons += 1
            if T[s + j] != P[j]:
                matched = False
                break
        if matched:
            occurrences.append(s)

    return occurrences, comparisons


def bm_bc_matcher(T: str, P: str, last: dict):
    """Алгоритм Боєра-Мура лише з евристикою поганого символу."""
    n = len(T)
    m = len(P)
    comparisons = 0
    shifts_count = 0
    shifts_total_len = 0
    occurrences = []
    s = 0

    while s <= n - m:
        j = m - 1
        while j >= 0:
            comparisons += 1
            if P[j] == T[s + j]:
                j -= 1
            else:
                break
        if j < 0:
            occurrences.append(s)
            shift = 1  # зсув на 1 для збереження перекривних входжень
        else:
            bad = max(1, j - last.get(T[s + j], -1))
            shift = bad

        shifts_count += 1
        shifts_total_len += shift
        s += shift

    return occurrences, comparisons, shifts_count, shifts_total_len


def bm_full_matcher(T: str, P: str, last: dict, GS: list):
    """Повний алгоритм Боєра-Мура (поганий символ + хороший суфікс)."""
    n = len(T)
    m = len(P)
    comparisons = 0
    shifts_count = 0
    shifts_total_len = 0
    occurrences = []
    s = 0

    while s <= n - m:
        j = m - 1
        while j >= 0:
            comparisons += 1
            if P[j] == T[s + j]:
                j -= 1
            else:
                break
        if j < 0:
            occurrences.append(s)
            shift = GS[0]
        else:
            bad = max(1, j - last.get(T[s + j], -1))
            shift = max(bad, GS[j + 1])

        shifts_count += 1
        shifts_total_len += shift
        s += shift

    return occurrences, comparisons, shifts_count, shifts_total_len


def rabin_karp_matcher(T: str, P: str, p: int, q: int):
    """Алгоритм Рабіна-Карпа з кодуванням A=0...Z=25."""
    n = len(T)
    m = len(P)
    h = pow(p, m - 1, q)
    p_hash = 0
    t_hash = 0

    for i in range(m):
        p_hash = (p_hash * p + (ord(P[i]) - 65)) % q
        t_hash = (t_hash * p + (ord(T[i]) - 65)) % q

    occurrences = []
    hash_matches = 0
    char_checks = 0
    false_matches = 0

    for s in range(n - m + 1):
        if p_hash == t_hash:
            hash_matches += 1
            matched = True
            for j in range(m):
                char_checks += 1
                if T[s + j] != P[j]:
                    matched = False
                    break
            if matched:
                occurrences.append(s)
            else:
                false_matches += 1

        if s < n - m:
            t_hash = ((t_hash - (ord(T[s]) - 65) * h) * p + (ord(T[s + m]) - 65)) % q
            if t_hash < 0:
                t_hash += q

    return occurrences, hash_matches, char_checks, false_matches


def measure_median_time(func, runs=5):
    """Вимірювання медіанного часу за 5 запусків."""
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        func()
        t1 = time.perf_counter()
        times.append(t1 - t0)
    times.sort()
    return times[runs // 2]


# ==============================================================================
# ОСНОВНИЙ БЛОК ВИКОНАННЯ
# ==============================================================================
def main():
    v = 3
    pattern = "SEARCH"
    m = len(pattern)
    n = 100_000
    positions = [1000, 25000, 50000, 75000, 95000]
    p_rk = 41
    q_rk = 1019

    # 1. Генерація тексту T0
    s_val = v
    sigma = string.ascii_uppercase
    chars_T0 = []
    for _ in range(n):
        s_val = (1664525 * s_val + 1013904223) & 0xFFFFFFFF
        chars_T0.append(sigma[s_val % 26])

    for pos in positions:
        for idx, ch in enumerate(pattern):
            chars_T0[pos + idx] = ch
    T0 = "".join(chars_T0)

    # 2. Генерація тексту T1 (велике число часткових збігів)
    X = "Z" if pattern[0] != "Z" else "Y"
    block_B = X + pattern[1:]  # 'ZEARCH'
    repeats = (n // len(block_B)) + 2
    chars_T1 = list((block_B * repeats)[:n])
    for pos in positions:
        for idx, ch in enumerate(pattern):
            chars_T1[pos + idx] = ch
    T1 = "".join(chars_T1)

    # 3. Попередня обробка
    last = build_last(pattern)
    GS = build_good_suffix(pattern)

    print("=== ТАБЛИЦЯ LAST (для присутніх символів) ===")
    for k in sorted(last.keys()):
        if last[k] != -1:
            print(f"last('{k}') = {last[k]}", end="  ")
    print(f"\nДля решти символів last(c) = -1")

    print(f"\n=== ТАБЛИЦЯ GOOD SUFFIX GS ===")
    print(f"GS = {GS}\n")

    # 4. Контрольні випробування (пункт д)
    print("=== КОНТРОЛЬНІ ВИПРОБУВАННЯ (п. д) ===")
    control_cases = [
        ("AAAA", "AAAAAAAA"),
        ("ABABA", "ABABABA"),
        ("ABCAB", "ABCABCAB"),
        ("XYZ", "AAAAAA"),
        ("A", "AAAA"),
        ("TOOLONG", "SHORT"),
    ]
    for p_pat, t_text in control_cases:
        l_c = build_last(p_pat)
        gs_c = build_good_suffix(p_pat)
        occ, _, sc, _ = bm_full_matcher(t_text, p_pat, l_c, gs_c)
        print(f"P='{p_pat:7s}' | T='{t_text:10s}' | Входження: {str(occ):15s} | GS={gs_c} | Зсувів: {sc}")


if __name__ == "__main__":
    main()