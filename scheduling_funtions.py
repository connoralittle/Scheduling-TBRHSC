from dataclasses import dataclass
from typing import List
import itertools
import re
import typing


def window(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(itertools.islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def detect_pattern(list, pattern):
    return False if re.search(pattern, ''.join([str(i) for i in list])) is None else True


def detect_pattern_soft(list, pattern):
    return len(re.findall(pattern, ''.join([str(i) for i in list])))


def not_list(my_list: typing.List):
    return list(map(lambda x: x.Not(), my_list))

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

                # Get a bounded span of the window to the right
                span = bounded_span(shifts, start + len(prior.choices),
                                    length, False)

                # Either you have the shift and the prior or you have neither
                and_window = start + len(prior.choices) + length - 1
                model.AddBoolAnd([prior.shifts[and_window], shifts[and_window]]).OnlyEnforceIf(
                    pred + [shifts[and_window]])

                # Then ban runs of n
                model.AddBoolOr(span).OnlyEnforceIf(pred)

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

                # Get a bounded span of the window to the right
                span = bounded_span(shifts, start + len(prior.choices),
                                    length, False)

                # Either you have the shift and the prior or you have neither
                and_window = start + len(prior.choices) + length - 1
                model.AddBoolAnd([prior.shifts[and_window], shifts[and_window]]).OnlyEnforceIf(
                    pred + [shifts[and_window]])

                # Then ban runs of n
                model.AddBoolOr(span).OnlyEnforceIf(pred)

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
                # Get the prior predicates
                pred = predicates(start, prior)

                # Get a bounded span of the window to the right
                span = bounded_span(shifts, start + len(prior.choices),
                                    length, False)

                # The name of the new variable
                name = ': under_span(start=%i, length=%i)' % (start, length)
                lit = model.NewBoolVar(prefix + name)

                # Allow the lit to be chosen
                span.append(lit)

                # Either you have the shift and the prior or you have neither
                and_window = start + len(prior.choices) + length - 1
                model.AddBoolAnd([prior.shifts[and_window], shifts[and_window]]).OnlyEnforceIf(
                    pred + [shifts[and_window]])

                # Then ban runs of n
                model.AddBoolOr(span).OnlyEnforceIf(pred)

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
                # Get the prior predicates
                pred = predicates(start, prior)

                # Get a bounded span of the window to the right
                span = bounded_span(shifts, start + len(prior.choices),
                                    length, False)

                # The name of the new variable
                name = ': under_span(start=%i, length=%i)' % (start, length)
                lit = model.NewBoolVar(prefix + name)

                # Allow the lit to be chosen
                span.append(lit)

                # Either you have the shift and the prior or you have neither
                and_window = start + len(prior.choices) + length - 1
                model.AddBoolAnd([prior.shifts[and_window], shifts[and_window]]).OnlyEnforceIf(
                    pred + [shifts[and_window]])

                # Then ban runs of n
                model.AddBoolOr(span).OnlyEnforceIf(pred)

                cost_literals.append(lit)
                # The penalty is proportional to the delta with soft_min.
                cost_coefficients.append(max_cost * (length - soft_max))

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


def add_soft_sequence_min_constraint(model, prefix, shifts, hard_min, soft_min, min_cost, prior = None, post = None):
    forbid_min(model, shifts, hard_min, prior, post)
    return penalize_min(model, prefix, shifts, hard_min, soft_min, min_cost, prior, post)
def add_soft_sequence_max_constraint(model, prefix, shifts, hard_max, soft_max, max_cost, prior = None, post = None):
    forbid_max(model, shifts, hard_max, prior, post)
    return penalize_max(model, prefix, shifts, hard_max, soft_max, max_cost, prior, post)
def add_soft_sequence_constraint2(model, prefix, shifts, hard_max, soft_max, max_cost, hard_min, soft_min, min_cost, prior = None, post = None):
    forbid_min(model, shifts, hard_min, prior, post)
    forbid_max(model, shifts, hard_max, prior, post)
    var1, coeff1 = penalize_min(model, prefix, shifts, hard_min, soft_min, min_cost, prior, post)
    var2, coeff2 = penalize_max(model, prefix, shifts, hard_max, soft_max, max_cost, prior, post)
    return (var1 + var2), (coeff1 + coeff2)


def add_soft_sum_constraint(model, shifts, hard_min, soft_min, min_cost,
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
        excess = model.NewIntVar(0, 7, prefix + ': under_sum')
        model.AddMaxEquality(excess, [delta, 0])
        cost_variables.append(excess)
        cost_coefficients.append(min_cost)

    # Penalize sums above the soft_max target.
    if soft_max < hard_max and max_cost > 0:
        delta = model.NewIntVar(-7, 7, '')
        model.Add(delta == sum_var - soft_max)
        excess = model.NewIntVar(0, 7, prefix + ': over_sum')
        model.AddMaxEquality(excess, [delta, 0])
        cost_variables.append(excess)
        cost_coefficients.append(max_cost)

    return cost_variables, cost_coefficients

def distribution_constraint():
    
    return