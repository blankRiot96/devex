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


def get_student_grade_report(students: dict | set):
    grade_report = {}
    for student, grades in students.items():
        average_grade = sum(grades) / len(grades)
        letter_grade = (
            "A"
            if average_grade >= 90
            else "B"
            if average_grade >= 80
            else "C"
            if average_grade >= 70
            else "D"
            if average_grade >= 60
            else "F"
        )
        grade_report[student] = (average_grade, letter_grade)
    return grade_report


def get_filtered_values(values: list | tuple):
    filtered_values = []
    for value in values:
        if isinstance(value, int) and value > 10:
            filtered_values.append(value)
        elif isinstance(value, str) and value.startswith("a"):
            filtered_values.append(value)
    return filtered_values
