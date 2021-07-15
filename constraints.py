from data import *
from model import *
from scheduling_funtions import *
from itertools import permutations
from typing import List, Dict


def all_shifts_taken(model: CpModel,
                     staff_works_shift_on_day: Dict[Tuple, IntVar],
                     staff: List[int],
                     days: List[int],
                     shifts: List[int]):
    # All shifts should be taken by doctors
    # No two doctors in the same shift on the same day
    for d in days:
        for s in shifts:
            constraint = [staff_works_shift_on_day[m, d, s]
                          for m in staff]
            model.Add(sum(constraint) == 1)


def max_days_worked(model: CpModel,
                    staff_works_day: Dict[Tuple, IntVar],
                    staff: List[int],
                    days: List[int],
                    hard_max: int,
                    soft_max: int,
                    max_cost: int):
    # Maximum work 7 consecutive days
    # SOFT Work maximum of 5 days in a row
    # GOAL Avoid working more than 3 days in row (could be 4)
    obj_bool_vars = []
    obj_bool_coeffs = []
    for m in staff:
        variables, coeffs = add_soft_sequence_max(
            model=model,
            prefix="max_days_in_a_row_" + m,
            shifts=not_list([staff_works_day[m, d] for d in days]),
            hard_max=hard_max,
            soft_max=soft_max,
            max_cost=max_cost,
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)
    return obj_bool_vars, obj_bool_coeffs


def min_days_off_after_midnight(model: CpModel,
                                staff_doesnt_work_day: Dict[Tuple, IntVar],
                                staff_works_midnight_shift: Dict[Tuple, IntVar],
                                staff: List[int],
                                days: List[int],
                                hard_min: int,
                                soft_min: int,
                                min_cost: int):
    # 2 days off after last midnight (except on call shift).
    # SOFT 3 days off after midnight. 4 even better
    obj_bool_vars = []
    obj_bool_coeffs = []
    for m in staff:
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="min_days_off_after_midnight_" + m,
            shifts=[staff_doesnt_work_day[m, d] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            prior=Prior([staff_works_midnight_shift[m, d]
                        for d in days], [1], True)
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)
    return obj_bool_vars, obj_bool_coeffs


def midnight_physicians(model: CpModel,
                        staff_works_shift_on_day: Dict[Tuple, IntVar],
                        midnight_staff: List[int],
                        days: List[int],
                        not_midnight_shifts: List[int]):
    # Certain physicians work only Midnight shifts
    x_shifts_only(model, staff_works_shift_on_day,
                  midnight_staff, days, not_midnight_shifts)


def no_midnights_within_six_months(model: CpModel,
                                   staff_works_shift_on_day: Dict[Tuple, IntVar],
                                   six_month_new_staff: List[int],
                                   days: List[int],
                                   midnight_shifts: List[int]):
    # Physicians in their first 6 months cant work midnights
    x_shifts_only(model, staff_works_shift_on_day,
                  six_month_new_staff, days, midnight_shifts)


def max_midnights_in_a_row(model: CpModel,
                           staff_works_midnight_shift: Dict[Tuple, IntVar],
                           staff: List[int],
                           days: List[int],
                           hard_max: int,
                           soft_max: int,
                           max_cost: int):
    # Maximum 2 midnights in a row (except for several physicians who only work midnights)
    # SOFT Max 1 midnight in a row
    obj_bool_vars = []
    obj_bool_coeffs = []
    for m in staff:
        variables, coeffs = add_soft_sequence_max(
            model=model,
            prefix="max_midnights_in_a_row_" + m,
            shifts=not_list([staff_works_midnight_shift[m, d] for d in days]),
            hard_max=hard_max,
            soft_max=soft_max,
            max_cost=max_cost,
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)
    return obj_bool_vars, obj_bool_coeffs


def ft_physicians(model: CpModel,
                  staff_works_shift_on_day: Dict[Tuple, IntVar],
                  ft_staff: List[int],
                  days: List[int],
                  not_ft_shifts: List[int]):
    # Certain physicians work only FT shift (0730,1530 shift)
    x_shifts_only(model, staff_works_shift_on_day,
                  ft_staff, days, not_ft_shifts)


