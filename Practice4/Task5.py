import sys
import time

P = 2147483647  # 2^31 - 1
MAGIC_XOR = 0x5BD1E995
MAX_EVICTIONS = 512


# ==============================================================================
# 1. ДОПОМІЖНІ МАТЕМАТИЧНІ ФУНКЦІЇ ТА ГЕНЕРАТОРИ
# ==============================================================================

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    d = 5
    while d * d <= n:
        if n % d == 0 or n % (d + 2) == 0:
            return False
        d += 6
    return True


def next_prime(n: int) -> int:
    """Повертає найменше просте число, не менше за n."""
    candidate = max(2, n)
    if candidate % 2 == 0 and candidate > 2:
        candidate += 1
    while not is_prime(candidate):
        candidate += 2
    return candidate


class LCG:
    """Лінійний конгруентний генератор псевдовипадкових чисел."""
    def __init__(self, seed: int):
        self.state = seed & 0xFFFFFFFF

    def next(self) -> int:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state


def get_hash_params(param_gen: LCG):
    """Генерація четвірки параметрів a1, b1, a2, b2."""
    u1 = param_gen.next()
    u2 = param_gen.next()
    u3 = param_gen.next()
    u4 = param_gen.next()
    a1 = 1 + (u1 % (P - 1))
    b1 = u2 % P
    a2 = 1 + (u3 % (P - 1))
    b2 = u4 % P
    return a1, b1, a2, b2


def generate_keys_U(v: int, r: int, total_needed: int) -> list:
    """Генерація унікальних ключів для набору U."""
    s0 = (1234567 + 10007 * v + 97 * r) & 0xFFFFFFFF
    gen = LCG(s0)
    seen = set()
    keys = []
    while len(keys) < total_needed:
        val = gen.next()
        k = 1 + (val % (P - 1))
        if k not in seen:
            seen.add(k)
            keys.append(k)
    return keys


def generate_keys_S(v: int, r: int, total_needed: int) -> list:
    """Генерація ключів для набору S."""
    base = 1 + 100003 * v + 8191 * r
    return [base + 2 * i for i in range(total_needed)]


# ==============================================================================
# 2. CUCKOO HASHING
# ==============================================================================

