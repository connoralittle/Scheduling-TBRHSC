from data import *
from model import *
from scheduling_funtions import *
from itertools import permutations
import math


def triangle_costs(num_shifts, num_days, num_staff):
    return math.ceil(float(num_shifts * num_days) / num_staff)


def highest_priority(num_shifts, num_days, num_staff):
    return int(triangle(triangle_costs(num_shifts, num_days, num_staff) + 3) * 4)


def high_priority(num_shifts, num_days, num_staff):
    return int(triangle(triangle_costs(num_shifts, num_days, num_staff) + 2) * 4)


def medium_priority(num_shifts, num_days, num_staff):
    return int(triangle(triangle_costs(num_shifts, num_days, num_staff) + 1) * 4)


def low_priority(num_shifts, num_days, num_staff):
    return int(triangle(triangle_costs(num_shifts, num_days, num_staff)) * 4)


def triangle(n):
    return (n * (n + 1)) / 2


def all_shifts_taken():
    # All shifts should be taken by doctors
    # No two doctors in the same shift on the same day
    for d in days:
        for s in shifts:
            constraint = [works[(m, d, s)]
                          for m in staff]
            model.Add(sum(constraint) == 1)


def max_days_worked(staff, hard_max, soft_max, max_cost):
    # Maximum work 7 consecutive days
    # SOFT Work maximum of 5 days in a row
    for m in staff:
        variables, coeffs = add_soft_sequence_max_constraint(
            model=model,
            prefix="max_days_in_a_row",
            shifts=not_list([days_assigned[m, d] for d in days]),
            hard_max=hard_max,
            soft_max=soft_max,
            max_cost=max_cost,
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def min_days_off_after_midnight(staff, hard_min, soft_min, min_cost):
    # 2 days off after last midnight (except on call shift).
    # SOFT 3 days off after midnight. 4 even better
    for m in staff:
        variables, coeffs = add_soft_sequence_min_constraint(
            model=model,
            prefix="days_off_after_midnight_shift",
            shifts=[days_assigned[(m, d)] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            prior=Prior([midnight_shifts_assigned[(m, d)]
                        for d in days], [1], True)
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def midnight_physicians():
    # Certain physicians work only Midnight shifts
    for m in midnight_staff:
        constraint = [works[(m, d, s)]
                      for d in days
                      for s in not_shifts(midnight_shifts)]

        model.Add(sum(constraint) == 0)


def no_midnights_within_six_months():
    # Physicians in their first 6 months cant work midnights
    for m in six_month_new_staff:
        constraint = [works[(m, d, s)]
                      for d in days
                      for s in midnight_shifts]

        model.Add(sum(constraint) == 0)


def max_midnights_in_a_row(staff, hard_max, soft_max, max_cost):
    # Maximum 2 midnights in a row (except for several physicians who only work midnights)
    # SOFT Max 1 midnight in a row
    for m in staff:
        variables, coeffs = add_soft_sequence_max_constraint(
            model=model,
            prefix="max_midnight_shifts_in_a_row",
            shifts=not_list([midnight_shifts_assigned[m, d] for d in days]),
            hard_max=hard_max,
            soft_max=soft_max,
            max_cost=max_cost,
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def on_call_shift_day_after():
    # On call shift - day after rules
    return


def ft_physicians():
    # Certain physicians work only FT shift (0730,1530 shift)
    for m in ft_staff:
        constraint = [works[(m, d, s)]
                      for d in days
                      for s in not_shifts(ft_shifts)]

        model.Add(sum(constraint) == 0)


def no_late_shift_before_time_off():
    # No 2000, 2200, or midnight shift prior to day requested off
    return


def no_early_shifts_before_on_call():
    # Physicians can work the 0930 shifts or earlier prior to working on call. They can work starting no earlier than 11 the day after on call.
    return


def days_off_after_consecutive_shifts(staff, hard_min, soft_min, min_cost):
    # 2 days off after 3 to 7 days of work in a row
    for m in staff:
        variables, coeffs = add_soft_sequence_min_constraint(
            model=model,
            prefix="days_off_after_consecutive_shifts",
            shifts=[days_assigned[m, d] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            prior=Prior([days_assigned[m, d] for d in days], [True, True, True]))
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def transitions_constraints(LOW, MID, HIGH, MAX):
    # General principle avoid shift times changing too much day to day
    # Shifts should have same start time to 2.5 hours later compared to previous shift (the 2 hours later can be relaxed to 3,4 perhaps)
    # No shifts that start more than 1.5 hours earlier than the shift on the previous day
    penalized_transitions = []

    for shift in list(permutations(shift_list, 2)):
        t1 = float(shift[0][0:2] + '.' + shift[0][2:4])
        t2 = float(shift[1][0:2] + '.' + shift[1][2:4])
        if t2 - t1 > 2.5:
            penalized_transitions.append(
                ((shift_list.index(shift[0]), shift_list.index(shift[1])), MAX))
        elif t2 - t1 < -1.5:
            penalized_transitions.append(
                ((shift_list.index(shift[0]), shift_list.index(shift[1])), MID))

    for (previous_shift, next_shift), cost in penalized_transitions:
        for m in staff:
            for d in days[:-1]:
                transition = [
                    works[m, d, previous_shift].Not(), works[m, d + 1,
                                                             next_shift].Not()
                ]
                if cost != 0:
                    trans_var = model.NewBoolVar(
                        'transition (employee=%i, day=%i)' % (m, d))
                    transition.append(trans_var)
                    model.AddBoolOr(transition)
                    obj_bool_vars.append(trans_var)
                    obj_bool_coeffs.append(cost)


def days_off_between_late_and_day_shifts(staff, hard_min, soft_min, min_cost):
    # 3 days off when transitioning from late shift to day shift
    for m in staff:
        add_soft_sequence_min_constraint(
            model=model,
            prefix="days_off_between_late_and_day",
            shifts=[days_assigned[(m, d)] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            prior=Prior([late_shifts_assigned[(m, d)] for d in days], [True]),
            post=Post([day_shifts_assigned[(m, d)] for d in days], [True]),
        )


def days_off_between_late_and_afternoon_shifts(staff, hard_min, soft_min, min_cost):
    # 2 days off when transitioning from late shift to afternoon shift (although this transition should be avoided)
    for m in staff:
        add_soft_sequence_min_constraint(
            model=model,
            prefix="days_off_between_late_and_day",
            shifts=[days_assigned[(m, d)] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            prior=Prior([late_shifts_assigned[(m, d)] for d in days], [True]),
            post=Post([afternoon_shifts_assigned[(m, d)]
                      for d in days], [True]),
        )


def late_shifts_in_a_row(staff, hard_max, soft_max, max_cost):
    # 3 late shifts in a row maximum - late shifts are 1800, 2000, 2200. The ability to set what a late shift is would be great. Likely better to set them
    # as 2000 and 2200. Midnight shift should also be included.
    for m in staff:
        variables, coeffs = add_soft_sequence_max_constraint(
            model=model,
            prefix="max_late_shifts_in_a_row",
            shifts=not_list([late_shifts_assigned[m, d] for d in days]),
            hard_max=hard_max,
            soft_max=soft_max,
            max_cost=max_cost,
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def late_shifts_in_weeks(staff, hard_min, soft_min, min_cost, hard_max, soft_max, max_cost):
    #  5 late shifts in two weeks maximum
    for m in staff:
        for w in range(days[-1] // 7):
            variables, coeffs = add_soft_sum_constraint(
                model=model,
                prefix="max_late_shifts_in_two_weeks",
                shifts=[late_shifts_assigned[m, d + w * 7] for d in range(7)],
                hard_min=hard_min,
                soft_min=soft_min,
                min_cost=min_cost,
                hard_max=hard_max,
                soft_max=soft_max,
                max_cost=max_cost,
            )
            obj_int_vars.extend(variables)
            obj_int_coeffs.extend(coeffs)


def avoid_consecutive_ft_shifts(staff, hard_max, soft_max, max_cost):
    # Avoid FT shifts (0730,1530) on consecutive days
    for m in staff:
        variables, coeffs = add_soft_sequence_max_constraint(
            model=model,
            prefix="avoid_consecutive_shifts",
            shifts=not_list([ft_shifts_assigned[(m, d)] for d in days]),
            hard_max=hard_max,
            soft_max=soft_max,
            max_cost=max_cost,
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)


base_cost = (4 * triangle_costs(len(shifts), len(weekdays), len(staff)))


def equalize_weekends(staff, target, cost):
    # Equalize weekends
    for m in staff:
        variables, coeffs = distribution_constraint(
            model=model,
            target_shifts=[days_assigned[m, d] for d in weekends],
            prefix="equalize_weekends",
            target=target,
            cost=cost
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)


def equalize_weekdays(staff, target, cost):
    # Equalize weekdays (same number of shifts on M,T,W,Th,F)
    for m in staff:
        variables, coeffs = distribution_constraint(
            model=model,
            target_shifts=[days_assigned[m, d] for d in weekdays],
            prefix="equalize_weekdays",
            target=target,
            cost=cost
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)


