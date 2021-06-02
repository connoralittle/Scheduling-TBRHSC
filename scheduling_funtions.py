from dataclasses import dataclass
from typing import List
from utility_functions import *


# https://github.com/google/or-tools/blob/master/examples/python/shift_scheduling_sat.py


def bounded_span(shifts, start, length, left_bound):
    sequence = []
    # Left border (start of works, or works[start - 1])
    if start > 0 and left_bound:
        sequence.append(shifts[start - 1].Not())

    for i in range(length):
        sequence.append(shifts[start + i])

    # Right border (end of works or works[start + length])
    if start + length < len(shifts):
        sequence.append(shifts[start + length].Not())
    return sequence


def predicates(start, prior):
    return [prior.shifts[i + start].Not()
            if prior.choices[i] == False
            else prior.shifts[i + start]
            for i in range(len(prior.choices))]


@dataclass
class Prior:
    shifts: List
    choices: List[bool]
    continue_shifts: bool = False


@dataclass
class Post:
    shifts: List
    choices: List[bool]


def forbid_min(model, shifts, hard_min, prior=None, post=None):
    # Creates a sliding window accross the planning period
    # ==============================================
    # |    |    |    |    |    |    |    |    |    |
    # ==============================================
    #   P    H    H    H    H     P    P
    # If there are 31 days in the planning period our window should span
    # The time it takes the rightmost element to reach the end
    # Which in this case is 31 - 1 - 4 - 2 + 1 = 26 iterations

    # There are 4 main cases and the function should work as expected in all 4
    if post is not None and prior is not None:
        window_size = len(shifts) - len(prior.choices) - \
            hard_min - len(post.choices) + 1
        for start in range(window_size):

            # Get the prior predicates
            pred = predicates(start, prior)

            # Get the post predicates
            post_window_start = start + len(prior.choices) + hard_min
            post_window_end = start + \
                len(prior.choices) + hard_min + len(post.choices)

            # Combine them
            pred = pred + post.shifts[post_window_start:post_window_end]

            # Get the elements between them
            # The list is notted because we want to ensure that they are false
            span = not_list(
                shifts[start + len(prior.choices): start + len(prior.choices) + hard_min])

            # If both predicates are satisfied then prohibit the sequence between them
            model.AddBoolAnd(span).OnlyEnforceIf(pred)

    # Sometimes we want the prior to be able to continue and extend the pattern
    # You can take as many days off as you want but once you start working you must work n shifts
    elif post is None and prior is not None and prior.continue_shifts:
        # This time we want to grow the window from size 1 to size n - 1
        for length in range(hard_min):
            window_size = len(shifts) - length - len(prior.choices)
            for start in range(window_size):

                # Get the prior predicates
                pred = predicates(start, prior)

                # Get the elements after pred
                sequence_window_start = start + len(prior.choices)
                sequence_window_end = start + len(prior.choices) + length + 1
                span = shifts[sequence_window_start:sequence_window_end]

                # Xor doesn't support reified variables so we have to do it manually
                xor_bool = model.NewBoolVar("")

                # If xor is disabled prevent the span from having working
                model.Add(sum(span) == 0).OnlyEnforceIf(
                    pred + [xor_bool.Not()])
                model.Add(prior.shifts[start + 1] == 1).OnlyEnforceIf(
                    pred + [xor_bool])

    elif post is None and prior is not None:
        window_size = len(shifts) - len(prior.choices) - hard_min + 1
        for start in range(window_size):

            # Get the prior predicates
            pred = predicates(start, prior)

            # Get the elements after pred
            sequence_window_start = start + len(prior.choices)
            sequence_window_end = start + len(prior.choices) + hard_min
            # The list is notted because we want to ensure that they are false
            span = not_list(shifts[sequence_window_start:sequence_window_end])

            # If the predicate is true then enforce the next N shifts must be off
            model.AddBoolAnd(span).OnlyEnforceIf(pred)

    elif post is not None and prior is None:
        window_size = len(shifts) - hard_min - len(post.choices) + 1
        for start in range(window_size):

            # Get the post predicates
            post_window_start = start + hard_min
            post_window_end = start + hard_min + len(post.choices)

            # Combine them
            posts = post.shifts[post_window_start:post_window_end]

            # Get the elements after pred
            sequence_window_start = start
            sequence_window_end = start + hard_min
            # The list is notted because we want to ensure that they are false
            span = not_list(shifts[sequence_window_start:sequence_window_end])

            model.AddBoolAnd(span).OnlyEnforceIf(posts)

    # If there is no pattern to match just ban all runs of n
    else:
        # This time we want to grow the window from size 1 to size n - 1
        for length in range(1, hard_min):
            window_size = len(shifts) - length + 1
            for start in range(window_size):

                # Get a bounded span of the window to the right
                span = bounded_span(shifts, start, length, True)

                # Prohibit runs of n
                model.AddBoolOr(span)


