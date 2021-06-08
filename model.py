from ortools.sat.python.cp_model import *
from data import *
from typing import Dict, List, Tuple


def create_model() -> CpModel:
    return CpModel()


def create_model_variables(model: CpModel,
                           prefix: str,
                           staff: List[int],
                           days: List[int]) -> Dict[Tuple, IntVar]:
    return {(m, d):
            model.NewBoolVar(f"{prefix}_staff_{m}_day_{d}")
            for m in staff
            for d in days}

 
def create_model_variables_long(model: CpModel,
                           prefix: str,
                           staff: List[int],
                           days: List[int],
                           shifts: List[int]) -> Dict[Tuple, IntVar]:
    return {(m, d, s):
            model.NewBoolVar(f"{prefix}_staff_{m}_day_{d}_shift_{s}")
            for m in staff
            for d in days
            for s in shifts}


def create_model_variables_int(model: CpModel,
                           prefix: str,
                           ub: int,
                           lb: int,
                           staff: List[int],
                           days: List[int],
                           shifts: List[int]) -> Dict[Tuple, IntVar]:
    return {(m, d, s):
            model.NewIntVar(lb, ub, f"{prefix}_staff_{m}_day_{d}")
            for m in staff
            for d in days
            for s in shifts}

def constraints_equal_sum(model: CpModel,
                          constraints: Dict[str, IntVar],
                          sums: Dict[str, IntVar],
                          staff: List[int],
                          days: List[int],
                          shifts: List[int]) -> Dict[Tuple, IntVar]:
    for m in staff:
        for d in days:
            model.Add(constraints[m, d] == sum(
                sums[m, d, s] for s in shifts))


def create_model_variables_with_sum(model: CpModel,
                                    prefix: str,
                                    sums: Dict[Tuple, IntVar],
                                    staff: List[int],
                                    days: List[int],
                                    shifts: List[int]) -> Dict[Tuple, IntVar]:
    constraints = {(m, d):
                   model.NewBoolVar(f"{prefix}_staff_{m}_day_{d}")
                   for m in staff
                   for d in days}

    constraints_equal_sum(model, constraints,
                          sums, staff, days, shifts)

    return constraints


def create_staff_variables(model: CpModel,
                           prefix: str,
                           values: List[str],
                           lb: int,
                           ub: int,
                           enforcements: Dict[Tuple, IntVar],
                           staff: List[int],
                           days: List[int],
                           shifts: List[int]) -> Dict[Tuple, IntVar]:

    constraints = create_model_variables_int(model, prefix, ub, lb, staff, days, shifts)

    for m in staff:
        for d in days:
            for s in shifts:
                model.Add(constraints[m, d, s] ==
                          values[m]).OnlyEnforceIf(enforcements[m, d, s])
                model.Add(constraints[m, d, s] == 0).OnlyEnforceIf(
                    enforcements[m, d, s].Not())

    return constraints


def create_solver(time_seconds: int) -> CpSolver:
    solver = CpSolver()
    solver.parameters.max_time_in_seconds = time_seconds
    solver.parameters.num_search_workers = 4
    return solver


def empty_minimize_constraints() -> Tuple[List, List]:
    return [], []

class VarArraySolutionPrinter(CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables):
        CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self):
        self.__solution_count += 1
        for v in self.__variables:
            print('%s=%i' % (v, self.Value(v)), end=' ')
        print()

    def solution_count(self):
        return self.__solution_count