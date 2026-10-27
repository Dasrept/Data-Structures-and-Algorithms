#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией.

Решение для варианта 6. Подробное описание эксперимента находится в
lab03-report.md. Запуск: python lab03-simple-sorts-quicksort.py --variant 6.
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
import time
from pathlib import Path
from typing import Any, Callable

# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


def bubble_sort(a: list, key: Callable[[Any], Any] | None = None) -> tuple[list, int, int]:
    """Сортировка пузырьком; возвращает копию, сравнения и число обменов.

    Худший и средний случаи O(n²), лучший O(n) благодаря раннему выходу.
    Обмены считаются одной операцией за перестановку соседней пары.
    """
    result = list(a)
    key = key or (lambda value: value)
    comparisons = swaps = 0
    for end in range(len(result) - 1, 0, -1):
        changed = False
        for i in range(end):
            comparisons += 1
            if key(result[i]) > key(result[i + 1]):
                result[i], result[i + 1] = result[i + 1], result[i]
                swaps += 1
                changed = True
        if not changed:
            break
    return result, comparisons, swaps


def insertion_sort(a: list, key: Callable[[Any], Any] | None = None) -> tuple[list, int, int]:
    """Сортировка вставками; moves — сдвиги плюс запись вставляемого ключа.

    Лучший случай O(n), средний и худший O(n²). Строгое сравнение сохраняет
    порядок элементов с равными ключами.
    """
    result = list(a)
    key = key or (lambda value: value)
    comparisons = moves = 0
    for i in range(1, len(result)):
        item = result[i]
        item_key = key(item)
        j = i - 1
        while j >= 0:
            comparisons += 1
            if key(result[j]) > item_key:
                result[j + 1] = result[j]
                moves += 1
                j -= 1
            else:
                break
        result[j + 1] = item
        moves += 1
    return result, comparisons, moves


def selection_sort(a: list, key: Callable[[Any], Any] | None = None) -> tuple[list, int, int]:
    """Сортировка выбором: Θ(n²) сравнений при любом порядке входа."""
    result = list(a)
    key = key or (lambda value: value)
    comparisons = swaps = 0
    for i in range(len(result) - 1):
        minimum = i
        for j in range(i + 1, len(result)):
            comparisons += 1
            if key(result[j]) < key(result[minimum]):
                minimum = j
        if minimum != i:
            result[i], result[minimum] = result[minimum], result[i]
            swaps += 1
    return result, comparisons, swaps


# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным опорным элементом
# ---------------------------------------------------------------------------


def quick_sort(
    a: list,
    rng: random.Random | None = None,
    key: Callable[[Any], Any] | None = None,
    stats: dict[str, int] | None = None,
) -> list:
    """Рандомизированный QuickSort с трёхпутевым разбиением.

    Среднее время O(n log n), худшее O(n²); стек O(log n) из-за рекурсии по
    меньшей части. При переданном stats записывает сравнения и обмены.
    Функция всегда сортирует копию и возвращает новый список.
    """
    if rng is None:
        rng = random.Random()
    key = key or (lambda value: value)
    result = list(a)
    counts = stats if stats is not None else {}
    counts["comparisons"] = 0
    counts["moves"] = 0

    def swap(i: int, j: int) -> None:
        if i != j:
            result[i], result[j] = result[j], result[i]
            counts["moves"] += 1

    def sort_range(lo: int, hi: int) -> None:
        while hi - lo > 1:
            pivot_key = key(result[rng.randrange(lo, hi)])
            lt = i = lo
            gt = hi
            while i < gt:
                counts["comparisons"] += 1
                current_key = key(result[i])
                if current_key < pivot_key:
                    swap(lt, i)
                    lt += 1
                    i += 1
                else:
                    counts["comparisons"] += 1
                    if current_key > pivot_key:
                        gt -= 1
                        swap(i, gt)
                    else:
                        i += 1

            left_size = lt - lo
            right_size = hi - gt
            if left_size < right_size:
                sort_range(lo, lt)
                lo = gt
            else:
                sort_range(gt, hi)
                hi = lt

    sort_range(0, len(result))
    return result


# ---------------------------------------------------------------------------
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------


def stability_demo() -> None:
    """Показать, какие из четырёх сортировок стабильны.

    Сравнение выполняется только по первому полю пары, чтобы метки не
    превращались в дополнительный критерий сортировки.
    """
    data = [(2, "a"), (2, "b"), (1, "c")]
    key = lambda pair: pair[0]
    outputs = {
        "bubble_sort": bubble_sort(data, key)[0],
        "insertion_sort": insertion_sort(data, key)[0],
        "selection_sort": selection_sort(data, key)[0],
        "quick_sort": quick_sort(data, random.Random(0), key),
    }
    print("\nДемонстрация стабильности (порядок меток для ключа 2):")
    for name, result in outputs.items():
        labels = [label for value, label in result if value == 2]
        stability = "стабильна" if labels == ["a", "b"] else "нестабильна"
        print(f"  {name:16s} {result} — {stability}")