class CuckooTable:
    def __init__(self, m: int, a1: int, b1: int, a2: int, b2: int,
                 use_stash: bool = False, auto_resize: bool = False, param_gen: LCG = None):
        self.m = m
        self.a1, self.b1 = a1, b1
        self.a2, self.b2 = a2, b2
        self.use_stash = use_stash
        self.auto_resize = auto_resize
        self.param_gen = param_gen

        self.T1 = [None] * m  # комірки: None або (key, value)
        self.T2 = [None] * m
        self.stash = [] if use_stash else None
        self.n = 0

        # Статистичні лічильники
        self.cell_accesses = 0
        self.key_comparisons = 0
        self.evictions = 0
        self.rehash_attempts = 0
        self.stash_accesses = 0
        self.failed_local_inserts = 0
        self.rehash_moves = 0

    def h1(self, x: int) -> int:
        return ((self.a1 * x + self.b1) % P) % self.m

    def h2(self, x: int) -> int:
        return ((self.a2 * x + self.b2) % P) % self.m

    def search(self, key: int):
        # 1. Перевірка T1
        self.cell_accesses += 1
        i1 = ((self.a1 * key + self.b1) % P) % self.m
        entry1 = self.T1[i1]
        if entry1 is not None:
            self.key_comparisons += 1
            if entry1[0] == key:
                return True, entry1[1]

        # 2. Перевірка T2
        self.cell_accesses += 1
        i2 = ((self.a2 * key + self.b2) % P) % self.m
        entry2 = self.T2[i2]
        if entry2 is not None:
            self.key_comparisons += 1
            if entry2[0] == key:
                return True, entry2[1]

        # 3. Перевірка Stash
        if self.use_stash and self.stash:
            self.stash_accesses += 1
            for k, v in self.stash:
                self.key_comparisons += 1
                if k == key:
                    return True, v

        return False, "NOT_FOUND"

    def delete(self, key: int) -> bool:
        i1 = ((self.a1 * key + self.b1) % P) % self.m
        self.cell_accesses += 1
        if self.T1[i1] is not None:
            self.key_comparisons += 1
            if self.T1[i1][0] == key:
                self.T1[i1] = None
                self.n -= 1
                return True

        i2 = ((self.a2 * key + self.b2) % P) % self.m
        self.cell_accesses += 1
        if self.T2[i2] is not None:
            self.key_comparisons += 1
            if self.T2[i2][0] == key:
                self.T2[i2] = None
                self.n -= 1
                return True

        if self.use_stash and self.stash:
            self.stash_accesses += 1
            for idx in range(len(self.stash)):
                self.key_comparisons += 1
                if self.stash[idx][0] == key:
                    self.stash.pop(idx)
                    self.n -= 1
                    return True

        return False

    def _try_insert_with_rollback(self, key: int, value: int):
        """Локальна спроба вставлення з журналом для повного відкату."""
        journal = []  # (table_id, index, old_val)
        current = (key, value)
        curr_tbl = 1
        evict_count = 0

        while True:
            if curr_tbl == 1:
                j = ((self.a1 * current[0] + self.b1) % P) % self.m
                self.cell_accesses += 1
                old_val = self.T1[j]
                if old_val is None:
                    self.T1[j] = current
                    journal.append((1, j, old_val))
                    self.evictions += evict_count
                    return True, evict_count
                if evict_count == MAX_EVICTIONS:
                    break
                self.T1[j] = current
                journal.append((1, j, old_val))
                current = old_val
                evict_count += 1
                curr_tbl = 2
            else:
                j = ((self.a2 * current[0] + self.b2) % P) % self.m
                self.cell_accesses += 1
                old_val = self.T2[j]
                if old_val is None:
                    self.T2[j] = current
                    journal.append((2, j, old_val))
                    self.evictions += evict_count
                    return True, evict_count
                if evict_count == MAX_EVICTIONS:
                    break
                self.T2[j] = current
                journal.append((2, j, old_val))
                current = old_val
                evict_count += 1
                curr_tbl = 1

        # Повний відкат у разі невдачі
        for tbl_id, idx, old_val in reversed(journal):
            if tbl_id == 1:
                self.T1[idx] = old_val
            else:
                self.T2[idx] = old_val
        return False, evict_count

    def insert(self, key: int, value: int) -> bool:
        # Перевірка наявності для уникнення дублювання
        i1 = ((self.a1 * key + self.b1) % P) % self.m
        if self.T1[i1] is not None and self.T1[i1][0] == key:
            self.T1[i1] = (key, value)
            return True

        i2 = ((self.a2 * key + self.b2) % P) % self.m
        if self.T2[i2] is not None and self.T2[i2][0] == key:
            self.T2[i2] = (key, value)
            return True

        if self.use_stash and self.stash:
            for idx in range(len(self.stash)):
                if self.stash[idx][0] == key:
                    self.stash[idx] = (key, value)
                    return True

        # Автоматичне розширення за коефіцієнтом заповнення
        if self.auto_resize and ((self.n + 1) / (2 * self.m)) > 0.40:
            if not self._grow_and_rehash():
                return False

        # Локальна спроба
        success, _ = self._try_insert_with_rollback(key, value)
        if success:
            self.n += 1
            return True

        # Обробка невдачі
        self.failed_local_inserts += 1
        if self.use_stash:
            if len(self.stash) < 4:
                self.stash.append((key, value))
                self.n += 1
                return True
            else:
                return self._rehash_all(extra_item=(key, value))
        else:
            return self._rehash_all(extra_item=(key, value))

    def _collect_all(self):
        records = []
        for e in self.T1:
            if e is not None:
                records.append(e)
        for e in self.T2:
            if e is not None:
                records.append(e)
        if self.use_stash and self.stash:
            records.extend(self.stash)
        return records

    def _rehash_all(self, extra_item=None) -> bool:
        all_records = self._collect_all()
        if extra_item:
            all_records.append(extra_item)

        cur_m = self.m
        # Спроба на поточному розмірі (до 5 разів)
        for _ in range(5):
            self.rehash_attempts += 1
            if self.param_gen is None:
                return False
            na1, nb1, na2, nb2 = get_hash_params(self.param_gen)
            ok, t1_new, t2_new, stash_new, moves = self._try_rebuild(cur_m, na1, nb1, na2, nb2, all_records)
            if ok:
                self.T1, self.T2 = t1_new, t2_new
                self.a1, self.b1, self.a2, self.b2 = na1, nb1, na2, nb2
                if self.use_stash:
                    self.stash = stash_new
                self.n = len(all_records)
                self.rehash_moves += moves
                return True

        if not self.auto_resize:
            return False

        # Збільшення розміру
        while True:
            cur_m = next_prime(2 * cur_m + 1)
            for _ in range(5):
                self.rehash_attempts += 1
                na1, nb1, na2, nb2 = get_hash_params(self.param_gen)
                ok, t1_new, t2_new, stash_new, moves = self._try_rebuild(cur_m, na1, nb1, na2, nb2, all_records)
                if ok:
                    self.m = cur_m
                    self.T1, self.T2 = t1_new, t2_new
                    self.a1, self.b1, self.a2, self.b2 = na1, nb1, na2, nb2
                    if self.use_stash:
                        self.stash = stash_new
                    self.n = len(all_records)
                    self.rehash_moves += moves
                    return True

    def _grow_and_rehash(self) -> bool:
        return self._rehash_all(extra_item=None)

    def _try_rebuild(self, m_size, a1, b1, a2, b2, records):
        t1 = [None] * m_size
        t2 = [None] * m_size
        st = [] if self.use_stash else None
        moves = 0

        for r in records:
            current = r
            curr_tbl = 1
            evict = 0
            inserted = False
            journal = []

            while True:
                if curr_tbl == 1:
                    j = ((a1 * current[0] + b1) % P) % m_size
                    old = t1[j]
                    if old is None:
                        t1[j] = current
                        journal.append((1, j, old))
                        moves += 1
                        inserted = True
                        break
                    if evict == MAX_EVICTIONS:
                        break
                    t1[j] = current
                    journal.append((1, j, old))
                    current = old
                    evict += 1
                    moves += 1
                    curr_tbl = 2
                else:
                    j = ((a2 * current[0] + b2) % P) % m_size
                    old = t2[j]
                    if old is None:
                        t2[j] = current
                        journal.append((2, j, old))
                        moves += 1
                        inserted = True
                        break
                    if evict == MAX_EVICTIONS:
                        break
                    t2[j] = current
                    journal.append((2, j, old))
                    current = old
                    evict += 1
                    moves += 1
                    curr_tbl = 1

            if not inserted:
                # Відкат для поточного елемента
                for tbl_id, idx, old_val in reversed(journal):
                    if tbl_id == 1:
                        t1[idx] = old_val
                    else:
                        t2[idx] = old_val

                if self.use_stash and len(st) < 4:
                    st.append(r)
                else:
                    return False, None, None, None, 0

        return True, t1, t2, st, moves

    def validate(self) -> bool:
        """Перевірка інваріантів Cuckoo hashing."""
        seen = set()
        count = 0
        for i, e in enumerate(self.T1):
            if e is not None:
                k = e[0]
                if k in seen:
                    return False
                seen.add(k)
                count += 1
                if self.h1(k) != i:
                    return False

        for i, e in enumerate(self.T2):
            if e is not None:
                k = e[0]
                if k in seen:
                    return False
                seen.add(k)
                count += 1
                if self.h2(k) != i:
                    return False

        if self.use_stash and self.stash:
            for k, _ in self.stash:
                if k in seen:
                    return False
                seen.add(k)
                count += 1

        return count == self.n


