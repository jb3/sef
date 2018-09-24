from prettyprinter import cpprint

from sef import token, parser, logic


CODE = """
def main()
    username = get_input("Enter your username: ")
    print("Welcome back", username)
end

def get_input(prompt)
    input(prompt)
end
"""

tokenizer = token.Tokenizer(CODE)
tokens = tokenizer.tokenize_code()

parser_ = parser.Parser(tokens)
ast = parser_.parse()

interpreter = logic.Interpreter(ast)
interpreter.begin_execution()
