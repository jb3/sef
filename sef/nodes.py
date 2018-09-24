"""
Nodes used for parsing
"""

from dataclasses import dataclass
from enum import Enum

__author__ = "Joseph Banks"

__all__ = ["Operator", "ExpressionNode", "DefinitionNode",
           "CallNode", "StringNode", "IntegerNode",
           "VariableReferenceNode", "OperatorNode",
           "VariableDeclarationNode"]

class Operator(Enum):
    """
    Various types for OperatorNode
    """
    ADD = 0
    SUBTRACT = 1
    DIVIDE = 2
    MULTIPLY = 3


@dataclass
class ExpressionNode:
    """
    Node for any type of expression
    """
    value: str


@dataclass
class DefinitionNode:
    """
    A function definition like:

    def x(a, b, c)
        a + b + c
    end
    """
    name: str
    arguments: list
    body: list  # List of ExpressionNodes


@dataclass
class CallNode:
    """
    A function call like:

    x(1, 2, three())
    """
    name: str
    arg_exprs: list


class StringNode(ExpressionNode):
    """
    A string node like:

    "hello world"
    """
    pass


class IntegerNode(ExpressionNode):
    """
    An integer like:

    1
    """
    pass


class VariableReferenceNode(ExpressionNode):
    """
    A node which references a variable, in this case
    the value parameter of the ExpressionNode mixin
    will be equivalent to the name of the variable
    """
    pass


class OperatorNode(ExpressionNode):
    """
    An operator such as + or -
    """
    pass


@dataclass
class VariableDeclarationNode:
    """
    A declaration of a variable such as:

    a = 1 + 2
    """
    name: str
    expression: ExpressionNode
