"""ortools_solvers.py

Enum representing all possible ORTools Solvers.
"""
from enum import Enum
from ortools.linear_solver import pywraplp


class ORToolsSolvers(Enum):
    CBC = pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING
    # GLPK = pywraplp.Solver.GLPK_MIXED_INTEGER_PROGRAMMING
    # GUROBI = pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING
    # CPLEX = pywraplp.Solver.CPLEX_MIXED_INTEGER_PROGRAMMING