def forbid_max(model, shifts, hard_max, prior=None, post=None):
    # Creates a sliding window accross the planning period
    # ==============================================
    # |    |    |    |    |    |    |    |    |    |
    # ==============================================
    #   P    H    H    H    H     P    P
    # If there are 31 days in the planning period our window should span
    # The time it takes the rightmost element to reach the end
    # Which in this case is 31 - 1 - 4 - 2 + 1 = 26 iterations

    # There are 4 main cases and the function should work as expected in all 4
    # if post is not None and prior is not None:
    #     window_size = len(shifts) - len(prior.choices) - \
    #     hard_min - len(post.choices) + 1
    #     for start in range(window_size):

    #         # Get the prior predicates
    #         pred = predicates2(start, prior)

    #         # Get the post predicates
    #         post_window_start = start + len(prior.choices) + hard_min
    #         post_window_end = start + \
    #             len(prior.choices) + hard_min + len(post.choices)

    #         # Combine them
    #         pred = pred + post.shifts[post_window_start:post_window_end]

    #         # Get the elements between them
    #         # The list is notted because we want to ensure that they are false
    #         span = not_list(
    #             shifts[start + len(prior.choices): start + len(prior.choices) + hard_min])

    #         # If both predicates are satisfied then prohibit the sequence between them
    #         model.AddBoolAnd(span).OnlyEnforceIf(pred)

    # Sometimes we want the prior to be able to continue and extend the pattern
    # You can take as many days off as you want but once you start working you must work n shifts
    if post is None and prior is not None and prior.continue_shifts:
        # This time we want to grow the window from size 1 to size n - 1
        for length in range(hard_max):
            window_size = len(shifts) - length - len(prior.choices)
            for start in range(window_size):

                # Get the prior predicates
                pred = predicates(start, prior)

                # Get the elements after pred
                sequence_window_start = start + len(prior.choices)
                sequence_window_end = start + len(prior.choices) + length + 1
                span = shifts[sequence_window_start:sequence_window_end]

                # Xor doesn't support reified variables so we have to do it manually
                xor_bool = model.NewBoolVar("")

                # If xor is disabled prevent the span from having working
                model.Add(sum(span) == 0).OnlyEnforceIf(
                    pred + [xor_bool.Not()])
                model.Add(prior.shifts[start + 1] == 1).OnlyEnforceIf(
                    pred + [xor_bool])

    elif post is None and prior is not None:
        window_size = len(shifts) - hard_max - len(prior.choices) + 1
        for start in range(window_size):

            # Get the prior predicates
            pred = predicates(start, prior)

            # Get the elements after pred
            sequence_window_start = start + len(prior.choices)
            sequence_window_end = start + len(prior.choices) + hard_max + 1
            span = shifts[sequence_window_start:sequence_window_end]

            # If the predicate is true then enforce the next N shifts must be off
            model.AddBoolAnd(span).OnlyEnforceIf(pred)

    # If there is no pattern to match just ban all runs of n
    else:
        window_size = len(shifts) - hard_max + 1
        for start in range(window_size):

            # Get the elements after pred
            sequence_window_start = start
            sequence_window_end = start + hard_max + 1
            span = shifts[sequence_window_start:sequence_window_end]

            # Prohibit runs of n
            model.AddBoolOr(span)


