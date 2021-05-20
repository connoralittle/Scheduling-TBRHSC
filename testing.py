# from typing import Optional

# def divide(a: float, b: float) -> Optional[float]:
#     try:
#         return a / b
#     except: 
#         return None

# ans = divide(2.0, 1.0)

# print(ans)
# ef add_soft_sequence_constraint(model, works, hard_min, soft_min, min_cost,
#                                  soft_max, hard_max, max_cost, prefix):
#     """Sequence constraint on true variables with soft and hard bounds.
#   This constraint look at every maximal contiguous sequence of variables
#   assigned to true. If forbids sequence of length < hard_min or > hard_max.
#   Then it creates penalty terms if the length is < soft_min or > soft_max.
#   Args:
#     model: the sequence constraint is built on this model.
#     works: a list of Boolean variables.
#     hard_min: any sequence of true variables must have a length of at least
#       hard_min.
#     soft_min: any sequence should have a length of at least soft_min, or a
#       linear penalty on the delta will be added to the objective.
#     min_cost: the coefficient of the linear penalty if the length is less than
#       soft_min.
#     soft_max: any sequence should have a length of at most soft_max, or a linear
#       penalty on the delta will be added to the objective.
#     hard_max: any sequence of true variables must have a length of at most
#       hard_max.
#     max_cost: the coefficient of the linear penalty if the length is more than
#       soft_max.
#     prefix: a base name for penalty literals.
#   Returns:
#     a tuple (variables_list, coefficient_list) containing the different
#     penalties created by the sequence constraint.
#   """
#     cost_literals = []
#     cost_coefficients = []

#     # Forbid sequences that are too short.
#     for length in range(1, hard_min):
#         for start in range(len(works) - length - 1):
#             model.AddBoolOr(negated_bounded_span(works, start, length))

#     # Penalize sequences that are below the soft limit.
#     if min_cost > 0:
#         for length in range(hard_min, soft_min):
#             for start in range(len(works) - length - 1):
#                 span = negated_bounded_span(works, start, length)
#                 name = ': under_span(start=%i, length=%i)' % (start, length)
#                 lit = model.NewBoolVar(prefix + name)
#                 span.append(lit)
#                 model.AddBoolOr(span)
#                 cost_literals.append(lit)
#                 # We filter exactly the sequence with a short length.
#                 # The penalty is proportional to the delta with soft_min.
#                 cost_coefficients.append(min_cost * (soft_min - length))

#     # Penalize sequences that are above the soft limit.
#     if max_cost > 0:
#         for length in range(soft_max + 1, hard_max + 1):
#             for start in range(len(works) - length - 1):
#                 span = negated_bounded_span(works, start, length)
#                 name = ': over_span(start=%i, length=%i)' % (start, length)
#                 lit = model.NewBoolVar(prefix + name)
#                 span.append(lit)
#                 model.AddBoolOr(span)
#                 cost_literals.append(lit)
#                 # Cost paid is max_cost * excess length.
#                 cost_coefficients.append(max_cost * (length - soft_max))

#     # Just forbid any sequence of true variables with length hard_max + 1
#     for start in range(len(works) - hard_max):
#         model.AddBoolOr(
#             [works[i].Not() for i in range(start, start + hard_max + 1)])
#     return cost_literals, cost_coefficients