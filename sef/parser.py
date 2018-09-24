"""
The Sef parser

This interprets the tokens generated and converts
it into a nicer machine readable format.
"""

import re
from typing import List

from .token import Tokenizer, TokenType, Token
from .nodes import *

__author__ = "Joseph Banks"


class Parser:
    """
    Sef parser class
    """
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def peek(self, expected_type: TokenType, offset: int = 0):
        """
        Peek for a type and confirm it is one we are expecting
        """
        try:
            # Is the next token (or the next token at the offset)
            # the type we are expecting?
            return self.tokens[offset].type == expected_type
        except IndexError:
            # End of code
            return False

    def consume(self, expected_type: TokenType):
        """
        Consume a type, pop it's value
        """
        # Remove the token from the head of the token list
        token = self.tokens.pop(0)

        # Is it the type we want?
        if token.type != expected_type:
            raise Exception(f"Looking for type {expected_type} "
                            f"but found {token.type}")

        return token

    def parse(self):
        """
        The entry point to the beginning of parsing
        """
        definitions = []

        # While we can still see new definitions we want to keep
        # parsing the definitions
        while self.peek(TokenType.DEF):
            # Add the definition to the definition list
            definitions.append(self.parse_definition())

        return definitions

    def parse_definition(self):
        """
        Parse the definitions of functions
        """
        # Consume the def
        self.consume(TokenType.DEF)

        # Consume the name of the function
        name = self.consume(TokenType.IDENTIFIER).value

        # Get the names of the arguments
        arguments = self.parse_argument_names()

        # Parse the body expression
        body = self.parse_expr()

        # Consume the ending token
        self.consume(TokenType.END)

        # Return a new definition node for the function
        return DefinitionNode(name, arguments, body)

    def is_operator_next(self):
        """
        A helper to check if an operator is next.
        """
        operators = [
            TokenType.ADD,
            TokenType.SUBTRACT,
            TokenType.DIVIDE,
            TokenType.MULTIPLY
        ]
        # Are any of the next tokens operators?
        return any([self.peek(operator) for operator in operators])

    def parse_expr(self, function_call: bool = False, n: int = -1):
        """
        Parse an expression, all sorts of things
        1 + 2, memes(), y = x
        """

        items = []

        # Used in the loop to see if we are finished
        finished = False

        # If we want to parse n tokens then we need
        # to know how many tokens there were before
        start_len = len(self.tokens)

        while not finished:
            if self.peek(TokenType.INTEGER):
                # Parse an integer
                items.append(self.parse_integer())
            elif self.peek(TokenType.STRING):
                # Parse a string
                items.append(self.parse_string())
            elif self.is_operator_next():
                # Parse a mathematical operator
                items.append(self.parse_operator())
            elif (self.peek(TokenType.IDENTIFIER) and
                    self.peek(TokenType.OPEN_PAREN, 1)):
                # Parse a function call, this is called if we have an
                # identifier immediately before us AND an opening bracket
                # immediately after, for example: identifier( is the start
                # of a function call
                items.append(self.parse_call())
            elif self.peek(TokenType.VARIABLE_DECLARATION):
                # Parse a variable declaration, like x = y
                items.append(self.parse_variable_declaration())
            elif self.peek(TokenType.IDENTIFIER):
                # Parse any idenifier into a variable reference
                items.append(self.parse_variable_reference())
            else:
                raise Exception(f"Invalid token type: {self.tokens[0]}")

            if start_len - len(self.tokens) == n:
                # We have parsed n tokens so we should break from
                # the loop
                break

            if function_call:
                # If we are in a function call and we see the symbols for
                # the end of the arguments, we should stop
                if (self.peek(TokenType.COMMA) or
                        self.peek(TokenType.CLOSE_PAREN)):
                    finished = True
            else:
                if self.peek(TokenType.END):
                    # If we see the end token of
                    # a definition, we should stop
                    finished = True

        # Return a list of things, [node, node2, node3] if there are
        # more than 1 things, or just return node if there is one
        return items if len(items) > 1 else items[0]

    def parse_variable_reference(self):
        """
        Parse the reference to a variable
        """
        # Parse an identifier into a variable reference
        ident = self.consume(TokenType.IDENTIFIER).value
        return VariableReferenceNode(ident)

    def parse_variable_declaration(self):
        """
        Parse the declaration of a variable, like:

        s = 1 + 3 - abc()
        """
        var_dec = self.consume(TokenType.VARIABLE_DECLARATION).value
        # The tokenizer leaves the body as raw for us so we have
        # access to any tokens that may lie in it
        match = re.match(r"\b([a-zA-Z_]+)\s?=\s?(.+)\n", var_dec)

        # Name of the variable
        name = match.groups()[0]

        # The expression which the variable is equal to
        expression = match.groups()[1]

        # Create a new tokenizer for the variable
        tokenizer = Tokenizer(expression)

        # Tokenize the variable body
        tokens = tokenizer.tokenize_code()

        # Add the tokens onto the head of the token list
        self.tokens = tokens + self.tokens

        # Parse the next X tokens into nodes of AST
        # for the body of the variable
        body = self.parse_expr(n=len(tokens))

        return VariableDeclarationNode(name, body)

    def parse_call(self):
        """
        Parse a function call into a CallNode, like:

        xy(a, b, c)
        """
        # Get the name of the called function
        name = self.consume(TokenType.IDENTIFIER).value
        # Get rid of the (
        self.consume(TokenType.OPEN_PAREN)

        # Parse the arguments
        argument_expressions = self.parse_argument_expressions()

        # Get rid of the )
        self.consume(TokenType.CLOSE_PAREN)

        return CallNode(name, argument_expressions)

    def parse_argument_expressions(self):
        """
        Parse arguments given to a function
        """
        expressions = []
        # Until we have a ) next, keep parsing
        while not self.peek(TokenType.CLOSE_PAREN):
            # Parse one argument
            expressions.append(self.parse_expr(function_call=True))
            # If there is a , after that, continue parsing
            # to the next argument
            while self.peek(TokenType.COMMA):
                # Consume the comma
                self.consume(TokenType.COMMA)
                # Parse the expression in the argument
                expressions.append(self.parse_expr(function_call=True))

        return expressions

    def parse_operator(self):
        """
        Parse any mathematical operator into an OperatorNode
        """
        if self.peek(TokenType.ADD):
            # If it is an add, consume a +
            type_ = OperatorNode(Operator.ADD)
            self.consume(TokenType.ADD)
        elif self.peek(TokenType.SUBTRACT):
            # If it is a subtract, consume a -
            type_ = OperatorNode(Operator.SUBTRACT)
            self.consume(TokenType.SUBTRACT)
        elif self.peek(TokenType.DIVIDE):
            # If it is a divide, consume a /
            type_ = OperatorNode(Operator.DIVIDE)
            self.consume(TokenType.DIVIDE)
        elif self.peek(TokenType.MULTIPLY):
            # If it is a multiply, consume a *
            type_ = OperatorNode(Operator.MULTIPLY)
            self.consume(TokenType.MULTIPLY)

        # Return the operator node
        return type_

    def parse_string(self):
        """
        Parse a string token into a StringNode
        """
        # Grab the value of the string token
        val = self.consume(TokenType.STRING).value

        # Remove the double/single quotes before and after the string
        match = re.match(r"['\"]([^'\"]+)['\"]", val)

        # Construct a new StringNode with the first element of the match
        return StringNode(match.groups()[0])

    def parse_integer(self):
        """
        Parse an integer token into an IntegerNode
        """
        # Simplest of them all, get the value of the token and int() it
        return IntegerNode(int(self.consume(TokenType.INTEGER).value))

    def parse_argument_names(self):
        """
        Parse the arguments given to a function during definition
        """
        arg_names = []

        # Consume the (
        self.consume(TokenType.OPEN_PAREN)

        if self.peek(TokenType.IDENTIFIER):
            # If we see any argument identifiers, start parsing

            # Parse an identifier and append to the arg_names list
            arg_names.append(self.consume(TokenType.IDENTIFIER).value)

            # As long as we see commas, keep on parsing
            while self.peek(TokenType.COMMA):
                # Consume the ,
                self.consume(TokenType.COMMA)

                # Add to the arg_names list
                arg_names.append(self.consume(TokenType.IDENTIFIER).value)

        # Consume the )
        self.consume(TokenType.CLOSE_PAREN)

        # Return a list of argument names
        return arg_names
