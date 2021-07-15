from calendar import monthrange
from utility_functions import *
from typing import List

NONE = 0
LOW = low_priority()
MID = medium_priority()
HIGH = high_priority()
MAX = highest_priority()
DEBUG = debug_priority()

# Read from a database
staff_list = ['Olivia', 'Emma', 'Ava', 'Charlotte', 'Sophia', 'Amelia', 'Isabella',
              'Mia', 'Evelyn', 'Harper', 'Camila', 'Gianna', 'Abigail', 'Luna', 'Ella',
              'Elizabeth', 'Sofia', 'Emily', 'Avery', 'Mila', 'Aria', 'Scarlett', 'Penelope',
              'Layla', 'Chloe', 'Victoria', 'Madison', 'Eleanor', 'Grace', 'Nora']

ft_only_staff_mask = [0] * len(staff_list)
midnight_staff_mask = [0] * len(staff_list)
staff_in_first_6_months_mask = [0] * len(staff_list)
# ft_only_staff = [0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# midnight_staff = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0]
# staff_in_first_6_months = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]
staff_productivity_mask = [5, 5, 6, 3, 4, 4, 5, 1, 6, 1, 3,
                           4, 4, 5, 1, 4, 4, 3, 6, 4, 1, 1, 3, 2, 5, 5, 3, 3, 1, 3]

# All shifts are 8 hours
shift_list = ['0700 - 1500',
              '0730 - 1530 (FT)',
              '0930 - 1730',
              '1200 - 2000',
              '1400 - 2200',
              '1530 - 2330 (FT)',
              '1600 - 2400',
              '1800 - 0200',
              '2000 - 0400',
              '2200 - 0400',
              '2359 - 0700',
              'On Call']

midnight_shifts_mask = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
late_shifts_mask = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0]
day_shifts_mask = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
afternoon_shifts_mask = [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0]
ft_shifts_mask = [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
on_call_shifts_mask = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]


def create_data(data: List) -> List[int]:
    return list(range(len(data)))


def filter_data(data: List[int], mask: List[int]) -> List[int]:
    return list(filter(lambda x: mask[data.index(x)] == 1, data))


def create_date_range(first_month: int, last_month: int, year: int) -> List[int]:
    days = sum([monthrange(year, month)[1]
               for month in range(first_month, last_month + 1)])
    first_day = monthrange(year, first_month)[0]
    return list(range(days)), first_day


def days_of_the_week(days: List[int], offset: int):
    return list(filter(lambda x: ((x - offset) % 7) == 0, days))


def mondays(days: List[int], first_day: int) -> List[int]:
    return days_of_the_week(days, (0 - first_day) % 7)


def tuesdays(days: List[int], first_day: int) -> List[int]:
    return days_of_the_week(days, (1 - first_day) % 7)


def wednesdays(days: List[int], first_day: int) -> List[int]:
    return days_of_the_week(days, (2 - first_day) % 7)


def thursdays(days: List[int], first_day: int) -> List[int]:
    return days_of_the_week(days, (3 - first_day) % 7)


def fridays(days: List[int], first_day: int) -> List[int]:
    return days_of_the_week(days, (4 - first_day) % 7)


def saturdays(days: List[int], first_day: int) -> List[int]:
    return days_of_the_week(days, (5 - first_day) % 7)


def sundays(days: List[int], first_day: int) -> List[int]:
    return days_of_the_week(days, (6 - first_day) % 7)
