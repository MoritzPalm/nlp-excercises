# names and grammer taken from here: https://pages.cs.wisc.edu/~horwitz/CS704-NOTES/1.LAMBDA-CALCULUS.html#NOR

class Expression(object):
    def children(self):
        pass


class Variable(Expression):
    def __init__(self, name):
        self.name = name

    def __str_(self):
        return self.name

    def children(self):
        return []


class Application(Expression):
    def __init__(self, left_expression, right_expression):
        self.left_expression = left_expression
        self.right_expression = right_expression

    def __str__(self):
        return u'({} {}'.format(self.left_expression, self.right_expression)

    def children(self):
        return [self.left_expression, self.right_expression]


class Abstraction(Expression):
    def __init__(self, parameter, body):
        self.parameter = parameter
        self.body = body

    def __str__(self):
        return u'λ{}.{}'.format(self.parameter, self.body)

    def children(self):
        return [self.parameter, self.body]
