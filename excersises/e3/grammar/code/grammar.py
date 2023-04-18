import re
from collections import defaultdict
from typing import List, Tuple, Mapping


class Symbol:
    """symbols of the grammar"""

    terminal: bool
    symbol: str

    def __init__(self, symbol: str):
        self.terminal = not symbol.startswith("$")
        self.symbol = symbol if self.terminal else symbol[1:]

    def __repr__(self):
        return ("" if self.terminal else "$") + self.symbol

    def __eq__(self, other):
        return self.symbol == other.symbol and self.terminal == other.terminal

    def __hash__(self):
        return hash(self.symbol)


class GrammarRule:
    """
    simple sequence rule.
    We don't support anything more complex;
    alternatives will have to be split into multiple sub-rules """

    lhs: Symbol
    rhs: List[Symbol]  # it's a list of Symbols
    expression: Symbol

    def __init__(self, lhs: Symbol, rhs: list, expression: Symbol):
        self.expression = expression
        self.lhs = lhs
        self.rhs = [lhs, rhs]

    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs

    def __repr__(self):
        return str(self.lhs) + " = " + " ".join([str(s) for s in self.rhs]) + ";"


class Grammar:
    language: str
    start_symbol: Symbol
    rules: List[GrammarRule] = []  # list of GrammarRules
    symbols: Mapping[str, Symbol] = {}  # map from strings to symbols
    rule_map: Mapping[tuple, GrammarRule] # map from RHSs to the matching rules
    counter_new_symbols: int = 0          # counter to keep track of the newly created symbols

    """initialize a new grammar from a srgs grammar file"""
    def __init__(self, lines, grammar_format="SRGS"):  # FIXME: maybe implement JSGF import in the future
        assert grammar_format == "SRGS", "illegal format descriptor: {}".format(grammar_format)
        lines = [re.sub("//.*$", "", line) for line in lines]  # remove comment lines
        lines = [line.strip() for line in lines if not re.match(r"^ *$", line)]  # remove empty lines
        assert lines.pop(0).lower() == "#abnf v1.0 utf-8;", "maybe something is wrong with header?"
        lang = re.match(r"language\s+(\S*)\s*;", lines.pop(0).lower())
        assert lang and len(lang.groups()) == 1, "cannot find correct language tag: {}".format(lang)
        self.language = lang.group(0)
        for line in lines:
            match = re.match(r"((?:public)?)\s*(\$\S+)\s*=\s*(.*?)\|{?(.*?)}?\s*;", line)     # TODO: does not work for public $S = $NP $VP;
            assert match and (len(match.groups()) == 3 or len(match.groups()) == 4), "cannot parse line {}".format(line)
            is_public = match.group(1) != ""
            lhs = self.get_symbol(match.group(2))
            rhs = [self.get_symbol(s) for s in re.split(r"\s+", match.group(3))]
            expression = self.get_symbol(match.group(4))
            rule = GrammarRule(lhs, rhs, expression)
            self.rules.append(rule)
            if is_public:
                self.start_symbol = lhs
        self.normalize()
        self.build_rule_map()

    def build_rule_map(self):
        self.rule_map = defaultdict(lambda: [])
        for r in self.rules:
            self.rule_map[tuple(r.rhs)].append(r)

    def get_symbol(self, symbol: str):
        if symbol not in self.symbols:
            self.symbols[symbol] = Symbol(symbol)
        return self.symbols[symbol]

    def __repr__(self):
        return "#ABNF V1.0 utf-8\n" + \
               "language " + self.language + "\n" + \
               "\n".join([str(r) if r.lhs != self.start_symbol else "public " + str(r) for r in self.rules])

    def is_CNF(self):
        """returns weather the grammar is in Chmosky normal form"""
        for rule in self.rules:
            if len(rule.rhs) == 1 and not rule.rhs[0].terminal:         # Right hand side of the rule consists of a single Non-Terminal
                return False
            elif len(rule.rhs) == 2 and (rule.rhs[0].terminal or rule.rhs[1].terminal):         # At least one of the two symbols on the right hand side of the rule is a Terminal
                return False
            else:
                return False
        return True

    def is_relaxedCNF(self):
        """check if the grammar is in accordance to the requirements of the extended parsing algorithm,
        which allows binary rules producing only non-terminals as well as unary rules"""
        for rule in self.rules:
            if not ((len(rule.rhs) == 2 and not rule.rhs[0].terminal and not rule.rhs[1].terminal) or len(
                    rule.rhs) == 1):  # the rule produces neither 2 non-Terminals nor exactly one symbol
                return False
        return True

    def normalize(self):
        """updates rules so that they are in relaxed Chomsky normal form"""
        # remove terminals from 'mixed' (T/NT) rules by replacing each T with a new NT
        for i, rule in enumerate(self.rules):
            if len(rule.rhs) > 1:
                for j, symbol in enumerate(rule.rhs):
                    if symbol.terminal:
                        # create a helper non-terminal symbol
                        new_symbol = self.get_symbol('$H{}'.format(self.counter_new_symbols), for_normalization=True)
                        self.counter_new_symbols += 1
                        # replace the Terminal on the right hand side of the rule with the newly created non-terminal
                        self.rules[i].rhs[j] = new_symbol
                        # add an extra rule mapping the new non-terminal to the terminal it replaces
                        self.rules.append(GrammarRule(new_symbol, [symbol]))

        # split rules with more than 2 Terminals into multiple rules
        to_delete = []  # indexes of the rules that are replaced. If they were deleted in the for loop, the enumeration won't work properly
        for j, rule in enumerate(self.rules):
            if len(rule.rhs) > 2:
                lhs = rule.lhs
                for i in range(len(rule.rhs) - 2):
                    new_symbol = self.get_symbol('$H{}'.format(self.counter_new_symbols), for_normalization=True)
                    self.counter_new_symbols += 1
                    # create a new rule mapping the current left hand side (in all cases except the first iteration a helper non-terminal)
                    # to the current non-terminal on the rhs as well as a helper-non-terminal
                    self.rules.append(GrammarRule(lhs, [rule.rhs[i], new_symbol]))
                    # the new lhs is the helper non-terminal that was just created
                    lhs = new_symbol
                # handle last 2 symbols: those will be on the right hand side of the new rule, no need for another non-terminal
                self.rules.append(GrammarRule(lhs, [rule.rhs[-2], rule.rhs[-1]]))
                to_delete[:0] = [j]  # preped index
        # delete rules that have been replaced
        for j in to_delete:
            del self.rules[j]
