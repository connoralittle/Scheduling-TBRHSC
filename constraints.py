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
                    max_cost: int,
                    obj_bool_vars: List[IntVar],
                    obj_bool_coeffs: List[int]):
    # Maximum work 7 consecutive days
    # SOFT Work maximum of 5 days in a row
    # GOAL Avoid working more than 3 days in row (could be 4)
    obj_bool_vars = []
    obj_bool_coeffs = []
    for m in staff:
        variables, coeffs = add_soft_sequence_max(
            model=model,
            prefix="max_days_in_a_row",
            shifts=not_list([staff_works_day[m, d] for d in days]),
            hard_max=hard_max,
            soft_max=soft_max,
            max_cost=max_cost,
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def min_days_off_after_midnight(model: CpModel,
                                staff_works_day: Dict[Tuple, IntVar],
                                staff_works_midnight_shift: Dict[Tuple, IntVar],
                                staff: List[int],
                                days: List[int],
                                hard_min: int,
                                soft_min: int,
                                min_cost: int,
                                obj_bool_vars: List[IntVar],
                                obj_bool_coeffs: List[int]):
    # 2 days off after last midnight (except on call shift).
    # SOFT 3 days off after midnight. 4 even better
    for m in staff:
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="min_days_off_after_midnight",
            shifts=[staff_works_day[m, d] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            prior=Prior([staff_works_midnight_shift[m, d]
                        for d in days], [1], True)
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def midnight_physicians(model: CpModel,
                        staff_works_shift_on_day: Dict[Tuple, IntVar],
                        midnight_staff: List[int],
                        days: List[int],
                        not_midnight_shifts: List[int]):
    # Certain physicians work only Midnight shifts
    for m in midnight_staff:
        constraint = [staff_works_shift_on_day[m, d, s]
                      for d in days
                      for s in not_midnight_shifts]

        model.Add(sum(constraint) == 0)


def no_midnights_within_six_months(model: CpModel,
                                   staff_works_shift_on_day: Dict[Tuple, IntVar],
                                   six_month_new_staff: List[int],
                                   days: List[int],
                                   midnight_shifts: List[int]):
    # Physicians in their first 6 months cant work midnights
    for m in six_month_new_staff:
        constraint = [staff_works_shift_on_day[m, d, s]
                      for d in days
                      for s in midnight_shifts]

        model.Add(sum(constraint) == 0)


def max_midnights_in_a_row(model: CpModel,
                           staff_works_midnight_shift: Dict[Tuple, IntVar],
                           staff: List[int],
                           days: List[int],
                           hard_max: int,
                           soft_max: int,
                           max_cost: int,
                           obj_bool_vars: List[IntVar],
                           obj_bool_coeffs: List[int]):
    # Maximum 2 midnights in a row (except for several physicians who only work midnights)
    # SOFT Max 1 midnight in a row
    for m in staff:
        variables, coeffs = add_soft_sequence_max(
            model=model,
            prefix="max_midnights_in_a_row",
            shifts=not_list([staff_works_midnight_shift[m, d] for d in days]),
            hard_max=hard_max,
            soft_max=soft_max,
            max_cost=max_cost,
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def ft_physicians(model: CpModel,
                  staff_works_shift_on_day: Dict[Tuple, IntVar],
                  ft_staff: List[int],
                  days: List[int],
                  not_ft_shifts: List[int]):
    # Certain physicians work only FT shift (0730,1530 shift)
    for m in ft_staff:
        constraint = [staff_works_shift_on_day[m, d, s]
                      for d in days
                      for s in not_ft_shifts]

        model.Add(sum(constraint) == 0)


def no_late_shift_before_time_off(model: CpModel,
                                  staff_works_day: Dict[Tuple, IntVar],
                                  staff_works_after_5_shift: Dict[Tuple, IntVar],
                                  staff: List[int],
                                  hard_min: int,
                                  soft_min: int,
                                  min_cost: int,
                                  obj_bool_vars: List[IntVar],
                                  obj_bool_coeffs: List[int]):
    # No 2000, 2200, or midnight shift prior to day requested off
    for m in staff:
        days_off_requests = list(
            filter(lambda x: x[0] == m and x[2] == -1, requests))
        days_off = list(
            map(lambda x: staff_works_day[m, x[1]], days_off_requests))
        days_before_days_off = list(map(
            lambda x: staff_works_after_5_shift[m, x[1] - 1] if x[1] > 0 else model.NewConstant(0), days_off_requests))
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="no_late_shift_before_time_off",
            shifts=days_before_days_off + [model.NewConstant(1)] * 1,
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            post=Post([model.NewConstant(1)] * hard_min + days_off, [1])
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)
    return


def on_call_rules_before(model: CpModel,
                         staff_works_on_call_shift: Dict[Tuple, IntVar],
                         staff_works_after_930_shift: Dict[Tuple, IntVar],
                         staff: List[int],
                         days: List[int],
                         hard_min: int,
                         soft_min: int,
                         min_cost: int,
                         obj_bool_vars: List[IntVar],
                         obj_bool_coeffs: List[int]):
    # On call shift - day after rules
    # Physicians can work the 0930 shifts or earlier prior to working on call.
    for m in staff:
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="on_call_rules_before",
            shifts=[staff_works_after_930_shift[m, d] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            post=Post([staff_works_on_call_shift[m, d] for d in days], [1])
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def on_call_rules_after(model: CpModel,
                        staff_works_on_call_shift: Dict[Tuple, IntVar],
                        staff_works_day_shift: Dict[Tuple, IntVar],
                        staff: List[int],
                        days: List[int],
                        hard_min: int,
                        soft_min: int,
                        min_cost: int,
                        obj_bool_vars: List[IntVar],
                        obj_bool_coeffs: List[int]):
    # On call shift - day after rules
    # They can work starting no earlier than 11 the day after on call.
    for m in staff:
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="on_call_rules_after",
            shifts=[staff_works_day_shift[m, d] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            prior=Prior([staff_works_on_call_shift[m, d] for d in days], [1])
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def days_off_after_consecutive_shifts(model: CpModel,
                                      staff_works_day: Dict[Tuple, IntVar],
                                      staff: List[int],
                                      days: List[int],
                                      hard_min: int,
                                      soft_min: int,
                                      min_cost: int,
                                      obj_bool_vars: List[IntVar],
                                      obj_bool_coeffs: List[int]):
    # 2 days off after 3 to 7 days of work in a row
    for m in staff:
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="days_off_after_consecutive_shifts",
            shifts=[staff_works_day[m, d] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            prior=Prior([staff_works_day[m, d] for d in days], [True, True, True]))
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def transitions_constraints(model: CpModel,
                staff_works_shift_on_day: Dict[Tuple, IntVar],
                staff: List[int],
                days: List[int],
                obj_bool_vars: List[IntVar],
                obj_bool_coeffs: List[int]):
    # General principle avoid shift times changing too much day to day
    # Shifts should have same start time to 2.5 hours later compared to previous shift (the 2 hours later can be relaxed to 3,4 perhaps)
    # No shifts that start more than 1.5 hours earlier than the shift on the previous day
    penalized_transitions = []

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
                    trans_var = model.NewBoolVar(
                        'transition (employee=%i, day=%i)' % (m, d))
                    transition.append(trans_var)
                    model.AddBoolOr(transition)
                    obj_bool_vars.append(trans_var)
                    obj_bool_coeffs.append(cost)


def days_off_between_late_and_day_shifts(model: CpModel,
                                         staff_works_day: Dict[Tuple, IntVar],
                                         staff_works_day_shift: Dict[Tuple, IntVar],
                                         staff_works_late_shift: Dict[Tuple, IntVar],
                                         staff: List[int],
                                         days: List[int],
                                         hard_min: int,
                                         soft_min: int,
                                         min_cost: int,
                                         obj_bool_vars: List[IntVar],
                                         obj_bool_coeffs: List[int]):
    # 3 days off when transitioning from late shift to day shift
    for m in staff:
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="days_off_between_late_and_day_shifts",
            shifts=[staff_works_day[(m, d)] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            prior=Prior([staff_works_late_shift[(m, d)]
                        for d in days], [True]),
            post=Post([staff_works_day_shift[(m, d)] for d in days], [True]),
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def days_off_between_late_and_afternoon_shifts(model: CpModel,
                                               staff_works_day: Dict[Tuple, IntVar],
                                               staff_works_afternoon_shift: Dict[Tuple, IntVar],
                                               staff_works_late_shift: Dict[Tuple, IntVar],
                                               staff: List[int],
                                               days: List[int],
                                               hard_min: int,
                                               soft_min: int,
                                               min_cost: int,
                                               obj_bool_vars: List[IntVar],
                                               obj_bool_coeffs: List[int]):
    # 2 days off when transitioning from late shift to afternoon shift (although this transition should be avoided)
    for m in staff:
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="days_off_between_late_and_afternoon_shifts",
            shifts=[staff_works_day[(m, d)] for d in days],
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            prior=Prior([staff_works_late_shift[(m, d)]
                        for d in days], [True]),
            post=Post([staff_works_afternoon_shift[(m, d)]
                      for d in days], [True]),
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def late_shifts_in_a_row(model: CpModel,
                         staff_works_late_shift: Dict[Tuple, IntVar],
                         staff: List[int],
                         days: List[int],
                         hard_max: int,
                         soft_max: int,
                         max_cost: int,
                         obj_bool_vars: List[IntVar],
                         obj_bool_coeffs: List[int]):
    # 3 late shifts in a row maximum - late shifts are 1800, 2000, 2200. The ability to set what a late shift is would be great. Likely better to set them
    # as 2000 and 2200. Midnight shift should also be included.
    for m in staff:
        variables, coeffs = add_soft_sequence_max(
            model=model,
            prefix="late_shifts_in_a_row",
            shifts=not_list([staff_works_late_shift[m, d] for d in days]),
            hard_max=hard_max,
            soft_max=soft_max,
            max_cost=max_cost,
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def late_shifts_in_weeks(model: CpModel,
                         staff_works_late_shift: Dict[Tuple, IntVar],
                         staff: List[int],
                         days: List[int],
                         hard_min: int,
                         soft_min: int,
                         min_cost: int,
                         hard_max: int,
                         soft_max: int,
                         max_cost: int,
                         obj_int_vars: List[IntVar],
                         obj_int_coeffs: List[int]):
    #  5 late shifts in two weeks maximum
    for m in staff:
        for w in range(days[-1] // 7):
            variables, coeffs = add_soft_sum(
                model=model,
                prefix="late_shifts_in_weeks",
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


def avoid_consecutive_ft_shifts(model: CpModel,
                                staff_works_ft_shift: Dict[Tuple, IntVar],
                                staff: List[int],
                                days: List[int],
                                hard_max: int,
                                soft_max: int,
                                max_cost: int,
                                obj_int_vars: List[IntVar],
                                obj_int_coeffs: List[int]):
    # Avoid FT shifts (0730,1530) on consecutive days
    for m in staff:
        variables, coeffs = add_soft_sequence_max(
            model=model,
            prefix="avoid_consecutive_ft_shifts",
            shifts=not_list([staff_works_ft_shift[(m, d)] for d in days]),
            hard_max=hard_max,
            soft_max=soft_max,
            max_cost=max_cost,
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)


def equalize_weekends(model: CpModel,
                      staff_works_day: Dict[Tuple, IntVar],
                      staff: List[int],
                      weekends: List[int],
                      cost: int,
                      target: int,
                      obj_int_vars: List[IntVar],
                      obj_int_coeffs: List[int]):
    # Equalize weekends
    for m in staff:
        variables, coeffs = distribution(
            model=model,
            target_shifts=[staff_works_day[m, d]
                           for d in weekends] + [model.NewConstant(-1)] * (4 - cost),
            prefix="equalize_weekends",
            target=target - (4 - cost)
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)


def minimize_split_weekends(model: CpModel,
                            staff_works_day: Dict[Tuple, IntVar],
                            staff: List[int],
                            saturdays: List[int],
                            sundays: List[int],
                            cost: int,
                            obj_int_vars: List[IntVar],
                            obj_int_coeffs: List[int]):
    # Minimize weekends working only 1 day (‘split weekends’)

    # The optimization constraints
    cost_literals = []
    cost_coefficients = []

    for m in staff:
        sats = [staff_works_day[m, d] for d in saturdays]
        suns = [staff_works_day[m, d] for d in sundays]

        for d in range(len(sats)):
            if d < len(suns):
                # The name of the new variable
                name = ': %d_%d' % (m, d)
                lit = model.NewBoolVar(name)
                model.AddBoolAnd([sats[d], suns[d]]).OnlyEnforceIf(
                    [sats[d], lit.Not()])
                cost_literals.append(lit)
                cost_coefficients.append(cost)

    obj_int_vars.extend(cost_literals)
    obj_int_coeffs.extend(cost_coefficients)


def equalize_night_shifts(model: CpModel,
                          staff_works_midnight_shift: Dict[Tuple, IntVar],
                          staff: List[int],
                          days: List[int],
                          cost: int,
                          target: int,
                          obj_int_vars: List[IntVar],
                          obj_int_coeffs: List[int]):
    # Equalize night shifts
    for m in staff:
        variables, coeffs = distribution(
            model=model,
            target_shifts=[staff_works_midnight_shift[m, d]
                           for d in days] + [model.NewConstant(-1)] * (4 - cost),
            prefix="equalize_nights",
            target=target - (4 - cost)
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)


def no_nightshifts_before_weekend_off(model: CpModel,
                                      staff_works_day: Dict[Tuple, IntVar],
                                      staff_works_after_5_shift: Dict[Tuple, IntVar],
                                      staff: List[int],
                                      fridays: List[int],
                                      saturdays: List[int],
                                      hard_min: int,
                                      soft_min: int,
                                      min_cost: int,
                                      obj_bool_vars: List[IntVar],
                                      obj_bool_coeffs: List[int]):
    # Avoid scheduling people shifts that end after 5 pm Friday on weekends they have off
    for m in staff:
        variables, coeffs = add_soft_sequence_min(
            model=model,
            prefix="days_off_after_midnight_shift",
            shifts=[staff_works_after_5_shift[(m, d)]
                    for d in fridays] + [model.NewConstant(1)] * 1,
            hard_min=hard_min,
            soft_min=soft_min,
            min_cost=min_cost,
            post=Post([model.NewConstant(1)] * hard_min +
                      [staff_works_day[(m, d)] for d in saturdays], [1])
        )
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)


def equalize_late_shifts(model: CpModel,
                         staff_works_late_shift: Dict[Tuple, IntVar],
                         staff: List[int],
                         days: List[int],
                         cost: int,
                         target: int,
                         obj_int_vars: List[IntVar],
                         obj_int_coeffs: List[int]):
    # Equalize late shifts (currently our 2000, 2200 shifts)
    # Equalize 2200 shifts
    # Equalize 2000 shifts
    for m in staff:
        variables, coeffs = distribution(
            model=model,
            target_shifts=[staff_works_late_shift[m, d]
                           for d in days] + [model.NewConstant(-1)] * (4 - cost),
            prefix="equalize_lates",
            target=target - (4 - cost)
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)


def equalize_day_shifts(model: CpModel,
                        staff_works_day_shift: Dict[Tuple, IntVar],
                        staff: List[int],
                        days: List[int],
                        cost: int,
                        target: int,
                        obj_int_vars: List[IntVar],
                        obj_int_coeffs: List[int]):
    # Equalize day shifts (0700 - 1200 start time)
    for m in staff:
        variables, coeffs = distribution(
            model=model,
            target_shifts=[staff_works_day_shift[m, d]
                           for d in days] + [model.NewConstant(-1)] * (4 - cost),
            prefix="equalize_fays",
            target=target - (4 - cost)
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)


def equalize_afternoon_shifts(model: CpModel,
                              staff_works_afternoon_shift: Dict[Tuple, IntVar],
                              staff: List[int],
                              days: List[int],
                              cost: int,
                              target: int,
                              obj_int_vars: List[IntVar],
                              obj_int_coeffs: List[int]):
    # Equalize afternoon shifts (1300 - 1800 start time)
    for m in staff:
        variables, coeffs = distribution(
            model=model,
            target_shifts=[staff_works_afternoon_shift[m, d]
                           for d in days] + [model.NewConstant(-1)] * (4 - cost),
            prefix="equalize_afternoons",
            target=target - (4 - cost)
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)


def equalize_weekdays(model: CpModel,
                      staff_works_day: Dict[Tuple, IntVar],
                      staff: List[int],
                      weekdays: List[int],
                      cost: int,
                      target: int,
                      obj_int_vars: List[IntVar],
                      obj_int_coeffs: List[int]):
    # Equalize weekdays (same number of shifts on M,T,W,Th,F)
    for m in staff:
        variables, coeffs = distribution(
            model=model,
            target_shifts=[staff_works_day[m, d]
                           for d in weekdays] + [model.NewConstant(-1)] * (4 - cost),
            prefix="equalize_weekdays",
            target=target - (4 - cost)
        )
        obj_int_vars.extend(variables)
        obj_int_coeffs.extend(coeffs)


def apply_requests(staff_works_shift_on_day: Dict[Tuple, IntVar],
                   staff_works_day: Dict[Tuple, IntVar],
                   obj_int_vars: List[IntVar],
                   obj_int_coeffs: List[int],
                   requests: Tuple):
    # The optimization constraints
    cost_literals = []
    cost_coefficients = []
    for staff2, day2, shift2, coef in requests:
        if shift2 == -1:
            cost_literals += [staff_works_day[staff2, day2]]
            cost_coefficients += [coef]
        else:
            cost_literals += [staff_works_shift_on_day[staff2, day2, shift2]]
            cost_coefficients += [coef]
    obj_int_vars.extend(cost_literals)
    obj_int_coeffs.extend(cost_coefficients)


def apply_productivity(model: CpModel,
                           staff_productivities: Dict[Tuple, IntVar],
                           staff: List[int],
                           days: List[int],
                           shifts: List[int],
                           span: int,
                           obj_int_vars: List[IntVar],
                           obj_int_coeffs: List[int]):
    # With productivities 1-n I can use the expected die rolls of span n-sided dice to determine how often each productivity will be violated
    for d in days:
        for wind in window(shifts[:-1], span):
            variables, coeffs = add_soft_sum(
                model=model,
                prefix="max_late_shifts_in_two_weeks",
                shifts=[staff_productivities[m, d, s] for m in staff for s in wind],
                hard_min=0,
                soft_min=6,
                min_cost=LOW,
                hard_max=span * 5,
                soft_max=15,
                max_cost=LOW,
            )
            obj_int_vars.extend(variables)
            obj_int_coeffs.extend(coeffs)