# ==============================================================================
# 3. HOPSCOTCH HASHING
# ==============================================================================

class HopscotchTable:
    def __init__(self, M: int, H: int, a1: int, b1: int,
                 auto_resize: bool = False, param_gen: LCG = None):
        self.M = M
        self.H = H
        self.a1 = a1
        self.b1 = b1
        self.auto_resize = auto_resize
        self.param_gen = param_gen

        self.table = [None] * M    # (key, value)
        self.hopinfo = [0] * M     # бітова маска розміром H
        self.n = 0

        # Статистичні лічильники
        self.cell_accesses = 0
        self.key_comparisons = 0
        self.displacements = 0
        self.max_displacements_single_insert = 0
        self.probed_cells = 0
        self.rehash_attempts = 0

    def h(self, x: int) -> int:
        return ((self.a1 * x + self.b1) % P) % self.M

    def _dist(self, u: int, j: int) -> int:
        return (j - u) % self.M

    def search(self, key: int):
        home = self.h(key)
        mask = self.hopinfo[home]
        for offset in range(self.H):
            if (mask >> offset) & 1:
                idx = (home + offset) % self.M
                self.cell_accesses += 1
                entry = self.table[idx]
                if entry is not None:
                    self.key_comparisons += 1
                    if entry[0] == key:
                        return True, entry[1]
        return False, "NOT_FOUND"

    def delete(self, key: int) -> bool:
        home = self.h(key)
        mask = self.hopinfo[home]
        for offset in range(self.H):
            if (mask >> offset) & 1:
                idx = (home + offset) % self.M
                self.cell_accesses += 1
                entry = self.table[idx]
                if entry is not None:
                    self.key_comparisons += 1
                    if entry[0] == key:
                        self.table[idx] = None
                        self.hopinfo[home] &= ~(1 << offset)
                        self.n -= 1
                        return True
        return False

    def insert(self, key: int, value: int) -> str:
        home = self.h(key)
        # Оновлення значення, якщо ключ присутній в околі
        mask = self.hopinfo[home]
        for offset in range(self.H):
            if (mask >> offset) & 1:
                idx = (home + offset) % self.M
                self.cell_accesses += 1
                if self.table[idx] is not None and self.table[idx][0] == key:
                    self.table[idx] = (key, value)
                    return "UPDATED"

        # Пошук вільної комірки (циклічний probe)
        free = -1
        for step in range(self.M):
            self.probed_cells += 1
            curr = (home + step) % self.M
            self.cell_accesses += 1
            if self.table[curr] is None:
                free = curr
                break

        if free == -1:
            if self.auto_resize:
                return self._resize_and_insert(key, value)
            return "RESIZE_REQUIRED"

        # Локальні зсуви
        moves_journal = []
        insert_moves = 0

        while self._dist(home, free) >= self.H:
            moved = False
            for offset in range(self.H - 1, 0, -1):
                candidate = (free - offset) % self.M
                self.cell_accesses += 1
                cand_entry = self.table[candidate]

                if cand_entry is not None:
                    cand_home = self.h(cand_entry[0])
                    if self._dist(cand_home, free) < self.H:
                        cand_old_offset = self._dist(cand_home, candidate)
                        cand_new_offset = self._dist(cand_home, free)

                        # Переміщення
                        self.table[free] = cand_entry
                        self.table[candidate] = None

                        self.hopinfo[cand_home] &= ~(1 << cand_old_offset)
                        self.hopinfo[cand_home] |= (1 << cand_new_offset)

                        moves_journal.append((candidate, free, cand_home, cand_old_offset, cand_new_offset, cand_entry))
                        free = candidate
                        moved = True
                        insert_moves += 1
                        self.displacements += 1
                        break

            if not moved:
                # Відкат усіх зсувів
                for c_pos, f_pos, c_home, old_off, new_off, entry in reversed(moves_journal):
                    self.table[c_pos] = entry
                    self.table[f_pos] = None
                    self.hopinfo[c_home] &= ~(1 << new_off)
                    self.hopinfo[c_home] |= (1 << old_off)
                self.displacements -= len(moves_journal)

                if self.auto_resize:
                    return self._resize_and_insert(key, value)
                return "RESIZE_REQUIRED"

        if insert_moves > self.max_displacements_single_insert:
            self.max_displacements_single_insert = insert_moves

        # Розміщення нового запису
        self.table[free] = (key, value)
        self.hopinfo[home] |= (1 << self._dist(home, free))
        self.n += 1
        return "SUCCESS"

    def _resize_and_insert(self, key: int, value: int) -> str:
        all_records = [e for e in self.table if e is not None]
        all_records.append((key, value))

        cur_M = self.M
        for _ in range(4):  # Не більше 4 спроб розширення
            cur_M = next_prime(2 * cur_M + 1)
            self.rehash_attempts += 1
            if self.param_gen is None:
                return "CAPACITY_FAILURE"
            na1, nb1, _, _ = get_hash_params(self.param_gen)

            # Тимчасова таблиця
            temp = HopscotchTable(cur_M, self.H, na1, nb1, auto_resize=False)
            ok = True
            for rk, rv in all_records:
                res = temp.insert(rk, rv)
                if res not in ("SUCCESS", "UPDATED"):
                    ok = False
                    break

            if ok:
                self.M = cur_M
                self.a1, self.b1 = na1, nb1
                self.table = temp.table
                self.hopinfo = temp.hopinfo
                self.n = temp.n
                return "SUCCESS"

        return "CAPACITY_FAILURE"

    def validate(self) -> bool:
        """Перевірка коректності бітових карт та околів Hopscotch."""
        count = 0
        for i, entry in enumerate(self.table):
            if entry is not None:
                count += 1
                cand_home = self.h(entry[0])
                d = self._dist(cand_home, i)
                if d >= self.H:
                    return False
                if not ((self.hopinfo[cand_home] >> d) & 1):
                    return False

        # Перевірка відповідності бітів записам
        for u in range(self.M):
            mask = self.hopinfo[u]
            for off in range(self.H):
                if (mask >> off) & 1:
                    idx = (u + off) % self.M
                    if self.table[idx] is None or self.h(self.table[idx][0]) != u:
                        return False

        return count == self.n


