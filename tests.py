from unittest.main import main
from model import *
from data import * 
from constraints import *
from scheduling_funtions import *
import unittest
import __main__

days_worked_results = {}
midnights_worked_results = {}
lates_worked_results = {}
day_shifts_worked_results = {}
shift_results = {}
ft_worked_results = {}
for m in staff:
    days_worked_results[m] = [solver.Value(days_assigned[(m, d)]) for d in days]
    midnights_worked_results[m] = [solver.Value(midnight_shifts_assigned[(m, d)]) for d in days]
    lates_worked_results[m] = [solver.Value(late_shifts_assigned[(m, d)]) for d in days]
    day_shifts_worked_results[m] = [solver.Value(day_shifts_assigned[(m, d)]) for d in days]
    ft_worked_results[m] = [solver.Value(ft_shifts_assigned[(m, d)]) for d in days]
    for d in days:
        shift_results[(m, d)] = [solver.Value(works[(m, d, s)]) for s in shifts]

class TestHard(unittest.TestCase):

    def all_shifts_taken(self):
        # No two doctors in the same shift on the same day
        # All shifts should be taken by doctors
        for d in days:
            num_staff_per_shift = zip(*[shift_results[(m, d)] for m in staff])
            self.assertEqual(list(sum(column) for column in num_staff_per_shift),
            [1] * len(shifts),
            """# No two doctors in the same shift on the same day
            # All shifts should be taken by doctors""")

    def no_two_shifts_in_the_same_day(self):
        #No two shifts same day
        for key, result in shift_results.items():
            self.assertLessEqual(sum(result), 
            1, 
            """#No two shifts same day""")

    def max_days_worked(self):
        # Maximum work 7 consecutive days
        for key, result in days_worked_results.items():
            self.assertFalse(detect_pattern(result, "11111111"),
            """# Maximum work 7 consecutive days""")

    def days_off_after_midnight(self):
        # 2 days off after last midnight (except on call shift)
        for key in midnights_worked_results.keys() and days_worked_results.keys():
            if not midnight_only[key]:
                for idx in days[:-3]:
                    if midnights_worked_results[key][idx] == 1 and midnights_worked_results[key][idx+1] == 0:
                        self.assertEqual(sum(days_worked_results[key][idx+1:idx+3]),
                        0,
                        """# 2 days off after last midnight (except on call shift)""")

    def midnight_physicians(self):
        # Certain staff work midnights only
        for key, result in shift_results.items():
            if (midnight_only[key[0]]):
                self.assertTrue(result == [0,0,0,0,0,0,0,0,0,0,1] or result == [0] * len(shifts),
                """# Certain staff work midnights only""")

    def no_midnights_within_six_months(self):
        # No midnights for staff in their first 6 months (need way to indicate when physician is in first 6 months of practice)
        for key, result in midnights_worked_results.items():
            if (first_six_month_only[key]):
                self.assertEqual(sum(result), 
                0, 
                """# No midnights for staff in their first 6 months (need way to indicate when physician is in first 6 months of practice)""")

    def max_midnights_in_a_row(self):
        # Maximum 2 midnights in a row (except for several physicians who only work midnights)
        for key, result in midnights_worked_results.items():
            if not midnight_only[key]:
                self.assertFalse(detect_pattern(result, "111"),
                """# Maximum 2 midnights in a row (except for several physicians who only work midnights)""")

    # On call shift - day after rules

    def ft_physicians(self):
        # Certain physicians work only FT shift (0730,1530 shift)
        for key, result in shift_results.items():
            if (staff_list[key[0]] == 1):
                self.assertTrue(result == [0,1,0,0,0,0,0,0,0,0,0] or result == [0,0,0,0,0,1,0,0,0,0,0] or result == [0] * len(shifts),
                """# Certain physicians work only FT shift (0730,1530 shift)""")

    # No 2000, 2200, or midnight shift prior to day requested off

    # Physicians can work the 0930 shifts or earlier prior to working on call. They can work starting no earlier than 11 the day after on call.

    def days_off_after_consecutive_shifts(self): 
        # 2 days off after 3 to 7 days of work in a row
        for key, result in days_worked_results.items():
            self.assertFalse(detect_pattern(result, "11101"),
            """# 2 days off after 3 to 7 days of work in a row""")