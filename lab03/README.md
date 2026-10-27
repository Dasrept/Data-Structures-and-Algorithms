# Лабораторная работа 3

**Вариант 6.** Простые сортировки и QuickSort с рандомизированным опорным элементом.

- Код: [`lab03-simple-sorts-quicksort.py`](lab03-simple-sorts-quicksort.py)
- Отчёт: [`lab03-report.md`](lab03-report.md)
- Все значения счётчиков: [`lab03_counters.csv`](lab03_counters.csv)
- Все результаты замеров: [`lab03_timings.csv`](lab03_timings.csv)
- Графики: [`lab03_simple_sorts.png`](lab03_simple_sorts.png), [`lab03_quick_sort.png`](lab03_quick_sort.png)
- Отдельная копия полного кода: [`lab03-full-code.py`](lab03-full-code.py)

Из корня репозитория запусти:

```powershell
python lab03/lab03-simple-sorts-quicksort.py --variant 6 --out lab03
```

Программа сначала запускает проверки, затем повторяет бенчмарк: для каждой точки один прогрев и пять измерений, результатом служит медиана. Seed для варианта 6 равен `36`.
