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
    field = [[set([]) for y in range(n)] for x in range(n)]  # initializes array of size (n,n);necessary to prevent any issues with copy by reference
    t = [[[] for _ in range(n)] for _ in range(n)]

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
                        for left_node in field[k][i]:
                            for right_node in field[j][k+1]:
                                t[j][i].append(ParseTree(rule.lhs, [left_node, right_node]))
    if grammar.start_symbol in field[0][n - 1]:
        return [node for node in t[0][n - 1] if node.symbol == grammar.start_symbol]
    else:
        return []  # not much better than the exception because we promise above to return all parses...


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
