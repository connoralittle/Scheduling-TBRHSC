from ortools.sat.python import cp_model
import itertools
from calendar import monthrange

# https://docs.python.org/release/2.3.5/lib/itertools-example.html
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

def main():

    staff_list = [['Olivia', 0],
                ['Emma', 1], 
                ['Ava', 1],
                ['Charlotte', 1], 
                ['Sophia', 0],
                ['Amelia', 0],
                ['Isabella', 1],
                ['Mia', 1],
                ['Evelyn', 1],
                ['Harper', 0],
                ['Camila', 0],
                ['Gianna', 0],
                ['Abigail', 0], 
                ['Luna', 0],
                ['Ella', 0],
                ['Elizabeth', 0], 
                ['Sofia', 1],
                ['Emily', 1],
                ['Avery', 0],
                ['Mila', 1]]

    staff_length = len(staff_list)
    staff = range(staff_length)

    shift_list = ['0700 - 1500',
            '0730 - 1530 (FT)',
            '0930 - 1730',
            '1200 - 2000',
            '1400 - 2200',
            '1530 - 2330 (FT)',
            '1600 - 2400',
            '1800 - 0200',
            '2000 - 0400',
            '2200 - 0400',
            '2359 - 0700',
            'On call (22:00)']

    midnight_offset = 6
    midnight_shifts = range(len(shift_list[6:]))

    shift_length = len(shift_list)
    shifts = range(shift_length)

    planning_period = monthrange(2021, 5)
    days_length = planning_period[1]
    days = range(planning_period[1])

    model = cp_model.CpModel()

    #decision variables
    #staff 'm' works shift 's' on day 'd'
    x = {(m, d, s) : \
        model.NewBoolVar('s%id%is%i' % (m, d, s)) \
        for m in staff \
        for d in days \
        for s in shifts}

    # All shifts should be taken by doctors
    # No two doctors in the same shift on the same day
    for d in days:
        for s in shifts:
            constraint = [x[(m,d,s)] \
                            for m in staff]
            model.Add(sum(constraint) == 1)

    # Maximum work 7 consecutive days
    num_con_days = 7
    for m in staff:
        for wind in window(days, num_con_days+1):
            constraint = [x[(m,d,s)] \
                        for d in wind \
                        for s in shifts]

            model.Add(sum(constraint) <= num_con_days) 

    #solve and print
    # model.Maximize(0)d

    solver = cp_model.CpSolver()
    solver.Solve(model)

    for d in days:
        print('Day', d)
        for m in staff:
            for s in shifts:
                if solver.Value(x[(m, d, s)]) == 1:
                    print(staff_list[m], 'works shift', shift_list[s])
        print()



if __name__ == "__main__":
   main()