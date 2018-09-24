"""
The Sef tokenizer
"""

from dataclasses import dataclass
from enum import Enum
import re
from typing import List

__author__ = "Joseph Banks"

TOKENS = [
    # Functions
    ("def", r"\bdef \b"),
    ("end", r"\bend\b"),

    # Variable declarations
    ("variable_declaration", r"\b[a-zA-Z_]+\s?=\s?.+\n"),

    # Identifier
    ("identifier", r"\b[a-zA-Z_]+\b"),

    # Types
    ("integer", r"[0-9]+"),
    ("string", r"['\"][^'\"]+['\"]"),

    # Function items
    ("open_paren", r"\("),
    ("close_paren", r"\)"),
    ("comma", r","),

    # Operators
    ("add", r"\+"),
    ("subtract", r"-"),
    ("multiply", r"\*"),
    ("divide", r"\/")
]


class TokenType(Enum):
    """
    The various types a token can be
    """
    DEF = 0
    END = 1
    VARIABLE_DECLARATION = 2
    IDENTIFIER = 3
    INTEGER = 4
    STRING = 5
    OPEN_PAREN = 6
    CLOSE_PAREN = 7
    COMMA = 8
    ADD = 9
    SUBTRACT = 10
    MULTIPLY = 11
    DIVIDE = 12


@dataclass
class Token:
    """
    Value used to represent a token
    """
    type: TokenType
    value: str


class Tokenizer:
    """
    The tokenizer used for converting sef into tokens
    """

    def __init__(self, code):
        # Strip whitespace from the left
        self.code = code.lstrip()

    def tokenize_code(self) -> List[Token]:
        """
        Tokenize the code in self.code
        """
        tokens = []

        # When we process a token we remove the token from the
        # source code, so when it is empty we know to stop
        while self.code != "":
            # Add the next token to the list
            tokens.append(self.tokenize_next())

            # Strip the left side of whitespace, this is so the
            # regexes match and so the variable declaration matcher can
            # have an entire line to itself
            self.code = self.code.lstrip()
        return tokens

    def tokenize_next(self) -> Token:
        """
        Take a look at the next token in the code
        and convert it into a token class
        """
        for token_type, token_re in TOKENS:
            # Wrap the entire token regex in a \A so we know
            # we are at the start of the string
            regex = r"\A(" + token_re + ")"
            match = re.match(regex, self.code)
            # Did this token match the regex?
            if match:
                # Get the full value of the token
                value = match.groups()[0]
                # Remove the token from the head of the source code
                self.code = self.code[len(value):]

                # Return a new Token class
                return Token(getattr(TokenType, token_type.upper()), value)

        # If we got to here, no regexes matched so we went wrong somewhere
        raise Exception(f"No valid tokens found for: '{self.code}'")
