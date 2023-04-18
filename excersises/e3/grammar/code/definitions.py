from lambda_grammar import Variable, Abstraction, Application
import itertools


# inspired heavily from pythons ast module
class NodeVisitor(object):
    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method)
        return visitor(node)


# "subclassing" the NodeVisitor class and keeping the ast conventions
class FreeVariables(NodeVisitor):
    def visit_variable(self, node):
        return {node.name}

    def visit_application(self, node):
        return (self.visit(node.left_expression) |
                self.visit(node.right_expression))

    def visit_abstraction(self, node):
        return self.visit(node.body) - self.visit(node.parameter)


class BoundVariables(NodeVisitor):
    def visit_variable(self, node):
        return set()

    def visit_application(self, node):
        return (self.visit(node.left_expression) |
                self.visit(node.right_expression))

    def visit_abstraction(self, node):
        return self.visit(node.body) | {node.parameter.name}


class AlphaConversion(NodeVisitor):
    def __init__(self, to_replace, replacement):
        self.to_replace = to_replace
        self.replacement = replacement

    def visit_variable(self, node):
        if node.name == self.to_replace.name:
            return self.replacement
        else:
            return Variable(node.name)

    def visit_application(self, node):
        return Application(self.visit(node.left_expression), self.visit(node.right_expression))

    def visit_abstraction(self, node):
        if node.parameter.name in FreeVariables().visit(self.replacement):
            # name conflict with bound variable
            unavailable_names = (FreeVariables().visit(node) |
                                 {node.parameter.name})
            new_name = next(s for s in lexicographical()
                            if s not in unavailable_names)
            new_parameter = Variable(new_name)
            converter = AlphaConversion(node.parameter, new_parameter)
            new_body = converter.visit(node.body)
            return Abstraction(new_parameter, self.visit(new_body))
        else:
            return Abstraction(self.visit(node.parameter),
                               self.visit(node.body))


def lexicographical():
    """All alphabetic strings in lexicographical order."""
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for size in itertools.count(1):
        for string in itertools.product(alphabet, repeat=size):
            yield ''.join(string)


class BetaReduction(NodeVisitor):

    def __init__(self):
        self.reduced = False

    def visit_variable(self, node):
        return Variable(node.name)

    def visit_application(self, node):
        if (isinstance(node.left_expression, Abstraction) and
                not self.reduced):
            self.reduced = True
            converter = AlphaConversion(node.left_expression.parameter,
                                        node.right_expression)
            return converter.visit(node.left_expression.body)
        else:
            return Application(self.visit(node.left_expression),
                               self.visit(node.right_expression))

    def visit_abstraction(self, node):
        return Abstraction(self.visit(node.left_expression), self.visit(node.right_expression))