def penalize_min(model, prefix, shifts, hard_min, soft_min, min_cost, prior=None, post=None):
    # The optimization constraints
    cost_literals = []
    cost_coefficients = []

  # Penalize sequences that are below the soft limit.
    for length in range(hard_min, soft_min):
        # Creates a sliding window accross the planning period from hard to soft min
        # ==============================================
        # |    |    |    |    |    |    |    |    |    |
        # ==============================================
        #   P    H    H    H    S     P    P
        # If there are 31 days in the planning period our window should span
        # The time it takes the rightmost element to reach the end
        # Which in this case is 31 - 1 - 4 - 2 + 1 = 26 iterations for the soft min
        # And 27 for the hard min

        # Penalizing a soft minimum involves creating a new variable and ORing it
        # With the forbidden sequence

        # There are 4 main cases and the function should work as expected in all 4
        if post is not None and prior is not None:
            window_size = len(shifts) - len(prior.choices) - \
                length - len(post.choices) + 1
            for start in range(window_size):

                # Get the prior predicates
                pred = predicates(start, prior)

                # Get the post predicates
                post_window_start = start + len(prior.choices) + length
                post_window_end = start + \
                    len(prior.choices) + length + len(post.choices)

                # Combine them
                posts = post.shifts[post_window_start:post_window_end]

                # Get the elements after pred
                sequence_window_start = start + len(prior.choices)
                sequence_window_end = start + len(prior.choices) + length
                span = shifts[sequence_window_start:sequence_window_end]

                # If the pattern exists then the middle must all be off
                model.AddBoolAnd(not_list(span)).OnlyEnforceIf(
                    pred + posts)

                # We need to create the expression (A1 and A2 and A3 and ... and An) or lit
                # To do this we need an intermediate variable
                not_sequence = model.NewBoolVar('not_sequence')
                # The pattern only exists if you are willing to pay
                model.AddBoolAnd(posts).OnlyEnforceIf(pred + [not_sequence])

                # The name of the new variable
                name = ': under_span(start=%i, length=%i)' % (start, length)
                lit = model.NewBoolVar(prefix + name)

                # Either all of the shifts are on or the literal is on
                model.AddBoolOr([not_sequence, lit]).OnlyEnforceIf(pred)

                cost_literals.append(lit)
                # The penalty is proportional to the delta with soft_min.
                cost_coefficients.append(min_cost * (soft_min - length))

        # Sometimes we want the prior to be able to continue and extend the pattern
        # You can take as many days off as you want but once you start working you must work n shifts
        elif post is None and prior is not None and prior.continue_shifts:
            window_size = len(shifts) - len(prior.choices) - length
            for start in range(window_size):

                # The name of the new variable
                name = ': under_span(start=%i, length=%i)' % (start, length)
                lit = model.NewBoolVar(prefix + name)

                # Get the prior predicates
                pred = predicates(start, prior)

                # Get the elements after pred
                sequence_window_start = start + len(prior.choices)
                sequence_window_end = start + len(prior.choices) + length + 1
                span = shifts[sequence_window_start:sequence_window_end]

                # Xor doesn't support reified variables so we have to do it manually
                xor_bool = model.NewBoolVar("")
                pattern_break_bool = model.NewBoolVar("")

                # If xor is disabled prevent the span from having working
                model.Add(sum(span) == 0).OnlyEnforceIf(
                    pred + [xor_bool.Not(), pattern_break_bool.Not()])
                model.Add(prior.shifts[start + 1] == 1).OnlyEnforceIf(
                    pred + [xor_bool])

                # Either all of the shifts are on or the literal is on
                model.AddBoolOr([pattern_break_bool, lit]).OnlyEnforceIf(pred)

                cost_literals.append(lit)
                # The penalty is proportional to the delta with soft_min.
                cost_coefficients.append(min_cost * (soft_min - length))

        elif post is None and prior is not None:
            window_size = len(shifts) - len(prior.choices) - length + 1
            for start in range(window_size):
                # Get the prior predicates
                pred = predicates(start, prior)

                # Get the elements after pred
                sequence_window_start = start + len(prior.choices)
                sequence_window_end = start + len(prior.choices) + length
                span = shifts[sequence_window_start:sequence_window_end]

                # We need to create the expression (A1 and A2 and A3 and ... and An) or lit
                # To do this we need an intermediate variable
                not_sequence = model.NewBoolVar('not_sequence')
                # Saying the sum equals 0 is the same as saying they are all 0
                model.Add(sum(span) == 0).OnlyEnforceIf(
                    pred + [not_sequence])

                # The name of the new variable
                name = ': under_span(start=%i, length=%i)' % (start, length)
                lit = model.NewBoolVar(prefix + name)

                # Either all of the shifts are on or the literal is on
                model.AddBoolOr([not_sequence, lit]).OnlyEnforceIf(pred)

                cost_literals.append(lit)
                # The penalty is proportional to the delta with soft_min.
                cost_coefficients.append(min_cost * (soft_min - length))

        elif post is not None and prior is None:
            window_size = len(shifts) - length - len(post.choices) + 1
            for start in range(window_size):

                # Get the post predicates
                post_window_start = start + length
                post_window_end = start + length + len(post.choices)

                # Combine them
                posts = post.shifts[post_window_start:post_window_end]

                span = bounded_span(shifts, start, length, False)

                # The name of the new variable
                name = 'name'
                lit = model.NewBoolVar(name)

                model.AddBoolAnd(posts + span).OnlyEnforceIf(
                    posts + [lit.Not()])

                cost_literals.append(lit)
                # The penalty is proportional to the delta with soft_min.
                cost_coefficients.append(min_cost * (soft_min - length))

        # If there is no pattern to match just ban all runs of n
        else:
            window_size = len(shifts) - length
            for start in range(window_size):

                # Get a bounded span of the window to the right
                span = bounded_span(shifts, start, length, True)

                # The name of the new variable
                name = ': under_span(start=%i, length=%i)' % (start, length)
                lit = model.NewBoolVar(prefix + name)

                # Allow the lit to be chosen
                span.append(lit)

                # Prohibit runs of n
                model.AddBoolOr(span)

                cost_literals.append(lit)
                # The penalty is proportional to the delta with soft_min.
                cost_coefficients.append(min_cost * (soft_min - length))

    # Return the optimization constraints
    return cost_literals, cost_coefficients


