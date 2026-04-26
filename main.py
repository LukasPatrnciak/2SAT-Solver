"""
2-SAT Solver
============

Implements:
1. Static batch 2-SAT solver
2. Dynamic interactive 2-SAT solver with rollback

Author: generated solution for ADS assignment
"""

from collections import defaultdict
import sys


class TwoSATSolver:
    def __init__(self):
        # graph[u] = set of vertices reachable from u
        self.graph = defaultdict(set)

        # all variables that appeared so far
        self.variables = set()

    # ------------------------------------------------------------
    # Literal utilities
    # ------------------------------------------------------------

    def negate(self, literal):
        """Return negated literal."""
        return -literal

    def remember_literal(self, literal):
        """Store variable number without sign."""
        self.variables.add(abs(literal))

    # ------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------

    def add_edge(self, source, target):
        """Add implication source -> target."""
        self.graph[source].add(target)

        # Make sure both vertices exist in graph, even if target has no outgoing edges.
        if target not in self.graph:
            self.graph[target] = set()

    def remove_edge(self, source, target):
        """Remove implication source -> target if it exists."""
        if source in self.graph and target in self.graph[source]:
            self.graph[source].remove(target)

    def clause_to_edges(self, first_literal, second_literal):
        """
        Convert clause (a v b) into two implications:
            not a -> b
            not b -> a
        """
        edge_1 = (self.negate(first_literal), second_literal)
        edge_2 = (self.negate(second_literal), first_literal)
        return edge_1, edge_2

    def add_clause_without_check(self, first_literal, second_literal):
        """Add a clause without checking satisfiability."""
        self.remember_literal(first_literal)
        self.remember_literal(second_literal)

        edge_1, edge_2 = self.clause_to_edges(first_literal, second_literal)
        self.add_edge(edge_1[0], edge_1[1])
        self.add_edge(edge_2[0], edge_2[1])

        return [edge_1, edge_2]

    def add_clause_dynamic(self, first_literal, second_literal):
        """
        Try to add a clause dynamically.

        If the new clause keeps the formula SAT, it stays in the graph.
        If it makes the formula UNSAT, added edges are removed = rollback.
        """
        added_edges = self.add_clause_without_check(first_literal, second_literal)

        is_sat, assignment, conflict = self.solve()

        if is_sat:
            return True, assignment, None

        # Rollback: remove only edges added by this operation.
        for source, target in added_edges:
            self.remove_edge(source, target)

        return False, None, conflict

    # ------------------------------------------------------------
    # Tarjan SCC algorithm
    # ------------------------------------------------------------

    def tarjan_scc(self):
        """Return dictionary vertex -> component_id."""
        index_counter = [0]
        stack = []
        on_stack = set()
        index = {}
        lowlink = {}
        component = {}
        component_id = [0]

        def strong_connect(vertex):
            index[vertex] = index_counter[0]
            lowlink[vertex] = index_counter[0]
            index_counter[0] += 1

            stack.append(vertex)
            on_stack.add(vertex)

            for neighbour in self.graph[vertex]:
                if neighbour not in index:
                    strong_connect(neighbour)
                    lowlink[vertex] = min(lowlink[vertex], lowlink[neighbour])
                elif neighbour in on_stack:
                    lowlink[vertex] = min(lowlink[vertex], index[neighbour])

            # Root of SCC
            if lowlink[vertex] == index[vertex]:
                while True:
                    item = stack.pop()
                    on_stack.remove(item)
                    component[item] = component_id[0]

                    if item == vertex:
                        break

                component_id[0] += 1

        # Make sure both x and -x exist for every known variable.
        for variable in self.variables:
            if variable not in self.graph:
                self.graph[variable] = set()
            if -variable not in self.graph:
                self.graph[-variable] = set()

        for vertex in list(self.graph.keys()):
            if vertex not in index:
                strong_connect(vertex)

        return component

    # ------------------------------------------------------------
    # SAT solving
    # ------------------------------------------------------------

    def solve(self):
        """
        Check whether current formula is SAT.

        Returns:
            (True, assignment, None)
            or
            (False, None, conflict_variable)
        """
        component = self.tarjan_scc()

        for variable in sorted(self.variables):
            if component[variable] == component[-variable]:
                return False, None, variable

        assignment = {}

        for variable in sorted(self.variables):
            # With this Tarjan numbering, this gives a valid assignment for our SCC order.
            assignment[variable] = component[variable] > component[-variable]

        return True, assignment, None

    # ------------------------------------------------------------
    # Path detection for explanation
    # ------------------------------------------------------------

    def find_path(self, start, target):
        """Find one path from start to target using DFS."""
        visited = set()
        parent = {}
        stack = [start]
        visited.add(start)

        while stack:
            current = stack.pop()

            if current == target:
                path = []
                while current in parent:
                    path.append(current)
                    current = parent[current]
                path.append(start)
                path.reverse()
                return path

            for neighbour in self.graph[current]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    parent[neighbour] = current
                    stack.append(neighbour)

        return None

    def conflict_path(self, variable):
        """
        Try to show why variable conflicts with its negation.

        In UNSAT case, there should be paths:
            x -> -x
            -x -> x
        """
        path_1 = self.find_path(variable, -variable)
        path_2 = self.find_path(-variable, variable)

        if path_1 and path_2:
            return path_1 + path_2[1:]
        if path_1:
            return path_1
        if path_2:
            return path_2
        return None