def no_late_shift_before_time_off(model: CpModel,
                                  staff_works_day: Dict[Tuple, IntVar],
                                  staff_doesnt_work_after_5_shift: Dict[Tuple, IntVar],
                                  staff: List[int],
                                  requests,
                                  hard_min: int,
                                  soft_min: int,
                                  min_cost: int):
    # No 2000, 2200, or midnight shift prior to day requested off
    obj_bool_vars = []
    obj_bool_coeffs = []
    for m in staff:
        days_off_requests = list(
            filter(lambda x: x[0] == m and x[2] == -1, requests))
        days_off = list(
            map(lambda x: staff_works_day[m, x[1]], days_off_requests))
        days_before_days_off = list(map(
            lambda x: staff_doesnt_work_after_5_shift[m, x[1] - 1] if x[1] > 0 else model.NewConstant(0), days_off_requests))
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="no_late_shift_before_time_off_" + m,
            shifts=days_before_days_off + [model.NewConstant(1)] * 1,
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            post=Post([model.NewConstant(1)] * hard_min + days_off, [1])
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)
    return obj_bool_vars, obj_bool_coeffs


def on_call_rules_before(model: CpModel,
                         staff_works_on_call_shift: Dict[Tuple, IntVar],
                         staff_doesnt_work_after_930_shift: Dict[Tuple, IntVar],
                         staff: List[int],
                         days: List[int],
                         hard_min: int,
                         soft_min: int,
                         min_cost: int):
    # On call shift - day after rules
    # Physicians can work the 0930 shifts or earlier prior to working on call.
    obj_bool_vars = []
    obj_bool_coeffs = []
    for m in staff:
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="on_call_rules_before_" + m,
            shifts=[staff_doesnt_work_after_930_shift[m, d] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            post=Post([staff_works_on_call_shift[m, d] for d in days], [1])
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)
    return obj_bool_vars, obj_bool_coeffs


def on_call_rules_after(model: CpModel,
                        staff_works_on_call_shift: Dict[Tuple, IntVar],
                        staff_doesnt_work_day_shift: Dict[Tuple, IntVar],
                        staff: List[int],
                        days: List[int],
                        hard_min: int,
                        soft_min: int,
                        min_cost: int):
    # On call shift - day after rules
    # They can work starting no earlier than 11 the day after on call.
    obj_bool_vars = []
    obj_bool_coeffs = []
    for m in staff:
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="on_call_rules_after_" + m,
            shifts=[staff_doesnt_work_day_shift[m, d] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            prior=Prior([staff_works_on_call_shift[m, d] for d in days], [1])
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)
    return obj_bool_vars, obj_bool_coeffs


def days_off_after_consecutive_shifts(model: CpModel,
                                      staff_works_day: Dict[Tuple, IntVar],
                                      staff_doesnt_work_day: Dict[Tuple, IntVar],
                                      staff: List[int],
                                      days: List[int],
                                      hard_min: int,
                                      soft_min: int,
                                      min_cost: int):
    # 2 days off after 3 to 7 days of work in a row
    obj_bool_vars = []
    obj_bool_coeffs = []
    for m in staff:
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="days_off_after_consecutive_shifts_" + m,
            shifts=[staff_doesnt_work_day[m, d] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            prior=Prior([staff_works_day[m, d] for d in days], [1, 1, 1], True))
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)
    return obj_bool_vars, obj_bool_coeffs


def transitions_constraints(model: CpModel,
                            staff_works_shift_on_day: Dict[Tuple, IntVar],
                            staff: List[int],
                            days: List[int]):
    # General principle avoid shift times changing too much day to day
    # Shifts should have same start time to 2.5 hours later compared to previous shift (the 2 hours later can be relaxed to 3,4 perhaps)
    # No shifts that start more than 1.5 hours earlier than the shift on the previous day
    penalized_transitions = []
    obj_bool_vars = []
    obj_bool_coeffs = []

    for shift in list(permutations(shift_list[:-1], 2)):
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
                    staff_works_shift_on_day[m, d, previous_shift].Not(), staff_works_shift_on_day[m, d + 1,
                                                                                                   next_shift].Not()
                ]
                if cost != 0:
                    name = 'transition (employee=%s, day=%i)' % (m, d)
                    lit = model.NewBoolVar(name)

                    model.AddBoolOr(transition + [lit])
                    obj_bool_vars.append(lit)
                    obj_bool_coeffs.append(cost)
    return obj_bool_vars, obj_bool_coeffs


