import sys
import regex as re
import os

r_inner = r'([^\s\(\)]+|\(([^()]|(?R))*\))'
operators = ['+', '-', '*', '/', '<', '<=', '=', '>=', '>']
lboperators = ['<=', '>=', '=', '>','<', 'and', 'or']
r_op = r'('
for o in lboperators:
    r_op += o + '|'
r_op = r_op[:-1] + r')'

if len(sys.argv) < 2:
    exit(1)

print(os.path)
f = open(sys.argv[1], "r")

content = f.read()


def clean_whitespace(formula):
    return re.sub(r' +', ' ', formula)


def get_all_with_required_depth(formula, req_bracket_depth):
    return get_all_with_required_depth_rec(formula, -1, -1, req_bracket_depth,
                                           req_bracket_depth)[0]


def get_all_with_bracket_bounds(formula, min_depth, max_depth, min_bracket_depth,
                                max_bracket_depth):
    return get_all_with_required_depth_rec(formula, min_depth, max_depth, min_bracket_depth,
                                           max_bracket_depth)[0]


def get_all_with_required_depth_rec(formula, min_depth, max_depth, min_bracket_depth,
                                    max_bracket_depth, results=None,
                                    current_depth=0, index=0):
    if results is None:
        results = list()
    maximum = current_depth
    while index < len(formula):
        c = formula[index]
        if c == '(':
            (results, new_index, new_max) = \
                get_all_with_required_depth_rec(formula, min_depth, max_depth,
                                                min_bracket_depth,
                                                max_bracket_depth,
                                                results, current_depth + 1,
                                                index + 1)
            bracket_depth = new_max - current_depth
            if (min_bracket_depth <= bracket_depth
                or min_bracket_depth == -1) \
                    and (
                    bracket_depth <= max_bracket_depth
                    or max_bracket_depth == -1)\
                    and (
                    min_depth <= current_depth or min_depth == -1)\
                    and (
                    current_depth <= max_depth or max_depth == -1):
                results.append((index, new_index + 1))
            maximum = max(maximum, new_max)
            index = new_index
        elif c == ')':
            break
        index += 1
    return results, index, maximum


def replace_vars(formula):
    r = r'([v_][a-zA-Z0-9_-]*)'
    m = re.search(r, formula)
    while m is not None:
        print(m[0])
        s = m[0].split('_')
        name = s[1] + s[-1]
        print(name)
        formula = formula.replace(m[0], name)
        m = re.search(r, formula)
    return formula


def find_max_depth(formula):
    top = 0
    curr = 0
    for c in formula:
        if c == '(':
            curr += 1
        elif c == ')':
            curr -= 1
        else:
            continue
        top = max(top, curr)
    return top


def rearrange_operators(formula):
    max_depth = find_max_depth(formula)
    for i in range(0, find_max_depth(formula) + 1):
        matches = get_all_with_required_depth(formula, i)
        formula = replace_matches(formula, matches)
    return clean_whitespace(formula)


def replace_matches(formula, matches):
    for match_bounds in matches:
        match = formula[match_bounds[0]:match_bounds[1]]
        op = re.search(r'([\S]+)', match[1:])[0]
        if op not in operators:
            continue
        inner = list(re.finditer(r_inner, match[1:-1]))
        if len(inner) >= 2:
            replace = ""
            j = 1
            while j < len(inner) - 1:
                replace += inner[j][0] + inner[0][0]
                j += 1
            replace += inner[-1][0]
            replace = '(' + replace + ')'
        else:
            replace = match
        difference = len(match) - len(replace)
        replace = replace + difference * ' '
        start = match_bounds[0]
        end = match_bounds[1]
        formula = formula[0:start] + replace + formula[end:]
        pass
    return formula


def format_brackets(formula):
    d = 0
    new_formula = ''
    for c in formula:
        if c == '(':
            new_formula += '\n' + '  '*d
            d += 1
        elif c == ')':
            d -= 1
        new_formula += c
    return new_formula


formula = re.search(r'(\(.*\))', content)[0]
formula = replace_vars(formula)
print(formula)
formula = rearrange_operators(formula)
formula = format_brackets(formula)
print(formula)