def penalize_max(model, prefix, shifts, hard_max, soft_max, max_cost, prior=None, post=None):
    # The optimization constraints
    cost_literals = []
    cost_coefficients = []

  # Penalize sequences that are below the soft limit.
    for length in range(soft_max + 1, hard_max + 1):
        # Creates a sliding window accross the planning period from hard to soft min
        # ==============================================
        # |    |    |    |    |    |    |    |    |    |
        # ==============================================
        #   P    H    H    H    S     P    P
        # If there are 31 days in the planning period our window should span
        # The time it takes the rightmost element to reach the end
        # Which in this case is 31 - 1 - 4 - 2 + 1 = 26 iterations for the soft min
        # And 27 for the hard min

        # Penalizing a soft minimum involves creating a new variable and ORing it
        # With the forbidden sequence

        # Sometimes we want the prior to be able to continue and extend the pattern
        # You can take as many days off as you want but once you start working you must work n shifts
        if post is None and prior is not None and prior.continue_shifts:
            window_size = len(shifts) - len(prior.choices) - length
            for start in range(window_size):

                # The name of the new variable
                name = ': under_span(start=%i, length=%i)' % (start, length)
                lit = model.NewBoolVar(prefix + name)

                # Get the prior predicates
                pred = predicates(start, prior)

                # Get the elements after pred
                sequence_window_start = start + len(prior.choices)
                sequence_window_end = start + len(prior.choices) + length + 1
                span = shifts[sequence_window_start:sequence_window_end]

                # Xor doesn't support reified variables so we have to do it manually
                xor_bool = model.NewBoolVar("")
                pattern_break_bool = model.NewBoolVar("")

                # If xor is disabled prevent the span from having working
                model.Add(sum(span) == 0).OnlyEnforceIf(
                    pred + [xor_bool.Not(), pattern_break_bool.Not()])
                model.Add(prior.shifts[start + 1] == 1).OnlyEnforceIf(
                    pred + [xor_bool])

                # Either all of the shifts are on or the literal is on
                model.AddBoolOr([pattern_break_bool, lit]).OnlyEnforceIf(pred)

                cost_literals.append(lit)
                # The penalty is proportional to the delta with soft_min.
                cost_coefficients.append(max_cost * (soft_max - length))

        elif post is None and prior is not None:
            window_size = len(shifts) - len(prior.choices) - length
            for start in range(window_size):
                # Get the prior predicates
                pred = predicates(start, prior)

                # Get the elements after pred
                sequence_window_start = start + len(prior.choices)
                sequence_window_end = start + len(prior.choices) + length
                span = shifts[sequence_window_start:sequence_window_end]

                # We need to create the expression (A1 and A2 and A3 and ... and An) or lit
                # To do this we need an intermediate variable
                not_sequence = model.NewBoolVar('not_sequence')
                # Saying the sum equals the length is the same as saying they are all 1
                model.Add(sum(span) == len(span)).OnlyEnforceIf(
                    pred + [not_sequence])

                # The name of the new variable
                name = ': under_span(start=%i, length=%i)' % (start, length)
                lit = model.NewBoolVar(prefix + name)

                # Either all of the shifts are on or the literal is on
                model.AddBoolOr([not_sequence, lit]).OnlyEnforceIf(pred)

                cost_literals.append(lit)
                # The penalty is proportional to the delta with soft_min.
                cost_coefficients.append(max_cost * (length - soft_max))

        # If there is no pattern to match just ban all runs of n
        else:
            window_size = len(shifts) - length
            for start in range(window_size):

                # Get a bounded span of the window to the right
                span = bounded_span(shifts, start, length, True)

                # The name of the new variable
                name = ': under_span(start=%i, length=%i)' % (start, length)
                lit = model.NewBoolVar(prefix + name)

                # Allow the lit to be chosen
                span.append(lit)

                # Prohibit runs of n
                model.AddBoolOr(span)

                cost_literals.append(lit)
                # The penalty is proportional to the delta with soft_min.
                cost_coefficients.append(max_cost * (length - soft_max))

    # Return the optimization constraints
    return cost_literals, cost_coefficients


