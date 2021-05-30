from ortools.sat.python import cp_model
from data import *

model = cp_model.CpModel()
solver = cp_model.CpSolver()

# decision variables
# staff 'm' works shift 's' on day 'd'
works = {(m, d, s):
         model.NewBoolVar('works_s%id%is%i' % (m, d, s))
         for m in staff
         for d in days
         for s in shifts}

# intermediate variables
# staff 'm' works on day 'd'

# This enforces the constraint
# No two shifts same day
days_assigned = {(m, d):
                 model.NewBoolVar('days_works_s%id%i' % (m, d))
                 for m in staff
                 for d in days}

for m in staff:
    for d in days:
        model.Add(days_assigned[m, d] == sum(works[m, d, s] for s in shifts))

# intermediate variables
# staff 'm' works on day 'd' on midnight shift 's'
afternoon_shifts_assigned = {(m, d):
                             model.NewBoolVar('afternoon_s%id%i' % (m, d))
                             for m in staff
                             for d in days}

for m in staff:
    for d in days:
        model.Add(afternoon_shifts_assigned[m, d] == sum(
            works[m, d, s] for s in afternoon_shifts))

# intermediate variables
# staff 'm' works on day 'd' on midnight shift 's'
midnight_shifts_assigned = {(m, d):
                            model.NewBoolVar('midnight_s%id%i' % (m, d))
                            for m in staff
                            for d in days}

for m in staff:
    for d in days:
        model.Add(midnight_shifts_assigned[m, d] == sum(
            works[m, d, s] for s in midnight_shifts))

# intermediate variables
# staff 'm' works on day 'd' on midnight shift 's'
on_call_shifts_assigned = {(m, d):
                           model.NewBoolVar('on_call_s%id%i' % (m, d))
                           for m in staff
                           for d in days}

for m in staff:
    for d in days:
        model.Add(on_call_shifts_assigned[m, d] == sum(
            works[m, d, s] for s in on_call_shifts))

# intermediate variables
# staff 'm' works on day 'd' on ft shift 's'
ft_shifts_assigned = {(m, d):
                      model.NewBoolVar('ft_s%id%i' % (m, d))
                      for m in staff
                      for d in days}

for m in staff:
    for d in days:
        model.Add(ft_shifts_assigned[m, d] == sum(
            works[m, d, s] for s in ft_shifts))

# intermediate variables
# staff 'm' works on day 'd' on late shift 's'
late_shifts_assigned = {(m, d):
                        model.NewBoolVar('late_s%id%i' % (m, d))
                        for m in staff
                        for d in days}

for m in staff:
    for d in days:
        model.Add(late_shifts_assigned[m, d] == sum(
            works[m, d, s] for s in late_shifts))

# intermediate variables
# staff 'm' works on day 'd' on late shift 's'
after_5_shifts_assigned = {(m, d):
                           model.NewBoolVar('after_5_s%id%i' % (m, d))
                           for m in staff
                           for d in days}

for m in staff:
    for d in days:
        model.Add(after_5_shifts_assigned[m, d] == sum(
            works[m, d, s] for s in late_shifts + midnight_shifts))

# intermediate variables
# staff 'm' works on day 'd' on midnight shift 's'
after_930_shifts_assigned = {(m, d):
                            model.NewBoolVar('after_930_s%id%i' % (m, d))
                            for m in staff
                            for d in days}

for m in staff:
    for d in days:
        model.Add(after_930_shifts_assigned[m, d] == sum(
            works[m, d, s] for s in not_shifts(day_shifts)))


# intermediate variables
# staff 'm' works on day 'd' on late shift 's'
day_shifts_assigned = {(m, d):
                       model.NewBoolVar('day_s%id%i' % (m, d))
                       for m in staff
                       for d in days}

for m in staff:
    for d in days:
        model.Add(day_shifts_assigned[m, d] == sum(
            works[m, d, s] for s in day_shifts))

obj_int_vars = []
obj_int_coeffs = []
obj_bool_vars = []
obj_bool_coeffs = []
