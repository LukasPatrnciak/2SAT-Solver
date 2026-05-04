#     2-SAT SOLVER
# Lukas Patrnciak
# AIS ID: 92320


import sys
from collections import deque
sys.setrecursionlimit(10**7) # Kvoli rekurzii


def literal_to_graph_index(x):
    variable = abs(x) - 1

    if x > 0:
        return 2 * variable

    else:
        return 2 * variable + 1


def negation_index(index):
    if index % 2 == 0:
        return index + 1

    else:
        return index - 1


def graph_index_to_literal(index):
    variable = index // 2 + 1

    if index % 2 == 0:
        return variable

    else:
        return -variable


def ensure_graph_size(graph, reverse_graph, variables_count):
    while len(graph) < 2 * variables_count:
        graph.append([])
        reverse_graph.append([])


def add_edge(graph, reverse_graph, from_vertex, to_vertex):
    if to_vertex not in graph[from_vertex]:
        graph[from_vertex].append(to_vertex)
        reverse_graph[to_vertex].append(from_vertex)

        return True

    return False


def add_clause_to_graph(graph, reverse_graph, a, b):
    a_i = literal_to_graph_index(a)
    b_i = literal_to_graph_index(b)

    not_a = negation_index(a_i)
    not_b = negation_index(b_i)

    added_edges = []

    if add_edge(graph, reverse_graph, not_a, b_i):
        added_edges.append((not_a, b_i))

    if add_edge(graph, reverse_graph, not_b, a_i):
        added_edges.append((not_b, a_i))

    return added_edges


def remove_edges_from_graph(graph, reverse_graph, added_edges):
    for from_vertex, to_vertex in added_edges:
        if to_vertex in graph[from_vertex]:
            graph[from_vertex].remove(to_vertex)

        if from_vertex in reverse_graph[to_vertex]:
            reverse_graph[to_vertex].remove(from_vertex)


def find_path(graph, start, end):
    parent = [-1] * len(graph)
    queue = deque()

    queue.append(start)
    parent[start] = start

    while queue:
        current = queue.popleft() # .pop(0)

        if current == end:
            break

        for neighbor in graph[current]:
            if parent[neighbor] == -1:
                parent[neighbor] = current
                queue.append(neighbor)

    if parent[end] == -1:
        return []

    path = []
    current = end

    while current != start:
        path.append(current)
        current = parent[current]

    path.append(start)
    path.reverse()

    literals_path = []

    for vertex in path:
        literals_path.append(graph_index_to_literal(vertex))

    return literals_path


def find_incremental_conflict_cycle(graph, variables_to_check):
    for variable in variables_to_check:
        positive = literal_to_graph_index(variable)
        negative = literal_to_graph_index(-variable)

        path1 = find_path(graph, positive, negative)
        path2 = find_path(graph, negative, positive)

        if path1 and path2:
            return path1 + path2[1:]

    return []


def kosaraju_algorithm(graph, reverse_graph):
    size = len(graph)

    visited = [False] * size
    order = []

    # Prvy DFS - urci poradie vrcholov v
    def dfs1(v):
        visited[v] = True

        for neighbor in graph[v]:
            if not visited[neighbor]:
                dfs1(neighbor)

        # Vrchol pridame az po spracovani vsetkych susedov
        order.append(v)

    for vertex in range(size):
        if not visited[vertex]:
            dfs1(vertex)

    components = [-1] * size

    # Druhy DFS - najde jednu silne suvislu komponentu comp
    def dfs2(v, comp_id):
        components[v] = comp_id

        for neighbor in reverse_graph[v]:
            if components[neighbor] == -1:
                dfs2(neighbor, comp_id)

    component_id = 0

    # Ideme od vrcholov, ktore sa vytvorili naposledy
    for vertex in reversed(order):
        if components[vertex] == -1:
            dfs2(vertex, component_id)
            component_id = component_id + 1

    return components


def solve_from_graph(graph, reverse_graph, variables_count):
    components = kosaraju_algorithm(graph, reverse_graph)

    for i in range(variables_count):
        positive = 2 * i
        negative = 2 * i + 1

        if components[positive] == components[negative]:
            return None

    assignment = []

    for i in range(variables_count):
        positive = 2 * i
        negative = 2 * i + 1

        value = components[positive] > components[negative]
        assignment.append(value)

    return assignment


def find_critical_cycle(graph, reverse_graph, variables_count):
    components = kosaraju_algorithm(graph, reverse_graph)

    for i in range(variables_count):
        positive = 2 * i
        negative = 2 * i + 1

        if components[positive] == components[negative]:
            path1 = find_path(graph, positive, negative)
            path2 = find_path(graph, negative, positive)

            if path1 and path2:
                return path1 + path2[1:]

    return []


def build_graph(variables_count, clauses):
    graph = []
    reverse_graph = []

    ensure_graph_size(graph, reverse_graph, variables_count)

    for a, b in clauses:
        add_clause_to_graph(graph, reverse_graph, a, b)

    return graph, reverse_graph


def static_mode(line):
    variables_count, clauses_count = map(int, line.split())

    clauses = []

    for i in range(clauses_count):
        literal_a, literal_b = map(int, input().split())
        clauses.append((literal_a, literal_b))

    graph, reverse_graph = build_graph(variables_count, clauses)
    result = solve_from_graph(graph, reverse_graph, variables_count)

    if result is None:
        print("UNSAT")

        cycle = find_critical_cycle(graph, reverse_graph, variables_count)

        if cycle:
            print("Path detected:", " -> ".join(map(str, cycle)))

    else:
        print("SAT")

        values = []

        for value in result:
            values.append(str(int(value)))

        print(" ".join(values))


def interactive_mode(line):
    max_variable = 0
    graph = []
    reverse_graph = []

    while True:
        parts = line.split()

        if len(parts) == 0:
            line = input()
            continue

        command = parts[0]

        if command == "Q":
            break

        elif command == "A":
            literal_a = int(parts[1])
            literal_b = int(parts[2])

            new_max_variable = max(max_variable, abs(literal_a), abs(literal_b))

            ensure_graph_size(graph, reverse_graph, new_max_variable)

            old_max_variable = max_variable
            max_variable = new_max_variable

            added_edges = add_clause_to_graph(graph, reverse_graph, literal_a, literal_b)
            cycle = find_incremental_conflict_cycle(graph, [abs(literal_a), abs(literal_b)])

            if cycle:
                remove_edges_from_graph(graph, reverse_graph, added_edges)
                max_variable = old_max_variable

                print("UNSAT: Clause (" + str(literal_a) + " v " + str(literal_b) + ") rejected.")
                print("Path detected:", " -> ".join(map(str, cycle)))

            else:
                print("SAT: Clause (" + str(literal_a) + " v " + str(literal_b) + ") accepted.")

        elif command == "S":
            result = solve_from_graph(graph, reverse_graph, max_variable)

            if result is None:
                print("UNSAT")

            else:
                print("SAT")

                values = []

                for value in result:
                    values.append(str(int(value)))

                print(" ".join(values))

        line = input()



# SPUSTENIE V MODOCH NA ZAKLADE VSTUPU
first_line = input()

if first_line and first_line[0].isdigit():
    static_mode(first_line)

else:
    interactive_mode(first_line)