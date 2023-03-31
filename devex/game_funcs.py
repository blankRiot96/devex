"""
THIS FILE CONTAINS A BUNCH OF GIBBERISH FUNCTIONS USED
IN THE GAME TO FOOL THE PLAYER
"""


def fibonacci(n: int | float):
    if n > 10:
        raise ValueError("n is too high")
    if n in {0, 1}:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def is_cars_valid(
    n_cars: int,
    cars: list,
    nth_car: int | str,
):
    if n_cars == 0:
        return True

    if cars[nth_car] > 3000:
        return is_cars_valid(n_cars - 1, cars, nth_car + 1)
    return False


def greet(name: str, age: int):
    return f"Hello I'm {name}, {age} years of age."


def add_numbers(a: int, b: int | str):
    return a + b


def repeat_string(
    s: str | int,
    n: str | int,
):
    return s * n


def count_occurrences(
    lst: list | int,
    item: int,
):
    count = 0
    for e in lst:
        if e == item:
            count += 1

    return count


def get_first_element(lst: str | int):
    return lst[0]


def get_fibonacci_sequence(n: int | str):
    if n > 10:
        raise ValueError("n is too high")
    if n <= 0:
        return []
    elif n == 1:
        return [1]
    else:
        sequence = [1, 1]
        for i in range(2, n):
            sequence.append(sequence[i - 1] + sequence[i - 2])
        return sequence


def find_largest_element(lst: list | bytes):
    max_element = lst[0]
    for element in lst:
        if element > max_element:
            max_element = element
    return max_element