def days_off_between_late_and_day_shifts(model: CpModel,
                                         staff_doesnt_work_day: Dict[Tuple, IntVar],
                                         staff_works_day_shift: Dict[Tuple, IntVar],
                                         staff_works_late_shift: Dict[Tuple, IntVar],
                                         staff: List[int],
                                         days: List[int],
                                         hard_min: int,
                                         soft_min: int,
                                         min_cost: int):
    # 3 days off when transitioning from late shift to day shift
    obj_bool_vars = []
    obj_bool_coeffs = []
    for m in staff:
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="days_off_between_late_and_day_shifts_" + m,
            shifts=[staff_doesnt_work_day[(m, d)] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            prior=Prior([staff_works_late_shift[m, d]
                        for d in days], [1]),
            post=Post([staff_works_day_shift[m, d] for d in days], [1]),
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)
    return obj_bool_vars, obj_bool_coeffs


def days_off_between_late_and_afternoon_shifts(model: CpModel,
                                               staff_doesnt_work_day: Dict[Tuple, IntVar],
                                               staff_works_afternoon_shift: Dict[Tuple, IntVar],
                                               staff_works_late_shift: Dict[Tuple, IntVar],
                                               staff: List[int],
                                               days: List[int],
                                               hard_min: int,
                                               soft_min: int,
                                               min_cost: int):
    # 2 days off when transitioning from late shift to afternoon shift (although this transition should be avoided)
    obj_bool_vars = []
    obj_bool_coeffs = []
    for m in staff:
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="days_off_between_late_and_afternoon_shifts_" + m,
            shifts=[staff_doesnt_work_day[(m, d)] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            prior=Prior([staff_works_late_shift[m, d]
                        for d in days], [1]),
            post=Post([staff_works_afternoon_shift[m, d]
                      for d in days], [1]),
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)
    return obj_bool_vars, obj_bool_coeffs


def late_shifts_in_a_row(model: CpModel,
                         staff_works_late_shift: Dict[Tuple, IntVar],
                         staff: List[int],
                         days: List[int],
                         hard_max: int,
                         soft_max: int,
                         max_cost: int):
    # 3 late shifts in a row maximum - late shifts are 1800, 2000, 2200. The ability to set what a late shift is would be great. Likely better to set them
    # as 2000 and 2200. Midnight shift should also be included.
    obj_bool_vars = []
    obj_bool_coeffs = []
    for m in staff:
        variables, coeffs = add_soft_sequence_max(
            model=model,
            prefix="late_shifts_in_a_row_" + m,
            shifts=not_list([staff_works_late_shift[m, d] for d in days]),
            hard_max=hard_max,
            soft_max=soft_max,
            max_cost=max_cost,
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)
    return obj_bool_vars, obj_bool_coeffs


