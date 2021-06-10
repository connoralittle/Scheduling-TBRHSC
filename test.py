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
    add_soft_sequence_max_test(
        "Max days worked consecutively", staff_works_day_results, hard_max, soft_max, obj)


def min_days_off_after_midnight_test(staff_doesnt_work_day_results, staff_works_midnight_shift_results, hard_min, soft_min, obj):
    add_soft_sequence_min_test("Min days off after midnight shift",
                               staff_doesnt_work_day_results, hard_min, soft_min, obj, Prior(staff_works_midnight_shift_results, [1], True))


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
    add_soft_sequence_max_test("Max midnights worked consecutively",
                               staff_works_midnight_shift_results, hard_max, soft_max, obj)


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


def on_call_rules_before_test(staff_doesnt_work_after_930_shift_results, staff_works_on_call_shift_results, hard_min, soft_min, obj):
    # On call shift - day after rules
    # Physicians can work the 0930 shifts or earlier prior to working on call.
    add_soft_sequence_min_test("No shifts after 930 before on call",
                               staff_doesnt_work_after_930_shift_results, hard_min, soft_min, obj, post=Post(staff_works_on_call_shift_results, [1]))


def on_call_rules_after_test(staff_doesnt_work_day_shift_results, staff_works_on_call_shift_results, hard_min, soft_min, obj):
    # On call shift - day after rules
    # They can work starting no earlier than 11 the day after on call.
    add_soft_sequence_min_test("No early morning shifts post on call",
                               staff_doesnt_work_day_shift_results, hard_min, soft_min, obj, Prior(staff_works_on_call_shift_results, [1]))


def days_off_after_consecutive_shifts_test(staff_doesnt_work_day_results, staff_works_day_results, hard_min, soft_min, obj):
    # 2 days off after 3 to 7 days of work in a row
    add_soft_sequence_min_test("days_off_after_consecutive_shifts",
                               staff_doesnt_work_day_results, hard_min, soft_min, obj, Prior(staff_works_day_results, [1, 1, 1], True))


def transition_constraint_test(staff_works_shift_on_day_results, days):
    # General principle avoid shift times changing too much day to day
    # Shifts should have same start time to 2.5 hours later compared to previous shift (the 2 hours later can be relaxed to 3,4 perhaps)
    # No shifts that start more than 1.5 hours earlier than the shift on the previous day
    penalized_transitions = []

    for shift in list(permutations(shift_list[:-1], 2)):
        t1 = float(shift[0][0:2] + '.' + shift[0][2:4])
        t2 = float(shift[1][0:2] + '.' + shift[1][2:4])
        if t2 - t1 > 2.5:
            penalized_transitions.append(
                ((shift_list.index(shift[0]), shift_list.index(shift[1])), 1))
        elif t2 - t1 < -1.5:
            penalized_transitions.append(
                ((shift_list.index(shift[0]), shift_list.index(shift[1])), 3))

    transitions = {elem[0]: elem[1] for elem in penalized_transitions}
    jumps_forward_25 = 0
    jumps_backwards_15 = 0
    previous_shift = -1
    for key, result in staff_works_shift_on_day_results.items():
        if previous_shift == -1:
            try:
                previous_shift = result.index(1)
            except:
                previous_shift = -1
        else:
            try:
                ans = transitions[(previous_shift, result.index(1))]
                if ans == 1:
                    jumps_forward_25 += 1
                elif ans == 3:
                    jumps_backwards_15 += 1
                previous_shift = result.index(1)
            except:
                previous_shift = -1

        if key[1] == len(days) - 1:
            previous_shift = -1

    print(
        f"Number of times shifts jump forwards 2.5 hours: {jumps_forward_25}")
    print(
        f"Number of times shifts jump backwards 1.5 hours: {jumps_forward_25}")
    print()


def days_off_between_late_and_day_shifts_test(staff_doesnt_work_day_results, staff_works_late_shift_results, staff_works_day_shift_results, hard_min, soft_min, obj):
    add_soft_sequence_min_test("days_off_between_late_and_day_shifts",
                               staff_doesnt_work_day_results, hard_min, soft_min, obj, Prior(staff_works_late_shift_results, [1]), Post(staff_works_day_shift_results, [1]))


def days_off_between_late_and_afternoon_shifts_test(staff_doesnt_work_day_results, staff_works_late_shift_results, staff_works_afternoon_shift_results, hard_min, soft_min, obj):
    add_soft_sequence_min_test("days_off_between_late_and_afternoon_shifts",
                               staff_doesnt_work_day_results, hard_min, soft_min, obj, Prior(staff_works_late_shift_results, [1]), Post(staff_works_afternoon_shift_results, [1]))

def late_shifts_in_a_row_test(staff_doesnt_work_late_shift_results, hard_min, soft_min, obj):
    add_soft_sequence_max_test("days_off_between_late_and_afternoon_shifts",
                               staff_doesnt_work_late_shift_results, hard_min, soft_min, obj)

def avoid_consecutive_ft_shifts_test(staff_works_ft_shift_results, hard_min, soft_min, obj):
    add_soft_sequence_max_test("days_off_between_late_and_afternoon_shifts",
                               staff_works_ft_shift_results, hard_min, soft_min, obj)

def equalize_weekends_test(staff_works_weekend, target_cost, obj):
    distribution_test("Weekend Equalization", staff_works_weekend, target_cost, obj)

def equalize_night_shifts_test(staff_works_midnight_shift, target_cost, obj):
    distribution_test("night shift Equalization", staff_works_midnight_shift, target_cost, obj)

def equalize_late_shifts_test(staff_works_late_shift, target_cost, obj):
    distribution_test("night shift Equalization", staff_works_late_shift, target_cost, obj)

def equalize_day_shifts_test(staff_works_day_shift, target_cost, obj):
    distribution_test("night shift Equalization", staff_works_day_shift, target_cost, obj)

def equalize_afternoon_shifts_test(staff_works_afternoon_shift, target_cost, obj):
    distribution_test("night shift Equalization", staff_works_afternoon_shift, target_cost, obj)

def equalize_weekdays_test(staff_works_weekdays, target_cost, obj):
    distribution_test("Weekend Equalization", staff_works_weekdays, target_cost, obj)

def minimize_split_weekends_test(solver, staff_works_day, staff, sats, suns):
    split_weekends = 0
    for m in staff:
        sat = [solver.Value(staff_works_day[m, d]) for d in sats]
        sun = [solver.Value(staff_works_day[m, d]) for d in suns]
        for d in sats:
            if d < len(suns) and sat[d] and sun[d]:
                split_weekends += 1

    print(f"Number of split weekends: {split_weekends}")

def no_nightshifts_before_weekend_off_test(staff_doesnt_work_after_5_shift, staff_works_day, hard_min, soft_min, obj):
    add_soft_sequence_min_test("no_nightshifts_before_weekend_off",
                               staff_doesnt_work_after_5_shift, hard_min, soft_min, obj, post=Post(staff_works_day, [1]))
