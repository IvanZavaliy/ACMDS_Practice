import random
import string
import time


def compute_transition_function(pattern: str, alphabet: list[str]) -> dict:
    """Побудова функції переходів детермінованого скінченного автомата δ(q, a)."""
    m = len(pattern)
    delta = {}

    for q in range(m + 1):
        for a in alphabet:
            # Рядок, утворений префіксом довжини q і новим символом a
            combined = pattern[:q] + a

            # Шукаємо найбільше k (0 <= k <= m), для якого префікс шаблону
            # довжини k є суфіксом рядка combined
            k = min(m, q + 1)
            while k > 0:
                if combined.endswith(pattern[:k]):
                    break
                k -= 1
            delta[(q, a)] = k

    return delta


def finite_automaton_matcher(text: str, delta: dict, m: int):
    """Пошук усіх входжень шаблону за один прохід тексту T."""
    q = 0
    matches = []

    # Текст сканується рівно один раз без повернення каретки (backtracking)
    for i, ch in enumerate(text):
        q = delta.get((q, ch), 0)
        if q == m:
            # Збіг закінчується в поточній позиції i,
            # початковий індекс: i - m + 1
            start_pos = i - m + 1
            matches.append((start_pos, i))

    return matches


def main():
    variant = 3
    pattern = "std::"
    m = len(pattern)
    text_len = 100_000
    insert_positions = [1000, 25000, 50000, 75000, 95000]

    # Формування алфавіту Σ: C/C++-подібні символи
    special_chars = "(){}[];,.=+-*/<>!&:"
    alphabet = sorted(list(set(
        string.ascii_uppercase +
        string.ascii_lowercase +
        string.digits +
        "_" + " " + special_chars
    )))

    # 1. Генерація тексту довжиною 100 000 символів (seed = 3)
    random.seed(variant)
    text_chars = random.choices(alphabet, k=text_len)

    # 2. Вставка шаблону у вказані позиції
    for pos in insert_positions:
        for offset, ch in enumerate(pattern):
            text_chars[pos + offset] = ch

    text = "".join(text_chars)

    # 3. Побудова функції переходів δ
    t0_build = time.perf_counter()
    delta = compute_transition_function(pattern, alphabet)
    t_build = time.perf_counter() - t0_build

    # 4. Пошук за допомогою автомата
    t0_search = time.perf_counter()
    found_matches = finite_automaton_matcher(text, delta, m)
    t_search = time.perf_counter() - t0_search

    # Виведення результатів
    print(f"Розмір алфавіту |Σ|: {len(alphabet)}")
    print(f"Довжина тексту:    {len(text)} символів")
    print(f"Довжина шаблону m: {m} символів ('{pattern}')")
    print(f"Час побудови автомата: {t_build * 1000:.3f} мс")
    print(f"Час пошуку в тексті:   {t_search * 1000:.3f} мс\n")

    print(f"Знайдено входжень: {len(found_matches)}")
    print("Список входжень [індекс початку, індекс кінця]:")
    for start, end in found_matches:
        snippet = text[start:end + 1]
        print(f"  Позиція {start:5d} .. {end:5d} -> фрагмент: '{snippet}'")


if __name__ == "__main__":
    main()