# ==============================================================================
# 4. ГОЛОВНИЙ ЕКСПЕРИМЕНТ (г)
# ==============================================================================

def run_main_experiment(v: int = 3):
    print("=" * 80)
    print(f" ЕКСПЕРИМЕНТ (г): Основне дослідження (Варіант v={v})")
    print("=" * 80)

    N_list = [100000, 500000, 1000000]
    alpha_list = [0.25, 0.38]
    datasets = ['U', 'S']

    for N in N_list:
        L = 2 * N + int(0.1 * N)
        for alpha in alpha_list:
            m_cuckoo = next_prime(int(N / (2 * alpha)) + 1)
            M_hopscotch = next_prime(2 * m_cuckoo)

            for d_name in datasets:
                print(f"\n---> Конфігурація: N={N}, alpha={alpha}, Набір={d_name}")
                print(f"     Параметри: m_cuckoo={m_cuckoo}, M_hopscotch={M_hopscotch}")

                # Три повтори r in {0, 1, 2}
                for r in (0, 1, 2):
                    # 1. Генерація даних (поза таймером)
                    if d_name == 'U':
                        keys = generate_keys_U(v, r, L)
                    else:
                        keys = generate_keys_S(v, r, L)

                    # Порядок успішних пошуків: key[(37 * j) % N]
                    succ_keys = [keys[(37 * j) % N] for j in range(N)]
                    # Неуспішні пошуки: ключі з індексами N ... 2N-1
                    unsucc_keys = keys[N:2 * N]
                    D = int(0.1 * N)

                    # ----------------------------------------------------------
                    # А. ТЕСТ CUCKOO HASHING
                    # ----------------------------------------------------------
                    s0_h = (987654321 + 10007 * v + 97 * r) & 0xFFFFFFFF
                    gen_cuckoo = LCG(s0_h)
                    a1, b1, a2, b2 = get_hash_params(gen_cuckoo)

                    cuckoo = CuckooTable(m_cuckoo, a1, b1, a2, b2,
                                         use_stash=False, auto_resize=False, param_gen=gen_cuckoo)

                    # Фаза 1: Побудова
                    t0 = time.perf_counter()
                    build_failed = False
                    for i in range(N):
                        k = keys[i]
                        val = k ^ MAGIC_XOR
                        if not cuckoo.insert(k, val):
                            build_failed = True
                            break
                    t_build_cuckoo = time.perf_counter() - t0

                    if build_failed:
                        print(f"  [r={r}] Cuckoo   : BUILD_FAILED")
                    else:
                        # Фаза 2: Успішні пошуки
                        t0 = time.perf_counter()
                        for sk in succ_keys:
                            cuckoo.search(sk)
                        t_succ_cuckoo = time.perf_counter() - t0

                        # Фаза 3: Неуспішні пошуки
                        t0 = time.perf_counter()
                        for uk in unsucc_keys:
                            cuckoo.search(uk)
                        t_unsucc_cuckoo = time.perf_counter() - t0

                        # Фаза 4: Модифікації
                        t0 = time.perf_counter()
                        mod_fail = False
                        for t in range(D):
                            del_k = keys[(73 * t) % N]
                            ins_k = keys[2 * N + t]
                            cuckoo.delete(del_k)
                            if not cuckoo.insert(ins_k, ins_k ^ MAGIC_XOR):
                                mod_fail = True
                                print(f"  [r={r}] Cuckoo   : INSERT_FAILED на кроці t={t}")
                                break
                        t_mod_cuckoo = time.perf_counter() - t0

                        if not mod_fail:
                            print(f"  [r={r}] Cuckoo   | Build: {t_build_cuckoo:.3f}s | "
                                  f"Succ: {t_succ_cuckoo:.3f}s | Unsucc: {t_unsucc_cuckoo:.3f}s | "
                                  f"Mod: {t_mod_cuckoo:.3f}s | Evict: {cuckoo.evictions} | Rehash: {cuckoo.rehash_attempts}")

                    # ----------------------------------------------------------
                    # Б. ТЕСТ HOPSCOTCH HASHING
                    # ----------------------------------------------------------
                    gen_hop = LCG(s0_h)
                    ha1, hb1, _, _ = get_hash_params(gen_hop)

                    hop = HopscotchTable(M_hopscotch, H=16, a1=ha1, b1=hb1,
                                         auto_resize=False, param_gen=gen_hop)

                    # Фаза 1: Побудова
                    t0 = time.perf_counter()
                    hop_build_fail = False
                    for i in range(N):
                        k = keys[i]
                        val = k ^ MAGIC_XOR
                        res = hop.insert(k, val)
                        if res not in ("SUCCESS", "UPDATED"):
                            hop_build_fail = True
                            break
                    t_build_hop = time.perf_counter() - t0

                    if hop_build_fail:
                        print(f"  [r={r}] Hopscotch: BUILD_FAILED")
                    else:
                        # Фаза 2: Успішні пошуки
                        t0 = time.perf_counter()
                        for sk in succ_keys:
                            hop.search(sk)
                        t_succ_hop = time.perf_counter() - t0

                        # Фаза 3: Неуспішні пошуки
                        t0 = time.perf_counter()
                        for uk in unsucc_keys:
                            hop.search(uk)
                        t_unsucc_hop = time.perf_counter() - t0

                        # Фаза 4: Модифікації
                        t0 = time.perf_counter()
                        hop_mod_fail = False
                        for t in range(D):
                            del_k = keys[(73 * t) % N]
                            ins_k = keys[2 * N + t]
                            hop.delete(del_k)
                            res = hop.insert(ins_k, ins_k ^ MAGIC_XOR)
                            if res not in ("SUCCESS", "UPDATED"):
                                hop_mod_fail = True
                                print(f"  [r={r}] Hopscotch: INSERT_FAILED на кроці t={t}")
                                break
                        t_mod_hop = time.perf_counter() - t0

                        if not hop_mod_fail:
                            print(f"  [r={r}] Hopscotch| Build: {t_build_hop:.3f}s | "
                                  f"Succ: {t_succ_hop:.3f}s | Unsucc: {t_unsucc_hop:.3f}s | "
                                  f"Mod: {t_mod_hop:.3f}s | Displ: {hop.displacements}")