def late_shifts_in_weeks(model: CpModel,
                         staff_works_late_shift: Dict[Tuple, IntVar],
                         staff: List[int],
                         days: List[int],
                         hard_min: int,
                         soft_min: int,
                         min_cost: int,
                         hard_max: int,
                         soft_max: int,
                         max_cost: int):
    #  5 late shifts in two weeks maximum
    obj_int_vars = []
    obj_int_coeffs = []
    for m in staff:
        for w in range(days[-1] // 7):
            variables, coeffs = add_soft_sum(
                model=model,
                prefix="late_shifts_in_weeks_" + m,
                shifts=[staff_works_late_shift[m, d + w * 7]
                        for d in range(7)],
                hard_min=hard_min,
                soft_min=soft_min,
                min_cost=min_cost,
                hard_max=hard_max,
                soft_max=soft_max,
                max_cost=max_cost,
            )
            obj_int_vars.extend(variables)
            obj_int_coeffs.extend(coeffs)
    return obj_int_vars, obj_int_coeffs


def avoid_consecutive_ft_shifts(model: CpModel,
                                staff_works_ft_shift: Dict[Tuple, IntVar],
                                staff: List[int],
                                days: List[int],
                                hard_max: int,
                                soft_max: int,
                                max_cost: int):
    # Avoid FT shifts (0730,1530) on consecutive days
    obj_int_vars = []
    obj_int_coeffs = []
    for m in staff:
        variables, coeffs = add_soft_sequence_max(
            model=model,
            prefix="avoid_consecutive_ft_shifts_" + m,
            shifts=not_list([staff_works_ft_shift[(m, d)] for d in days]),
            hard_max=hard_max,
            soft_max=soft_max,
            max_cost=max_cost,
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)
    return obj_int_vars, obj_int_coeffs


def equalize_weekends(model: CpModel,
                      staff_works_day: Dict[Tuple, IntVar],
                      staff: List[int],
                      weekends: List[int],
                      cost: int,
                      target: int):
    # Equalize weekends
    obj_int_vars = []
    obj_int_coeffs = []
    for m in staff:
        variables, coeffs = distribution(
            model=model,
            target_shifts=[staff_works_day[m, d]
                           for d in weekends] + [model.NewConstant(-1)] * (4 - cost),
            prefix="equalize_weekends_" + m,
            target=target - (4 - cost)
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)
    return obj_int_vars, obj_int_coeffs


def minimize_split_weekends(model: CpModel,
                            staff_works_day: Dict[Tuple, IntVar],
                            staff: List[int],
                            sats: List[int],
                            suns: List[int],
                            cost: int):
    # Minimize weekends working only 1 day (‘split weekends’)
    obj_int_vars = []
    obj_int_coeffs = []
    for m in staff:
        sat = [staff_works_day[m, d] for d in sats]
        sun = [staff_works_day[m, d] for d in suns]

        for d in range(len(sat)):
            if d < len(sun):
                # The name of the new variable
                name = ': minimize_split_weekends_%s_%d' % (m, d)
                lit = model.NewBoolVar(name)
                model.AddBoolAnd([sat[d], sun[d]]).OnlyEnforceIf(
                    [sat[d], lit.Not()])
                model.AddBoolAnd([sun[d], sat[d]]).OnlyEnforceIf(
                    [sun[d], lit.Not()])
                obj_int_vars.append(lit)
                obj_int_coeffs.append(cost)

    return obj_int_vars, obj_int_coeffs


def equalize_night_shifts(model: CpModel,
                          staff_works_midnight_shift: Dict[Tuple, IntVar],
                          staff: List[int],
                          days: List[int],
                          cost: int,
                          target: int):
    # Equalize night shifts
    obj_int_vars = []
    obj_int_coeffs = []
    for m in staff:
        variables, coeffs = distribution(
            model=model,
            target_shifts=[staff_works_midnight_shift[m, d]
                           for d in days] + [model.NewConstant(-1)] * (4 - cost),
            prefix="equalize_nights_" + m,
            target=target - (4 - cost)
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)
    return obj_int_vars, obj_int_coeffs


def no_nightshifts_before_weekend_off(model: CpModel,
                                      staff_works_day: Dict[Tuple, IntVar],
                                      staff_doesnt_work_after_5_shift: Dict[Tuple, IntVar],
                                      staff: List[int],
                                      fridays: List[int],
                                      saturdays: List[int],
                                      hard_min: int,
                                      soft_min: int,
                                      min_cost: int):
    # Avoid scheduling people shifts that end after 5 pm Friday on weekends they have off
    obj_bool_vars = []
    obj_bool_coeffs = []
    for m in staff:
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="no_nightshifts_before_weekend_off_" + m,
            shifts=[staff_doesnt_work_after_5_shift[m, d]
                    for d in fridays] + [model.NewConstant(1)] * 1,
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            post=Post([model.NewConstant(1)] * hard_min +
                      [staff_works_day[m, d] for d in saturdays], [1])
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)
    return obj_bool_vars, obj_bool_coeffs