# ---------------------------------------------------------------------------
# 4. Классы входов (данные по варианту, детерминированно по seed)
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три класса входов размера n: упорядоченный, случайный, обратный."""
    rng = random.Random(seed + n)  # свой поток для каждого размера
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация: порядок, перестановка, граничные случаи и эталон
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    """Инвариант 1: неубывающий порядок элементов."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


def expect(condition: bool, message: str) -> None:
    """Проверка не отключается флагом python -O."""
    if not condition:
        raise RuntimeError(message)


def stable_for_example(data: list, result: list) -> bool:
    """Проверить сохранение порядка меток внутри равных ключей."""
    keys = {pair[0] for pair in data}
    return all(
        [label for key, label in data if key == value]
        == [label for key, label in result if key == value]
        for value in keys
    )


def self_check() -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for name, fn in ALGORITHMS.items():
        for a in boundary:
            res = fn(list(a))
            expect(isinstance(res, list), f"{name}: результат должен быть list")
            expect(is_sorted(res), f"{name}: нарушен порядок на {a}")
            expect(sorted(res) == sorted(a), f"{name}: не перестановка входа {a}")
            expect(res is not a, f"{name}: функция должна вернуть новую копию")

    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        expected = sorted(a)
        for name, fn in ALGORITHMS.items():
            source = list(a)
            result = fn(source)
            expect(result == expected, f"{name}: расходится с sorted() на {a}")
            expect(source == a, f"{name}: функция изменила входной список")

    # Проверка точных известных счётчиков на пяти элементах.
    _, bubble_sorted_cmp, bubble_sorted_swaps = bubble_sort([1, 2, 3, 4, 5])
    expect((bubble_sorted_cmp, bubble_sorted_swaps) == (4, 0),
           "bubble_sort: счётчик лучшего случая неверен")
    _, bubble_reverse_cmp, bubble_reverse_swaps = bubble_sort([5, 4, 3, 2, 1])
    expect((bubble_reverse_cmp, bubble_reverse_swaps) == (10, 10),
           "bubble_sort: счётчик обратного порядка неверен")
    _, insertion_sorted_cmp, insertion_sorted_moves = insertion_sort([1, 2, 3, 4, 5])
    expect((insertion_sorted_cmp, insertion_sorted_moves) == (4, 4),
           "insertion_sort: счётчик лучшего случая неверен")
    _, insertion_reverse_cmp, insertion_reverse_moves = insertion_sort([5, 4, 3, 2, 1])
    expect((insertion_reverse_cmp, insertion_reverse_moves) == (10, 14),
           "insertion_sort: счётчик обратного порядка неверен")
    for data in ([1, 2, 3, 4, 5], [5, 4, 3, 2, 1], [3, 1, 2, 5, 4]):
        _, comparisons, _ = selection_sort(data)
        expect(comparisons == len(data) * (len(data) - 1) // 2,
               "selection_sort: число сравнений должно быть n*(n-1)/2")

    pairs = [(2, "a"), (2, "b"), (1, "c")]
    stability_results = (
        bubble_sort(pairs, key=lambda pair: pair[0])[0],
        insertion_sort(pairs, key=lambda pair: pair[0])[0],
        selection_sort(pairs, key=lambda pair: pair[0])[0],
        quick_sort(pairs, random.Random(0), key=lambda pair: pair[0]),
    )
    statuses = [stable_for_example(pairs, result) for result in stability_results]
    expect(statuses == [True, True, False, False],
           f"демонстрация стабильности дала неожиданные результаты: {statuses}")

    stats: dict[str, int] = {}
    quick_result = quick_sort([5, 3, 1, 4, 2], random.Random(3), stats=stats)
    expect(quick_result == [1, 2, 3, 4, 5], "quick_sort: ошибка на счётном тесте")
    expect(stats["comparisons"] > 0 and stats["moves"] >= 0,
           "quick_sort: счётчики не заполнены")
    print("self_check:")
    print("  граничные случаи и 300 случайных массивов на алгоритм: OK")
    print("  инварианты порядка и перестановки, вход не меняется: OK")
    print("  счётчики сравнений/обменов/перемещений: OK")
    print("  стабильность: пузырёк и вставки стабильны; выбор и QuickSort — нет: OK")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 6. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]     # для простых сортировок
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]   # для QuickSort
REPEATS = 5


def bench(fn, data: list) -> float:
    """Медиана времени выполнения fn(копия data) по REPEATS запускам, с прогревом."""
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        arg = list(data)  # свежая копия: сортировка не должна получать свой результат
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def sort_with_counts(name: str, data: list, seed: int) -> tuple[list, int, int]:
    """Запустить один алгоритм и вернуть результат с двумя счётчиками."""
    if name == "bubble_sort":
        return bubble_sort(data)
    if name == "insertion_sort":
        return insertion_sort(data)
    if name == "selection_sort":
        return selection_sort(data)
    stats: dict[str, int] = {}
    result = quick_sort(data, random.Random(seed), stats=stats)
    return result, stats["comparisons"], stats["moves"]


