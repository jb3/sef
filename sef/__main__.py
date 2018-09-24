"""
The Sef interpreter.
"""

import sys

from sef.token import Tokenizer
from sef.parser import Parser
from sef.logic import Interpreter

__author__ = "Joseph Banks"

if __name__ == "__main__":
    path = sys.argv[1]

    with open(path, "r") as f:
        contents = f.read()

    tokenizer = Tokenizer(contents)
    tokens = tokenizer.tokenize_code()

    parser = Parser(tokens)
    ast = parser.parse()

    interpreter = Interpreter(ast)
    interpreter.begin_execution()
