import copy


class Algorithm:
    def get_algorithm_steps(self, tiles, variables, words):
        pass


class ExampleAlgorithm(Algorithm):

    def get_algorithm_steps(self, tiles, variables, words):
        moves_list = [['0h', 0], ['0v', 2], ['1v', 1], ['2h', 1], ['4h', None],
                 ['2h', None], ['1v', None], ['0v', 3], ['1v', 1], ['2h', 1],
                 ['4h', 4], ['5v', 5]]
        domains = {var: [word for word in words] for var in variables}
        solution = []
        for move in moves_list:
            solution.append([move[0], move[1], domains])
        return solution


result = []


def is_consistent(tiles, var, val):
    row = int(int(var[0:len(var) - 1]) / len(tiles[0]))
    column = int(int(var[0:len(var) - 1]) % len(tiles[0]))

    if var[len(var) - 1:len(var)] == "h":
        for i in range(0, len(val)):
            if (tiles[row][column + i] is False or
                    tiles[row][column + i] == val[i]):
                continue
            else:
                return False
    else:
        for i in range(0, len(val)):
            if (tiles[row + i][column] is False or
                    tiles[row + i][column] == val[i]):
                continue
            else:
                return False

    return True


def update_tiles(tiles, var, val):
    row = int(int(var[0:len(var) - 1]) / len(tiles[0]))
    column = int(int(var[0:len(var) - 1]) % len(tiles[0]))

    if var[len(var) - 1:len(var)] == "h":
        for i in range(0, len(val)):
            tiles[row][column + i] = val[i]
    else:
        for i in range(0, len(val)):
            tiles[row + i][column] = val[i]


def backtrack_search(vars, domains, lvl, tiles):
    if lvl == len(vars):
        return True

    var = tuple(vars)[lvl]
    for val in domains[var]:
        if is_consistent(tiles, var, val):
            result.append([var, domains[var].index(val), domains])
            new_domain = copy.deepcopy(domains)
            new_domain[var] = [val]

            new_tiles = copy.deepcopy(tiles)
            update_tiles(new_tiles, var, val)
            if backtrack_search(vars, new_domain, lvl + 1, new_tiles):
                return True

    result.append([var, None, domains])
    return False


class Backtracking(Algorithm):

    def get_algorithm_steps(self, tiles, variables, words):
        domains = {var: [word for word in words if len(word) == variables[var]] for var in variables}

        backtrack_search(variables, domains, 0, tiles)

        return result


def update_domain(domains, tiles, var):
    dom = []
    for d in domains[var]:
        if is_consistent(tiles, var, d):
            dom.append(d)
    domains[var] = dom


def forward_checking_search(vars, domains, lvl, tiles):
    if lvl == len(vars):
        return True

    var = tuple(vars)[lvl]
    for val in domains[var]:
        if is_consistent(tiles, var, val):
            new_domain = copy.deepcopy(domains)
            new_domain[var] = [val]

            new_tiles = copy.deepcopy(tiles)
            update_tiles(new_tiles, var, val)
            domain_empty_flag = 0
            for v in tuple(vars):
                if v != var and tuple(vars).index(v) > tuple(vars).index(var):
                    update_domain(new_domain, new_tiles, v)
                    if len(new_domain[v]) == 0:
                        domain_empty_flag = 1
                        #break

            #result.append([var, new_domain[var].index(val), new_domain])
            result.append([var, domains[var].index(val), domains])
            if domain_empty_flag:
                continue

            if forward_checking_search(vars, new_domain, lvl + 1, new_tiles):
                return True

    result.append([var, None, domains])
    return False


class ForwardChecking(Algorithm):

    def get_algorithm_steps(self, tiles, variables, words):
        domains = {var: [word for word in words if len(word) == variables[var]] for var in variables}

        forward_checking_search(variables, domains, 0, tiles)

        for move in result:
            print(move)
            print("\n")

        return result


def are_constrained(v, x, constraints):
    return [v, x] in constraints or [x, v] in constraints