def equalize_late_shifts(model: CpModel,
                         staff_works_late_shift: Dict[Tuple, IntVar],
                         staff: List[int],
                         days: List[int],
                         cost: int,
                         target: int):
    # Equalize late shifts (currently our 2000, 2200 shifts)
    # Equalize 2200 shifts
    # Equalize 2000 shifts
    obj_int_vars = []
    obj_int_coeffs = []
    for m in staff:
        variables, coeffs = distribution(
            model=model,
            target_shifts=[staff_works_late_shift[m, d]
                           for d in days] + [model.NewConstant(-1)] * (4 - cost),
            prefix="equalize_lates_" + m,
            target=target - (4 - cost)
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)
    return obj_int_vars, obj_int_coeffs


def equalize_day_shifts(model: CpModel,
                        staff_works_day_shift: Dict[Tuple, IntVar],
                        staff: List[int],
                        days: List[int],
                        cost: int,
                        target: int):
    # Equalize day shifts (0700 - 1200 start time)
    obj_int_vars = []
    obj_int_coeffs = []
    for m in staff:
        variables, coeffs = distribution(
            model=model,
            target_shifts=[staff_works_day_shift[m, d]
                           for d in days] + [model.NewConstant(-1)] * (4 - cost),
            prefix="equalize_days_" + m,
            target=target - (4 - cost)
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)
    return obj_int_vars, obj_int_coeffs


def equalize_afternoon_shifts(model: CpModel,
                              staff_works_afternoon_shift: Dict[Tuple, IntVar],
                              staff: List[int],
                              days: List[int],
                              cost: int,
                              target: int):
    # Equalize afternoon shifts (1300 - 1800 start time)
    obj_int_vars = []
    obj_int_coeffs = []
    for m in staff:
        variables, coeffs = distribution(
            model=model,
            target_shifts=[staff_works_afternoon_shift[m, d]
                           for d in days] + [model.NewConstant(-1)] * (4 - cost),
            prefix="equalize_afternoons_" + m,
            target=target - (4 - cost)
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)
    return obj_int_vars, obj_int_coeffs


def equalize_weekdays(model: CpModel,
                      staff_works_day: Dict[Tuple, IntVar],
                      staff: List[int],
                      weekdays: List[int],
                      cost: int,
                      target: int):
    # Equalize weekdays (same number of shifts on M,T,W,Th,F)
    obj_int_vars = []
    obj_int_coeffs = []
    for m in staff:
        variables, coeffs = distribution(
            model=model,
            target_shifts=[staff_works_day[m, d]
                           for d in weekdays] + [model.NewConstant(-1)] * (4 - cost),
            prefix="equalize_weekdays_" + m,
            target=target - (4 - cost)
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)
    return obj_int_vars, obj_int_coeffs


def apply_requests(staff_works_shift_on_day: Dict[Tuple, IntVar],
                   staff_works_day: Dict[Tuple, IntVar],
                   days: List[int],
                   requests: Tuple):
    obj_int_vars = []
    obj_int_coeffs = []
    for staff2, day2, shift2, coef in requests:
        if shift2 == -1:
            obj_int_vars += [staff_works_day[staff2, day2]]
            obj_int_coeffs += [coef]
        else:
            obj_int_vars += [staff_works_shift_on_day[staff2, day2, shift2]]
            obj_int_coeffs += [coef]
    return obj_int_vars, obj_int_coeffs


def apply_productivity(model: CpModel,
                       staff_productivities: Dict[Tuple, IntVar],
                       staff: List[int],
                       days: List[int],
                       shifts: List[int],
                       span: int):
    # With productivities 1-n I can use the expected die rolls of span n-sided dice to determine how often each productivity will be violated
    # The paper just describes "super cool" physicians
    # This could be balancing mean time to completion, average cost, etc
    obj_int_vars = []
    obj_int_coeffs = []
    for d in days:
        for wind in window(shifts[:-1], span):
            variables, coeffs = add_soft_sum(
                model=model,
                prefix="productivity",
                shifts=[staff_productivities[m, d, s]
                        for m in staff for s in wind],
                hard_min=0,
                soft_min=6,
                min_cost=LOW,
                hard_max=span * 5,
                soft_max=15,
                max_cost=LOW,
            )
            obj_int_vars.extend(variables)
            obj_int_coeffs.extend(coeffs)
    return obj_int_vars, obj_int_coeffs