def log_log_slope(points: list[tuple[int, float]]) -> float:
    """Линейная регрессия log10(time) по log10(n)."""
    xs = [math.log10(n) for n, _ in points]
    ys = [math.log10(seconds) for _, seconds in points]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = sum((x - mean_x) ** 2 for x in xs)
    return numerator / denominator


def plot_results(results: dict, out_dir: Path) -> None:
    """Сохранить log-log графики простых сортировок и QuickSort."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    classes = ("упорядоченный", "случайный", "обратный")
    simple_names = ("bubble_sort", "insertion_sort", "selection_sort")
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    for axis, name in zip(axes, simple_names):
        for class_name in classes:
            points = results[name][class_name]
            axis.plot(
                [n for n, _ in points],
                [seconds for _, seconds in points],
                marker="o",
                label=f"{class_name} (наклон {log_log_slope(points):.2f})",
            )
        axis.set_xscale("log")
        axis.set_yscale("log")
        axis.set_title(name)
        axis.set_xlabel("размер массива n")
        axis.grid(True, which="both", linewidth=0.35)
        axis.legend(fontsize=8)
    axes[0].set_ylabel("медианное время, с")
    fig.suptitle("Простые сортировки: log-log")
    fig.tight_layout()
    fig.savefig(out_dir / "lab03_simple_sorts.png", dpi=150)
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(8, 5))
    for class_name in classes:
        points = results["quick_sort"][class_name]
        axis.plot(
            [n for n, _ in points],
            [seconds for _, seconds in points],
            marker="o",
            label=f"{class_name} (наклон {log_log_slope(points):.2f})",
        )
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.set_title("Рандомизированный QuickSort: log-log")
    axis.set_xlabel("размер массива n")
    axis.set_ylabel("медианное время, с")
    axis.grid(True, which="both", linewidth=0.35)
    axis.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "lab03_quick_sort.png", dpi=150)
    plt.close(fig)


def write_csv(results: dict, counters: list[dict], out_dir: Path) -> None:
    """Сохранить все точки времени и счётчики для отчёта."""
    with (out_dir / "lab03_timings.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(("algorithm", "input_class", "n", "median_seconds", "log_log_slope"))
        for algorithm, groups in results.items():
            for class_name, points in groups.items():
                slope = log_log_slope(points)
                for n, seconds in points:
                    writer.writerow((algorithm, class_name, n, f"{seconds:.9g}", f"{slope:.4f}"))

    with (out_dir / "lab03_counters.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file, fieldnames=("algorithm", "input_class", "n", "comparisons", "moves_or_swaps")
        )
        writer.writeheader()
        writer.writerows(counters)


def run_benchmarks(seed: int, out_dir: Path) -> dict:
    """Замерить четыре алгоритма на трёх классах входа варианта."""
    out_dir.mkdir(parents=True, exist_ok=True)
    plans = (
        ("bubble_sort", SIZES_QUADRATIC),
        ("insertion_sort", SIZES_QUADRATIC),
        ("selection_sort", SIZES_QUADRATIC),
        ("quick_sort", SIZES_QUICK),
    )
    results: dict[str, dict[str, list[tuple[int, float]]]] = {}
    counters: list[dict] = []
    for name, sizes in plans:
        results[name] = {class_name: [] for class_name in make_inputs(1, seed)}
        print(f"\n{name} — время (медиана {REPEATS} повторов):")
        for n in sizes:
            for class_name, data in make_inputs(n, seed).items():
                fn = lambda values, alg=name, base=seed: sort_with_counts(alg, values, base)[0]
                seconds = bench(fn, data)
                _, comparisons, moves = sort_with_counts(name, data, seed)
                results[name][class_name].append((n, seconds))
                counters.append({
                    "algorithm": name,
                    "input_class": class_name,
                    "n": n,
                    "comparisons": comparisons,
                    "moves_or_swaps": moves,
                })
                print(
                    f"  n={n:>7} {class_name:<13} t={seconds:.3e} c "
                    f"comparisons={comparisons:>12,} moves/swaps={moves:>12,}"
                )

    print("\nНаклоны log-log регрессии:")
    for name, groups in results.items():
        for class_name, points in groups.items():
            print(f"  {name:16s} {class_name:<13} {log_log_slope(points):.3f}")

    write_csv(results, counters, out_dir)
    plot_results(results, out_dir)
    print(f"\nCSV и графики сохранены в: {out_dir.resolve()}")
    return results


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    ap.add_argument("--out", type=Path, default=Path("lab03"),
                    help="каталог для CSV и графиков (по умолчанию lab03)")
    args = ap.parse_args()
    if args.variant < 0:
        ap.error("номер варианта должен быть неотрицательным")
    seed = 30 + args.variant
    print(f"Вариант {args.variant}, seed={seed}")
    self_check()
    stability_demo()
    run_benchmarks(seed, args.out)


if __name__ == "__main__":
    main()