def satisfies_constraint(val_x, val_y, x, y, tiles):
    new_tiles = copy.deepcopy(tiles)
    update_tiles(new_tiles, x, val_x)

    row = int(int(y[0:len(y) - 1]) / len(tiles[0]))
    column = int(int(y[0:len(y) - 1]) % len(tiles[0]))

    if y[len(y) - 1:len(y)] == "h":
        for i in range(0, len(val_y)):
            if (new_tiles[row][column + i] is False or
                    new_tiles[row][column + i] == val_y[i]):
                continue
            else:
                return False
    else:
        for i in range(0, len(val_y)):
            if (new_tiles[row + i][column] is False or
                    new_tiles[row + i][column] == val_y[i]):
                continue
            else:
                return False

    return True


def arc_consistency(vars, domains, constraints, tiles): # constraints -> arc_list
    # comm next line
    arc_list = copy.deepcopy(constraints)
    #all_constraints = []
    #get_constraints(vars, len(tiles[0]), all_constraints)

    while arc_list:
        x, y = arc_list.pop(0)
        x_vals_delete = []
        for val_x in domains[x]:
            y_empty = True
            for val_y in domains[y]:
                if satisfies_constraint(val_x, val_y, x, y, tiles):
                    y_empty = False
                    break
            if y_empty:
                x_vals_delete.append(val_x)
        if x_vals_delete:
            domains[x] = [v for v in domains[x] if v not in x_vals_delete]
            if not domains[x]:
                return False
            for v in vars:
                if v != x and are_constrained(v, x, constraints): # constraints -> all_constraints
                    arc_list.append((v, x))
                    # comm next line
                    arc_list.append((x, v))
    return True


def arc_consistency_search(vars, domains, lvl, constraints, tiles):
    if lvl == len(vars):
        return True

    var = tuple(vars)[lvl]
    for val in domains[var]:
        if is_consistent(tiles, var, val):
            new_domain = copy.deepcopy(domains)
            new_domain[var] = [val]

            new_tiles = copy.deepcopy(tiles)
            update_tiles(new_tiles, var, val)
            #constraints = []
            # ~comm next line
            #get_constraints_for_var(var, vars, len(tiles[0]), constraints)
            if not arc_consistency(vars, new_domain, constraints, new_tiles):
                result.append([var, domains[var].index(val), domains])
                continue
            result.append([var, domains[var].index(val), domains])
            if arc_consistency_search(vars, new_domain, lvl + 1, constraints, new_tiles):
                return True

    result.append([var, None, domains])
    return False


def get_constraints_for_var(v, variables, tiles_width, constraints):
    list = dict()
    for var in variables:
        start = int(var[0:len(var) - 1])
        val = variables[var]
        list[var] = []

        if var[len(var) - 1:len(var)] == "h":
            for i in range(0, val):
                list[var].append(start + i)
        else:
            for i in range(0, val):
                list[var].append(start + i * tiles_width)

    for x in tuple(list):
        if x != v and set(list[x]).intersection(set(list[v])):
            constraints.append([x, v])
            # comm next line
            constraints.append([v, x])


def get_constraints(variables, tiles_width, constraints):
    list = dict()
    for var in variables:
        start = int(var[0:len(var) - 1])
        val = variables[var]
        list[var] = []

        if var[len(var) - 1:len(var)] == "h":
            for i in range(0, val):
                list[var].append(start + i)
        else:
            for i in range(0, val):
                list[var].append(start + i * tiles_width)

    for i in range(0, len(list) - 1):
        x = tuple(list)[i]
        for j in range(i + 1, len(list)):
            y = tuple(list)[j]
            if set(list[x]).intersection(set(list[y])):
                constraints.append([x, y])
                # comm next line
                constraints.append([y, x])


class ArcConsistency(Algorithm):

    def get_algorithm_steps(self, tiles, variables, words):
        domains = {var: [word for word in words if len(word) == variables[var]] for var in variables}
        constraints = []
        # comm next line
        get_constraints(variables, len(tiles[0]), constraints)

        arc_consistency_search(variables, domains, 0, constraints, tiles)

        return result