# ----------------------------------------------------------------
# Output helpers
# ----------------------------------------------------------------


def format_bool(value):
    return "1" if value else "0"


def print_assignment(assignment):
    print("SAT")
    for variable in sorted(assignment):
        print(f"x{variable} = {format_bool(assignment[variable])}")


# ----------------------------------------------------------------
# Static mode
# ----------------------------------------------------------------


def run_static_mode():
    solver = TwoSATSolver()

    first_line = sys.stdin.readline().strip()
    if not first_line:
        print("Empty input.")
        return

    number_of_variables, number_of_clauses = map(int, first_line.split())

    # Remember all variables from 1 to N, even if some do not appear in clauses.
    for variable in range(1, number_of_variables + 1):
        solver.variables.add(variable)

    for _ in range(number_of_clauses):
        line = sys.stdin.readline().strip()
        if not line:
            continue

        first_literal, second_literal = map(int, line.split())
        solver.add_clause_without_check(first_literal, second_literal)

    is_sat, assignment, conflict = solver.solve()

    if is_sat:
        print_assignment(assignment)
    else:
        print("UNSAT")
        print(f"Critical conflict: x{conflict} and -x{conflict} are in the same SCC")

        path = solver.conflict_path(conflict)
        if path:
            print("Critical cycle:", " -> ".join(map(str, path)))


# ----------------------------------------------------------------
# Dynamic mode
# ----------------------------------------------------------------


def run_dynamic_mode():
    solver = TwoSATSolver()

    for raw_line in sys.stdin:
        line = raw_line.strip()

        if not line:
            continue

        # Allow comments after %
        if "%" in line:
            line = line.split("%", 1)[0].strip()
            if not line:
                continue

        parts = line.split()
        command = parts[0].upper()

        if command == "Q":
            break

        if command == "S":
            is_sat, assignment, conflict = solver.solve()

            if is_sat:
                print_assignment(assignment)
            else:
                # This should not happen if rollback works correctly.
                print("UNSAT")
                print(f"Critical conflict: x{conflict} and -x{conflict}")

            continue

        if command == "A":
            if len(parts) != 3:
                print("Invalid command. Use: A l1 l2")
                continue

            first_literal = int(parts[1])
            second_literal = int(parts[2])

            success, assignment, conflict = solver.add_clause_dynamic(first_literal, second_literal)

            if success:
                print(f"ADDED: ({first_literal} v {second_literal})")
            else:
                print(f"UNSAT: Clause ({first_literal} v {second_literal}) rejected.")
                path = solver.conflict_path(conflict)

                if path:
                    print("Path detected:", " -> ".join(map(str, path)))
                else:
                    print(f"Conflict detected between {conflict} and {-conflict}.")

            continue

        print("Unknown command. Use A, S or Q.")


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------


def main():
    if len(sys.argv) >= 2:
        mode = sys.argv[1].lower()
    else:
        mode = "dynamic"

    if mode == "static":
        run_static_mode()
    elif mode == "dynamic":
        run_dynamic_mode()
    else:
        print("Unknown mode.")
        print("Use:")
        print("  python two_sat_solver.py static")
        print("  python two_sat_solver.py dynamic")


if __name__ == "__main__":
    main()
