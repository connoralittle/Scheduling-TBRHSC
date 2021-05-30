from calendar import monthrange

staff_list = ['Olivia', 'Emma', 'Ava', 'Charlotte', 'Sophia', 'Amelia', 'Isabella', 
        'Mia', 'Evelyn', 'Harper', 'Camila', 'Gianna','Abigail', 'Luna', 'Ella',
        'Elizabeth', 'Sofia', 'Emily', 'Avery', 'Mila']

ft_only = [0] * len(staff_list)
midnight_only = [0] * len(staff_list)
first_six_month_only = [0] * len(staff_list)
# ft_only = [0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# midnight_only = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0]
# first_six_month_only = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]

staff = range(len(staff_list))
midnight_staff = list(filter(lambda x: midnight_only[x] == 1, staff))
six_month_new_staff = list(filter(lambda x: first_six_month_only[x] == 1, staff))
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
        '2359 - 0700']

shifts = range(len(shift_list))
midnight_shifts = [10]
late_shifts = shifts[7:10]
day_shifts = shifts[:3]
afternoon_shifts = shifts[3:7]
ft_shifts = [2, 5]

jan = monthrange(2021, 1)
feb = monthrange(2021, 2)
mar = monthrange(2021, 3)
apr = monthrange(2021, 4)
may = monthrange(2021, 5)
jun = monthrange(20201, 6)

first_day = jan[0]
days = range(jan[1])

mondays = days[(0 - first_day) % 7::7]
tuesdays = days[(1 - first_day) % 7::7]
wednesdays = days[(2 - first_day) % 7::7]
thursdays = days[(3 - first_day) % 7::7]
fridays = days[(4 - first_day) % 7::7]
saturdays = days[(5 - first_day) % 7::7]
sundays = days[(6 - first_day) % 7::7]
weekdays = (list(mondays) + list(tuesdays) + list(wednesdays) + list(thursdays) + list(fridays))
weekends = (list(saturdays) + list(sundays))


def not_staff(staff_list):
    return staff if staff_list == [] else list(set(staff) - set(staff_list))

def not_shifts(shift_list):
    return shifts if shift_list == [] else list(set(shifts) - set(shift_list))