def add_soft_sequence_min(model, prefix, shifts, hard_min, soft_min, min_cost, prior=None, post=None):
    forbid_min(model, shifts, hard_min, prior, post)
    return penalize_min(model, prefix, shifts, hard_min, soft_min, min_cost, prior, post)


def add_soft_sequence_max(model, prefix, shifts, hard_max, soft_max, max_cost, prior=None, post=None):
    forbid_max(model, shifts, hard_max, prior, post)
    return penalize_max(model, prefix, shifts, hard_max, soft_max, max_cost, prior, post)


def add_soft_sequence(model, prefix, shifts, hard_max, soft_max, max_cost, hard_min, soft_min, min_cost, prior=None, post=None):
    forbid_min(model, shifts, hard_min, prior, post)
    forbid_max(model, shifts, hard_max, prior, post)
    var1, coeff1 = penalize_min(
        model, prefix, shifts, hard_min, soft_min, min_cost, prior, post)
    var2, coeff2 = penalize_max(
        model, prefix, shifts, hard_max, soft_max, max_cost, prior, post)
    return (var1 + var2), (coeff1 + coeff2)


def add_soft_sum(model, shifts, hard_min, soft_min, min_cost,
                 soft_max, hard_max, max_cost, prefix):

    cost_variables = []
    cost_coefficients = []
    sum_var = model.NewIntVar(hard_min, hard_max, '')
    # This adds the hard constraints on the sum.
    model.Add(sum_var == sum(shifts))

    # Penalize sums below the soft_min target.
    if soft_min > hard_min and min_cost > 0:
        delta = model.NewIntVar(-len(shifts), len(shifts), '')
        model.Add(delta == soft_min - sum_var)
        # TODO(user): Compare efficiency with only excess >= soft_min - sum_var.
        excess = model.NewIntVar(0, len(shifts), prefix + ': under_sum')
        model.AddMaxEquality(excess, [delta, 0])
        cost_variables.append(excess)
        cost_coefficients.append(min_cost)

    # Penalize sums above the soft_max target.
    if soft_max < hard_max and max_cost > 0:
        delta = model.NewIntVar(-len(shifts), len(shifts), '')
        model.Add(delta == sum_var - soft_max)
        excess = model.NewIntVar(0, len(shifts), prefix + ': over_sum')
        model.AddMaxEquality(excess, [delta, 0])
        cost_variables.append(excess)
        cost_coefficients.append(max_cost)

    return cost_variables, cost_coefficients


def distribution(model, target_shifts, prefix, target):
    # The optimization constraints
    cost_literals = []
    cost_coefficients = []

    prefix = "weekend_dist"
    num_shifts = model.NewIntVar(0, target * 2, '%s' % prefix)
    model.Add(num_shifts == sum(target_shifts))
    diff = model.NewIntVar(-target, target, '%s' % prefix)
    model.Add(num_shifts + diff == target)
    # over = model.NewIntVar(0, target, '%s' % prefix)
    # under = model.NewIntVar(0, target, '%s' % prefix)
    # model.Add(num_shifts + over - under == target)

    abs_diff = model.NewIntVar(0, target, '%s' % prefix)
    model.AddAbsEquality(abs_diff, diff)

    diff_plus_one = model.NewIntVar(1, target + 1, '%s' % prefix)
    model.Add(diff_plus_one == 1 + abs_diff)

    # diff = model.NewIntVar(0, target, '%s' % prefix)
    # model.Add(diff == over + under)

    # diff_plus_one = model.NewIntVar(1, target + 1, '%s' % prefix)
    # model.Add(diff_plus_one == diff + 1)

    # In order to stay as close to the target as possible a non-linear error is needed
    # Or else 0 away from the target and 3 away from the target is equivilant to
    # 2 away and 1 away. I don't want 1 person to get all the weekends off
    # I have chosen the triangle numbers, 4 * n(n+1)/2, 1 + 2 + 3... * 4
    # Using regression this is equivilant to 2x + 2x^2
    diff_not_linear = model.NewIntVar(
        0, target * target + target, 'diff_abs_%s' % prefix)
    model.AddMultiplicationEquality(diff_not_linear, [diff, diff_plus_one])

    cost_literals.append(diff_not_linear)
    # The penalty is proportional to the delta with soft_min.
    cost_coefficients.append(2)

    return cost_literals, cost_coefficients
