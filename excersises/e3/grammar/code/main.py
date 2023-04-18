import grammar
import parse
import parser
import lambda_parser


def interpret(tree):
    pass

def main():
    with open("../data/example.srgs", "r") as f:
        lines = f.readlines()
        gr = grammar.Grammar(lines)
    sentence = "Noah likes expensive restaurants"
    tokens = sentence.split(" ")
    trees = parser.parse(tokens, gr)
    for tree in trees:
        print(tree.to_dot())
    try:
        tree = trees[0]
        print(lambda_parser.lambda_parse(tree))
    except IndexError as e:
        print("no trees generated")

    print()


if __name__ == "__main__":
    main()
