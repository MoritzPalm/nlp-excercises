import grammar
import parse
import parser

if __name__ == "__main__":
    with open("../data/telescope.srgs", "r") as f:
        lines = f.readlines()
        gr = grammar.Grammar(lines)
    sentence = "I saw the duck with a telescope"
    tokens = sentence.split(" ")
    trees = parser.parse(tokens, gr)
    for tree in trees:
        print(tree.to_dot())
    assert repr(parser.example_telescope_parse()) in map(repr, trees)