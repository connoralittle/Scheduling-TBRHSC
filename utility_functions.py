import itertools
import re
import math
from typing import List

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