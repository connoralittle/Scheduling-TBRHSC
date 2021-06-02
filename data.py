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

requests = [
    # staff, day, shift, weight
    # if shift is -1 make it all shifts
    # if day is -1 then make it all days

    # Emma wants the first 6 days off after working one day
    (1, 1, -1, DEBUG),
    (1, 2, -1, DEBUG),
    (1, 3, -1, DEBUG),
    (1, 4, -1, DEBUG),
    (1, 5, -1, DEBUG),
    (1, 6, -1, DEBUG),

    (1, 30, -1, DEBUG),
    (3, 3, -1, DEBUG),
    (11, 6, -1, DEBUG),
    (4, 20, -1, DEBUG),
    (2, 3, -1, DEBUG),
    (8, 16, -1, DEBUG),
    (6, 14, -1, DEBUG),

    (6, 3, -1, DEBUG),
    (14, 6, -1, DEBUG),
    (15, 20, -1, DEBUG),
    (12, 3, -1, DEBUG),
    (18, 16, -1, DEBUG),
    (19, 14, -1, DEBUG),

    (4, 3, -1, DEBUG),
    (3, 6, -1, DEBUG),
    (7, 4, -1, DEBUG),
    (7, 6, -1, DEBUG),
    (7, 8, -1, DEBUG),
    (9, 14, -1, DEBUG),

    (4, 29, 4, DEBUG),
    (3, 23, 1, DEBUG),
    (7, 25, 2, DEBUG),
    (7, 28, 9, DEBUG),
    (7, 20, 6, DEBUG),
    (9, 3, 6, DEBUG),

    (0, 0, 1, DEBUG),
    (17, 0, 1, DEBUG),

]


def create_data(data: List) -> List[int]:
    return list(range(len(data)))


def filter_data(data: List[int], mask: List[int]) -> List[int]:
    return list(filter(lambda x: mask[x] == 1, data))


def create_date_range(first_month: int, last_month: int, year: int) -> List[int]:
    days = sum([monthrange(year, month)[1]
               for month in range(first_month, last_month + 1)])
    first_day = monthrange(year, first_month)[0]
    return list(range(days)), first_day


def days_of_the_week(days: List[int], first_day: int, offset: int):
    return days[(offset - first_day) % 7::7]


def mondays(days: List[int], first_day: int) -> List[int]:
    return days_of_the_week(days, first_day, 0)


def tuesdays(days: List[int], first_day: int) -> List[int]:
    return days_of_the_week(days, first_day, 1)


def wednesdays(days: List[int], first_day: int) -> List[int]:
    return days_of_the_week(days, first_day, 2)


def thursdays(days: List[int], first_day: int) -> List[int]:
    return days_of_the_week(days, first_day, 3)


def fridays(days: List[int], first_day: int) -> List[int]:
    return days_of_the_week(days, first_day, 4)


def saturdays(days: List[int], first_day: int) -> List[int]:
    return days_of_the_week(days, first_day, 5)


def sundays(days: List[int], first_day: int) -> List[int]:
    return days_of_the_week(days, first_day, 6)
