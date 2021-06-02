from typing import Dict, List
from constraints import *


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


def max_days_worked_test(staff_works_day_results: Dict[Tuple, IntVar]):
    # Maximum work 7 consecutive days
    for key, result in staff_works_day_results.items():
        assert(not detect_pattern(result, "11111111"))


def min_days_off_after_midnight_test(staff_works_midnight_shift_results: Dict[Tuple, IntVar],
                                     staff_works_day_results: Dict[Tuple, IntVar],
                                     days: List[int]):
    # # 2 days off after last midnight (except on call shift).
    for staff in staff_works_midnight_shift_results.keys():
        if not midnight_staff_mask[staff]:
            for day in days[:-3]:
                if staff_works_midnight_shift_results[staff][day] and not staff_works_midnight_shift_results[staff][day+1]:
                    assert(
                        sum(staff_works_day_results[staff][day+1:day+3]) == 0)


def midnight_physicians_test(staff_works_shift_on_day_results: Dict[Tuple, IntVar],
                             shifts: List[int]):
    # Certain staff work midnights only
    for staff, results in staff_works_shift_on_day_results.items():
        if midnight_staff_mask[staff[0]]:
            assert(results == [
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1] or results == [0] * len(shifts))


def no_midnights_within_six_months_test(staff_works_midnight_shift_results: Dict[Tuple, IntVar]):
    # No midnights for staff in their first 6 months (need way to indicate when physician is in first 6 months of practice)
    for staff, results in staff_works_midnight_shift_results.items():
        if (staff_in_first_6_months_mask[staff]):
            assert(sum(results == 0))


def max_midnights_in_a_row_test(staff_works_midnight_shift_results: Dict[Tuple, IntVar]):
    # Maximum 2 midnights in a row (except for several physicians who only work midnights)
    for staff, result in staff_works_midnight_shift_results.items():
        if not midnight_staff_mask[staff]:
            assert(not detect_pattern(result, "111"))


def ft_physicians_test(staff_works_shift_on_day_results: Dict[Tuple, IntVar],
                       shifts: List[int]):
    for key, result in staff_works_shift_on_day_results.items():
        if ft_only_staff_mask[key[0]]:
            assert(result == [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0] or result == [
                0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0] or result == [0] * len(shifts))


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