# ==============================================================================
# 5. ДОСЛІДЖЕННЯ ПАРАМЕТРІВ (ґ)
# ==============================================================================

def run_parameter_study(v: int = 3):
    print("\n" + "=" * 80)
    print(f" ЕКСПЕРИМЕНТ (ґ): Дослідження параметрів алгоритмів (Варіант v={v})")
    print("=" * 80)

    N = 200000
    datasets = ['U', 'S']

    # 1. Hopscotch дослідження (H, alpha)
    print("\n>>> Частина 1: Hopscotch Hashing (вплив H та alpha)")
    H_list = [8, 16, 32]
    alpha_hop_list = [0.60, 0.75, 0.85]

    for d_name in datasets:
        print(f"\n--- Набір даних: {d_name} ---")
        for H in H_list:
            for alpha in alpha_hop_list:
                M = next_prime(int(N / alpha) + 1)
                for r in (0, 1, 2):
                    if d_name == 'U':
                        keys = generate_keys_U(v, r, N)
                    else:
                        keys = generate_keys_S(v, r, N)

                    s0_h = (987654321 + 10007 * v + 97 * r) & 0xFFFFFFFF
                    gen = LCG(s0_h)
                    a1, b1, _, _ = get_hash_params(gen)

                    table = HopscotchTable(M, H, a1, b1, auto_resize=False)
                    inserted_cnt = 0
                    for k in keys:
                        res = table.insert(k, k ^ MAGIC_XOR)
                        if res in ("SUCCESS", "UPDATED"):
                            inserted_cnt += 1
                        else:
                            break

                    actual_alpha = inserted_cnt / M
                    print(f"H={H:2d} | alpha_target={alpha:.2f} | r={r} | "
                          f"Вставлено: {inserted_cnt:6d}/{N} | "
                          f"Фактичний alpha: {actual_alpha:.4f} | "
                          f"Зсувів (сум/макс): {table.displacements:7d} / {table.max_displacements_single_insert:3d} | "
                          f"Комірок перевірено: {table.probed_cells}")

    # 2. Cuckoo порівняння зі Stash
    print("\n>>> Частина 2: Cuckoo Hashing проти Cuckoo + Stash (alpha=0.38, auto_resize=True)")
    alpha_cuckoo = 0.38
    m_base = next_prime(int(N / (2 * alpha_cuckoo)) + 1)

    for d_name in datasets:
        print(f"\n--- Набір даних: {d_name} ---")
        for use_st in [False, True]:
            mode_str = "Cuckoo + Stash (cap=4)" if use_st else "Звичайний Cuckoo"
            for r in (0, 1, 2):
                if d_name == 'U':
                    keys = generate_keys_U(v, r, N)
                else:
                    keys = generate_keys_S(v, r, N)

                s0_h = (987654321 + 10007 * v + 97 * r) & 0xFFFFFFFF
                gen = LCG(s0_h)
                a1, b1, a2, b2 = get_hash_params(gen)

                cuckoo = CuckooTable(m_base, a1, b1, a2, b2,
                                     use_stash=use_st, auto_resize=True, param_gen=gen)

                for k in keys:
                    cuckoo.insert(k, k ^ MAGIC_XOR)

                print(f"[{mode_str:22s}] r={r} | Записів: {cuckoo.n} | "
                      f"Невдалих лок. спроб: {cuckoo.failed_local_inserts:4d} | "
                      f"Витіснень: {cuckoo.evictions:6d} | "
                      f"Перебудов: {cuckoo.rehash_attempts:2d} | "
                      f"Звернень до Stash: {cuckoo.stash_accesses:4d} | "
                      f"Зсувів при рехеші: {cuckoo.rehash_moves:6d}")


# ==============================================================================
# ТОЧКА ВХОДУ
# ==============================================================================

if __name__ == "__main__":
    # За замовчуванням встановлено варіант 3
    VARIANT = 3
    print(f"Запуск комплексу тестування хеш-таблиць. Обрано варіант v={VARIANT}\n")

    # 1. Запуск дослідження параметрів
    run_parameter_study(v=VARIANT)

    # 2. Запуск основного бенчмарку
    # (Для швидкої демонстрації можна викликати run_main_experiment)
    run_main_experiment(v=VARIANT)