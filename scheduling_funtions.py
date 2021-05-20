import itertools
import re


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

# https://github.com/google/or-tools/blob/master/examples/python/shift_scheduling_sat.py


def bounded_span(shifts, start, length, left_bound, right_bound):
    sequence = []
    # Left border (start of works, or works[start - 1])
    if start > 0 and left_bound:
        sequence.append(shifts[start - 1].Not())

    for i in range(length):
        sequence.append(shifts[start + i])

    # Right border (end of works or works[start + length])
    if start + length < len(shifts) and right_bound:
        sequence.append(shifts[start + length].Not())
    return sequence


def bounded_span_multi(shifts, start, length, left_bound, right_bound, division):
    sequence = []
    # Left border (start of works, or works[start - 1])
    if start > 0 and left_bound:
        sequence.append(shifts[start - 1].Not())

    for i in range(length):
        if i < division:
            sequence.append(shifts[0][start + i])
        else:
            sequence.append(shifts[1][start + i])

    # Right border (end of works or works[start + length])
    if start + length < len(shifts[0]) and right_bound:
        sequence.append(shifts[1][start + length].Not())
    return sequence


def predicates(start, length, prior, prior_shifts, post, post_shifts):
    b_prior = [prior_shifts[i + start].Not() if prior[i] == 0 else prior_shifts[i + start]
               for i in range(len(prior))]
    b_post = [post_shifts[i + start + length + len(post)].Not() if post[i] == 0 else post_shifts[i + start + length + len(post)]
              for i in range(len(post))]
    return b_prior + b_post


def forbid_min(model, shifts, hard_min, prior=[], post=[], prior_shifts=[], post_shifts=[], division=0):
    # Forbid sequences that are too short.
    prior_shifts = shifts if prior_shifts == [] else prior_shifts
    post_shifts = shifts if post_shifts == [] else post_shifts

    shift_length = len(shifts) if division == 0 else len(shifts[0])
    for length in range(1, hard_min):
        window_size = shift_length - length - len(prior) - len(post) + 1
        for start in range(window_size):
            pred = predicates(start, length, prior,
                              prior_shifts, post, post_shifts)
            if division == 0:
                span = bounded_span(shifts, start + len(prior),
                                    length, prior == [], post == [])
            else:
                span = bounded_span_multi(
                    shifts, start + len(prior), length, prior == [], post == [], division)
            print(pred)
            print(span)
            print()
            model.AddBoolOr(span).OnlyEnforceIf(pred)


def forbid_max(model, shifts, hard_max, prior=[], post=[], prior_shifts=[], post_shifts=[], division=0):
    # Just forbid any sequence of true variables with length hard_max + 1
    prior_shifts = shifts if prior_shifts == [] else prior_shifts
    post_shifts = shifts if post_shifts == [] else post_shifts

    shift_length = len(shifts) if division == 0 else len(shifts[0])
    window_size = shift_length - hard_max - len(prior) - len(post) + 1
    for start in range(window_size):
        pred = predicates(start, hard_max, prior,
                          prior_shifts, post, post_shifts)
        if division == 0:
            span = bounded_span(shifts, start + len(prior),
                                hard_max, False, False)
        else:
            span = bounded_span_multi(
                shifts, start + len(prior), hard_max, False, False, division)
        model.AddBoolOr(span).OnlyEnforceIf(pred)


def penalize_min(model, shifts, hard_min, soft_min, min_cost, prefix, prior=[], post=[], prior_shifts=[], post_shifts=[], division=0):
    cost_literals = []
    cost_coefficients = []
    prior_shifts = shifts if prior_shifts == [] else prior_shifts
    post_shifts = shifts if post_shifts == [] else post_shifts

  # Penalize sequences that are below the soft limit.
    shift_length = len(shifts) if division == 0 else len(shifts[0])
    for length in range(hard_min, soft_min):
        window_size = shift_length - length - len(prior) - len(post) + 1
        for start in range(window_size):
            pred = predicates(start, length, prior,
                              prior_shifts, post, post_shifts)
            if division == 0:
                span = bounded_span(shifts, start + len(prior),
                                    length, prior == [], post == [])
            else:
                span = bounded_span_multi(
                    shifts, start + len(prior), length, prior == [], post == [], division)
            name = ': under_span(start=%i, length=%i)' % (start, length)
            lit = model.NewBoolVar(prefix + name)
            span.append(lit)
            model.AddBoolOr(span).OnlyEnforceIf(pred)
            cost_literals.append(lit)
            # We filter exactly the sequence with a short length.
            # The penalty is proportional to the delta with soft_min.
            cost_coefficients.append(min_cost * (soft_min - length))

    return cost_literals, cost_coefficients


def penalize_max(model, shifts, hard_max, soft_max, max_cost, prefix, prior=[], post=[], prior_shifts=[], post_shifts=[], division=0):
    cost_literals = []
    cost_coefficients = []

    prior_shifts = shifts if prior_shifts == [] else prior_shifts
    post_shifts = shifts if post_shifts == [] else post_shifts

    shift_length = len(shifts) if division == 0 else len(shifts[0])
    for length in range(soft_max + 1, hard_max + 1):
        for start in range(shift_length - length - len(prior) - len(post)):
            pred = predicates(start, length, prior,
                              prior_shifts, post, post_shifts)
            if division == 0:
                span = bounded_span(shifts, start + len(prior),
                                    length, prior == [], post == [])
            else:
                span = bounded_span_multi(
                    shifts, start + len(prior), length, prior == [], post == [], division)
            name = ': over_span(start=%i, length=%i)' % (start, length)
            lit = model.NewBoolVar(prefix + name)
            span.append(lit)
            model.AddBoolOr(span).OnlyEnforceIf(pred)
            cost_literals.append(lit)
            # Cost paid is max_cost * excess length.
            cost_coefficients.append(max_cost * (length - soft_max))

    return cost_literals, cost_coefficients


def add_soft_sequence_min_constraint(model, shifts, hard_min, soft_min, min_cost, prefix,
                                     prior=[], post=[], prior_shifts=[], post_shifts=[], division=0):
    forbid_min(model, shifts, hard_min, prior, post,
               prior_shifts, post_shifts, division)
    return [], []
    # penalize_min(model, shifts, hard_min, soft_min, min_cost, prefix, prior, post, prior_shifts, post_shifts, division)


def add_soft_sequence_max_constraint(model, shifts, hard_max, soft_max, max_cost, prefix,
                                     prior=[], post=[], prior_shifts=[], post_shifts=[], division=0):
    forbid_max(model, shifts, hard_max, prior, post,
               prior_shifts, post_shifts, division)
    return penalize_max(model, shifts, hard_max, soft_max, max_cost, prefix, prior, post, prior_shifts, post_shifts, division)


def add_soft_sequence_constraint(model, shifts, hard_min, soft_min, min_cost,
                                 soft_max, hard_max, max_cost, prefix,
                                 prior=[], post=[], prior_shifts=[], post_shifts=[], division=0):
    forbid_min(model, shifts, hard_min, prior, post,
               prior_shifts, post_shifts, division)
    forbid_max(model, shifts, hard_max, prior, post,
               prior_shifts, post_shifts, division)
    var1, coeff1 = penalize_min(
        model, shifts, hard_min, soft_min, min_cost, prefix, prior, post, prior_shifts, post_shifts, division)
    var2, coeff2 = penalize_max(
        model, shifts, hard_max, soft_max, max_cost, prefix, prior, post, prior_shifts, post_shifts, division)
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
