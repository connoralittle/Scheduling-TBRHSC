from calendar import monthrange
from scheduling_funtions import *

NONE = 0
LOW = low_priority()
MID = medium_priority()
HIGH = high_priority()
MAX = highest_priority()
DEBUG = debug_priority()

staff_list = ['Olivia', 'Emma', 'Ava', 'Charlotte', 'Sophia', 'Amelia', 'Isabella',
              'Mia', 'Evelyn', 'Harper', 'Camila', 'Gianna', 'Abigail', 'Luna', 'Ella',
              'Elizabeth', 'Sofia', 'Emily', 'Avery', 'Mila', 'Aria', 'Scarlett', 'Penelope',
              'Layla', 'Chloe', 'Victoria', 'Madison', 'Eleanor', 'Grace', 'Nora'][:-5]

ft_only = [0] * len(staff_list)
midnight_only = [0] * len(staff_list)
first_six_month_only = [0] * len(staff_list)
# ft_only = [0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# midnight_only = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0]
# first_six_month_only = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]

staff = list(range(len(staff_list)))
midnight_staff = list(filter(lambda x: midnight_only[x] == 1, staff))
six_month_new_staff = list(
    filter(lambda x: first_six_month_only[x] == 1, staff))
ft_staff = list(filter(lambda x: ft_only[x] == 1, staff))

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

shifts = list(range(len(shift_list)))
midnight_shifts = [10]
late_shifts = list(shifts[7:10])
day_shifts = list(shifts[:3])
afternoon_shifts = list(shifts[3:7])
ft_shifts = [2, 5]
on_call_shifts = [11]

jan = monthrange(2021, 1)
feb = monthrange(2021, 2)
mar = monthrange(2021, 3)
apr = monthrange(2021, 4)
may = monthrange(2021, 5)
jun = monthrange(20201, 6)

first_day = jan[0]
# days = range(jan[1])
days = range(jan[1] + feb[1] + mar[1] + apr[1] + may[1] + jun[1])

mondays = days[(0 - first_day) % 7::7]
tuesdays = days[(1 - first_day) % 7::7]
wednesdays = days[(2 - first_day) % 7::7]
thursdays = days[(3 - first_day) % 7::7]
fridays = days[(4 - first_day) % 7::7]
saturdays = days[(5 - first_day) % 7::7]
sundays = days[(6 - first_day) % 7::7]
weekdays = (list(mondays) + list(tuesdays) +
            list(wednesdays) + list(thursdays) + list(fridays))
weekends = (list(saturdays) + list(sundays))

requests = [
    # staff, day, shift, weight
    # if shift is -1 make it all shifts

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

]


def not_staff(staff_list):
    return staff if staff_list == [] else list(set(staff) - set(staff_list))


def not_shifts(shift_list):
    return shifts if shift_list == [] else list(set(shifts) - set(shift_list))
