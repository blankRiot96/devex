"""
THIS FILE CONTAINS A BUNCH OF GIBBERISH FUNCTIONS USED
IN THE GAME TO FOOL THE PLAYER
"""


def fibonacci(n: int | float):
    if n in {0, 1}:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def is_cars_valid(n_cars: int, cars: list[int | str], nth_car: int | str):
    if n_cars == 0:
        return True

    if cars[nth_car] > 3000:
        return is_cars_valid(n_cars - 1, cars, nth_car + 1)
    return False


def greet(name: str, age: int):
    return f"Hello I'm {name}, {age} years of age."

o = is_cars_valid(3, [3001, 3000, 3003], 0)
print(o)
