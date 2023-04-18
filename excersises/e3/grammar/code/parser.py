from grammar import *
from parse import *


def is_in_language(words: list, grammar: Grammar) -> bool:
    return len(parse(words, grammar)) > 0


def parse(words: list, grammar: Grammar) -> list:
    """
    parses the list of words with grammar and returns the (possibly empty) list
    of possible parses. The ordering of possible parses is arbitrary.
    returns a list of ParseTree
    """
    n = len(words)
    field = [[set([]) for y in range(n)] for x in range(n)]  # field for cyk algorithm
    t = [[[] for _ in range(n)] for _ in range(n)]  # parse tree

    for i in range(0, n):  # filling the diagonal of the matrix with the corresponding non-terminals
        for rule in grammar.rules:
            if len(rule.rhs) == 1 and rule.rhs[0].symbol == words[i]:
                field[i][i].add(rule.lhs)
                t[i][i].append(ParseNode(rule.lhs, [ParseNode(rule.rhs[0])]))
    for i in range(1, n):
        for j in range(i, -1, -1):
            for k in range(j, i):
                for rule in grammar.rules:
                    if len(rule.rhs) == 2 and rule.rhs[0] in field[j][k] and rule.rhs[1] in field[k + 1][i]:
                        field[j][i].add(rule.lhs)
                        for left_node in t[j][k]:
                            for right_node in t[k+1][i]:
                                t[j][i].append(ParseTree(rule.lhs, [left_node, right_node]))
                        check_unary_rules(rule, grammar.rules, field[j][i], t[j][i])
    if grammar.start_symbol in field[0][n-1]:
        return [node for node in t[0][n-1] if node.symbol == grammar.start_symbol]
    else:
        return []  # not much better than the exception because we promise above to return all parses...


def check_unary_rules(current_rule, rules, field, t):
    """checks if a unary rule can be applied to the left hand side of current rule"""
    for r in rules:
        if len(r.rhs) == 1 and r.rhs[0] == current_rule.lhs:
            # if the current rule produces the current symbol, its left hand side will be added to the field
            field.add(r.lhs)
            # add parse nodes: all current nodes in t can be reached by the current rule r
            old_node_list = deepcopy(t)  # prevent endless loop
            for node in old_node_list:
                t.append(ParseTree(r.lhs, [node]))
            # in the case of chains of unary rules
            check_unary_rules(r, rules, field, t)


def example_telescope_parse():
    return \
        ParseTree(Symbol("$S"),
                  [ParseNode(Symbol("$NP"),
                             [ParseNode(Symbol("I"))]),
                   ParseNode(Symbol("$VP"),
                             [ParseNode(Symbol("$VP"),
                                        [ParseNode(Symbol("$V"),
                                                   [ParseNode(Symbol("saw"))]),
                                         ParseNode(Symbol("$NP"),
                                                   [ParseNode(Symbol("$Det"),
                                                              [ParseNode(Symbol("the"))]),
                                                    ParseNode(Symbol("$N"),
                                                              [ParseNode(Symbol("duck"))])])]),
                              ParseNode(Symbol("$PP"),
                                        [ParseNode(Symbol("$P"),
                                                   [ParseNode(Symbol("with"))]),
                                         ParseNode(Symbol("$NP"),
                                                   [ParseNode(Symbol("$Det"),
                                                              [ParseNode(Symbol("a"))]),
                                                    ParseNode(Symbol("$N"),
                                                              [ParseNode(Symbol("telescope"))])])])])])
