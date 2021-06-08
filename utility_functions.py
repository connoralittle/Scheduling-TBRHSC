import itertools
import re
import math
from typing import List, Dict

def window(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(itertools.islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def detect_pattern(list, pattern):
    return False if re.search(pattern, ''.join([str(i) for i in list])) is None else True


def detect_pattern_soft(list, pattern):
    return len(re.findall(pattern, ''.join([str(i) for i in list])))


def not_list(my_list: List):
    return list(map(lambda x: x.Not(), my_list))

def not_dict(my_dict: Dict):
    return {k: v.Not() for k, v in my_dict.items()}

def triangle_costs(num_shifts, num_days, num_staff):
    return math.ceil((num_shifts * num_days) / num_staff)

def debug_priority():
    return int(triangle(8) * 4)

def highest_priority():
    return int(triangle(5) * 4)


def high_priority():
    return int(triangle(4) * 4)


def medium_priority():
    return int(triangle(3) * 4)


def low_priority():
    return int(triangle(2) * 4)


def triangle(n):
    return (n * (n + 1)) / 2


def list_difference(starting_list: List, difference_list: List):
    return difference_list if starting_list == [] else list(set(starting_list) - set(difference_list))

def save_shifts_to_file(name, staff_works_shift_on_day, num_staff, num_days, num_shifts, solver):
    f = open(name, "w")

    f.write(f"{num_staff};")
    f.write(f"{num_days};")
    for m in range(num_staff):
        for d in range(num_days):
            shift_seq = ''.join([str(solver.Value(staff_works_shift_on_day[m,d,s])) for s in range(num_shifts)])
            f.write(f"{shift_seq};")
    f.close()

def read_shifts_from_file(model, name):
    with open(name) as myFile:
        text = myFile.read()
        results = text.split(';')
        prev_staff = range(int(results[0]))
        prev_days = list(range(-int(results[1]), 0))
        results = results[2:]
        prev_works = {}
        for m in prev_staff:
            for d in prev_days:
                for s, value in enumerate(results[0]):
                    prev_works[m,d,s] = model.NewConstant(int(value))
                results = results[1:]
    return prev_days, prev_works

def obj_result(solver, obj):
    return sum(map(lambda y: y[0] *  y[1], zip(map(lambda x: solver.Value(x), obj[0]), obj[1])))