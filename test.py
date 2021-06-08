from typing import Dict, List
from constraints import *
from testing_functions import *


def all_shifts_taken_test(staff_works_shift_on_day_results: Dict[Tuple, IntVar],
                          staff: List[int],
                          days: List[int],
                          shifts: List[int]):
    # No two doctors in the same shift on the same day
    # All shifts should be taken by doctors

    for d in days:
        num_staff_per_shift = zip(
            *[staff_works_shift_on_day_results[m, d] for m in staff])
        assert(list(sum(column)
               for column in num_staff_per_shift) == [1] * len(shifts))


def no_two_shifts_on_same_day_test(staff_works_shift_on_day_results: Dict[Tuple, IntVar]):
    # No two shifts same day
    for key, result in staff_works_shift_on_day_results.items():
        assert(sum(result) <= 1)


def max_days_worked_test(staff_works_day_results: Dict[Tuple, IntVar], hard_max: int, soft_max: int, obj):
    # Maximum work 7 consecutive days
    add_soft_sequence_max_test("Max days worked consecutively", staff_works_day_results, hard_max, soft_max, obj)

def min_days_off_after_midnight_test(staff_works_midnight_shift_results, hard_min, soft_min, obj, prior = None):
    add_soft_sequence_min_test("Min days off after midnight shift", staff_works_midnight_shift_results, hard_min, soft_min, obj, prior)

def midnight_physicians_test(staff_works_shift_on_day_results: Dict[Tuple, IntVar],
                             shifts: List[int]):

    # Certain staff work midnights only
    for key, result in staff_works_shift_on_day_results.items():
        x_shifts_only_test({key[0]: result}, midnight_staff_mask, [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], [0] * len(shifts)])


def no_midnights_within_six_months_test(staff_works_midnight_shift_results: Dict[Tuple, IntVar],
                                        shifts: List[int]):
    # No midnights for staff in their first 6 months (need way to indicate when physician is in first 6 months of practice)
    x_shifts_only_test(staff_works_midnight_shift_results,
                       staff_in_first_6_months_mask, [[0] * len(shifts)])


def max_midnights_in_a_row_test(staff_works_midnight_shift_results: Dict[Tuple, IntVar], hard_max: int, soft_max: int, obj):
    # Maximum 2 midnights in a row (except for several physicians who only work midnights)
    add_soft_sequence_max_test("Max midnights worked consecutively", staff_works_midnight_shift_results, hard_max, soft_max, obj)


def ft_physicians_test(staff_works_shift_on_day_results: Dict[Tuple, IntVar],
                       shifts: List[int]):
    # Certain physicians work only FT shift (0730,1530 shift)
    for key, result in staff_works_shift_on_day_results.items():
        x_shifts_only_test({key[0]: result}, ft_only_staff_mask, [[0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [
                           0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0], [0] * len(shifts)])


def no_late_shift_before_time_off_test(staff_works_day_results: Dict[Tuple, IntVar],
                                       staff_works_after_5_shift_results: Dict[Tuple, IntVar]):
    # No 2000, 2200, or midnight shift prior to day requested off
    for m, d, s, coeff in requests:
        if s == -1 and staff_works_day_results[m][d] and d > 0:
            assert(staff_works_after_5_shift_results[m][d-1] == 0)


def on_call_rules_before_test(staff_works_on_call_shift_results: Dict[Tuple, IntVar],
                              staff_works_after_930_shift_results: Dict[Tuple, IntVar]):
    # On call shift - day after rules
    # Physicians can work the 0930 shifts or earlier prior to working on call.
    for key, results in staff_works_on_call_shift_results.items():
        for idx in results:
            if idx > 0 and results[idx]:
                assert(staff_works_after_930_shift_results[key][idx-1] == 0)


def on_call_rules_after_test(staff_works_on_call_shift_results: Dict[Tuple, IntVar],
                             staff_works_day_shift_results: Dict[Tuple, IntVar],
                             days: List[int]):

    # On call shift - day after rules
    # They can work starting no earlier than 11 the day after on call.
    for key, result in staff_works_on_call_shift_results.items():
        for idx in result:
            if idx < len(days)-1 and result[idx]:
                assert(staff_works_day_shift_results[key][idx+1] == 0)


def days_off_after_consecutive_shifts_test(staff_works_day_results: Dict[Tuple, IntVar]):
    # 2 days off after 3 to 7 days of work in a row
    for key, result in staff_works_day_results.items():
        assert(not detect_pattern(result, "11101"))