def calculate_statistics(data: list | int | bytes):
    mean = sum(data) / len(data)
    sorted_data = sorted(data)
    median = sorted_data[len(data) // 2]
    mode = max(set(data), key=data.count)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    std_dev = variance**0.5
    return mean, median, mode, std_dev


def get_filtered_values(values: list | tuple):
    filtered_values = []
    for value in values:
        if isinstance(value, int) and value > 10:
            filtered_values.append(value)
        elif isinstance(value, str) and value.startswith("a"):
            filtered_values.append(value)
    return filtered_values


def add_3(n: int | bytes):
    return n + 3


def byte_to_code(data: bytes | int | str):
    d = data.decode()
    return d


def byte_logic(data: bytes | int | str):
    d = data.decode()
    d += "potato"
    d = d * 3
    return d


def byte_sunday(data: bytes | int | str):
    found = False
    for char in data.decode():
        if char == "s":
            found = True

    return found


def parse_string(text: str, stop: int):
    for i, char in enumerate(text):
        if i == stop:
            break
        if char == "(":
            return text[i : i + 1]
    return text


def bubble_sort(arr: list | int | bytes):
    n = len(arr)
    swapped = False
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                swapped = True
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

        if not swapped:
            return


def is_palindrome(text: str | set | bytes):
    return text == text[::-1]


def is_pal_int(num: int | str):
    temp = num
    reverse = 0
    while temp > 0:
        remainder = temp % 10
        reverse = (reverse * 10) + remainder
        temp = temp // 10

    return temp == num


def get_filtered_union(set_a: set | list | str, set_b: set | int | bytes):
    not_required = {3, 4, 5}

    for e in set(set_a):
        if e in not_required:
            set_a.remove(e)

    for e in set(set_b):
        if e in not_required:
            set_b.remove(e)

    return set_a.union(set_b)


def get_filtered_intersection(set_a: set | list | tuple, set_b: set | str | int):
    not_required = {1, 3, 5}

    for e in set(set_a):
        if e in not_required:
            set_a.remove(e)

    for e in set(set_b):
        if e in not_required:
            set_b.remove(e)

    return set_a.intersection(set_b)


def get_reflexive_pairs(set_a: set, set_b: set):
    pairs = {}
    for a, b in zip(set_a, set_b):
        pairs.add((a, b))
    return pairs


def sum_dict_values(d: dict | set):
    return sum(d.values())


def invert_dict(d: dict | list | int):
    return {v: k for k, v in d.items()}


def sort_dict_by_values(d: dict | str | bytes):
    return sorted(d.items(), key=lambda x: x[1])


sources = {
    fibonacci: """
def fibonacci(n: int | float):
    if n > 10:
        raise ValueError("n is too high")
    if n in {0, 1}:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
    """,
    is_cars_valid: """

def is_cars_valid(
    n_cars: int,
    cars: list,
    nth_car: int | str,
):
    if n_cars == 0:
        return True

    if cars[nth_car] > 3000:
        return is_cars_valid(n_cars - 1, cars, nth_car + 1)
    return False
    """,
    greet: """
def greet(name: str, age: int):
    return f"Hello I'm {name}, {age} years of age."
    """,
    add_numbers: """

def add_numbers(a: int, b: int | str):
    return a + b

    """,
    repeat_string: """
def repeat_string(
    s: str | int,
    n: str | int,
):
    return s * n


    """,
    count_occurrences: """
def count_occurrences(
    lst: list | int,
    item: int,
):
    count = 0
    for e in lst:
        if e == item:
            count += 1

    return count

    """,
    get_first_element: """
def get_first_element(lst: str | int):
    return lst[0]
    """,
    get_fibonacci_sequence: """
def get_fibonacci_sequence(n: int | str):
    if n > 10:
        raise ValueError("n is too high")
    if n <= 0:
        return []
    elif n == 1:
        return [1]
    else:
        sequence = [1, 1]
        for i in range(2, n):
            sequence.append(sequence[i - 1] + sequence[i - 2])
        return sequence
    """,
    find_largest_element: """

def find_largest_element(lst: list | bytes):
    max_element = lst[0]
    for element in lst:
        if element > max_element:
            max_element = element
    return max_element
    """,
    calculate_statistics: """
def calculate_statistics(data: list | int | bytes):
    mean = sum(data) / len(data)
    sorted_data = sorted(data)
    median = sorted_data[len(data) // 2]
    mode = max(set(data), key=data.count)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    std_dev = variance**0.5
    return mean, median, mode, std_dev
    """,
    get_filtered_values: """
def get_filtered_values(values: list | tuple):
    filtered_values = []
    for value in values:
        if isinstance(value, int) and value > 10:
            filtered_values.append(value)
        elif isinstance(value, str) and value.startswith("a"):
            filtered_values.append(value)
    return filtered_values
    """,
    add_3: """
def add_3(n: int | bytes):
    return n + 3

    """,
    byte_to_code: """
def byte_to_code(data: bytes | int | str):
    d = data.decode()
    return d
    """,
    byte_logic: """
def byte_logic(data: bytes | int | str):
    d = data.decode()
    d += "potato"
    d = d * 3
    return d
    """,
    byte_sunday: """
def byte_sunday(data: bytes | int | str):
    found = False
    for char in data.decode():
        if char == "s":
            found = True

    return found
    """,
    parse_string: """
def parse_string(text: str, stop: int):
    for i, char in enumerate(text):
        if i == stop:
            break
        if char == "(":
            return text[i : i + 1]
    return text
    """,
    bubble_sort: """
def bubble_sort(arr: list | int | bytes):
    n = len(arr)
    swapped = False
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                swapped = True
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

        if not swapped:
            return
    """,
    is_palindrome: """
def is_palindrome(text: str | set | bytes):
    return text == text[::-1]
    """,
    is_pal_int: """
def is_pal_int(num: int | str):
    temp = num
    reverse = 0
    while temp > 0:
        remainder = temp % 10
        reverse = (reverse * 10) + remainder
        temp = temp // 10

    return temp == num
    """,
    get_filtered_union: """
def get_filtered_union(set_a: set | list | str, set_b: set | int | bytes):
    not_required = {3, 4, 5}

    for e in set(set_a):
        if e in not_required:
            set_a.remove(e)

    for e in set(set_b):
        if e in not_required:
            set_b.remove(e)

    return set_a.union(set_b)
    """,
    get_filtered_intersection: """
def get_filtered_intersection(set_a: set | list | tuple, set_b: set | str | int):
    not_required = {1, 3, 5}

    for e in set(set_a):
        if e in not_required:
            set_a.remove(e)

    for e in set(set_b):
        if e in not_required:
            set_b.remove(e)

    return set_a.intersection(set_b)

    """,
    get_reflexive_pairs: """

def get_reflexive_pairs(set_a: set, set_b: set):
    pairs = {}
    for a, b in zip(set_a, set_b):
        pairs.add((a, b))
    return pairs

    """,
    sum_dict_values: """

def sum_dict_values(d: dict | set):
    return sum(d.values())

    """,
    invert_dict: """
def invert_dict(d: dict | list | int):
    return {v: k for k, v in d.items()}

    """,
    sort_dict_by_values: """
def sort_dict_by_values(d: dict | str | bytes):
    return sorted(d.items(), key=lambda x: x[1])


    """,
}
