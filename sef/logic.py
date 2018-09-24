"""
The class which implements the actual logic for executing the language
"""

from typing import Any, List

from .nodes import *

__author__ = "Joseph Banks"


class Interpreter:
    """
    The class for interpreting sef AST
    """
    def __init__(self, ast: List[DefinitionNode]):
        self.ast = ast
        self.functions = {}

    def begin_execution(self):
        """
        The entry point for interpreting, in this method we execute
        all the function definitions so they are ready for use when
        they are called.

        We then confirm we have a main function defined with no
        arguments.

        If we do, we execute it
        """
        for item in self.ast:
            self.execute_item(item)

        if self.functions.get("main") is None:
            raise Exception("All sef files must declare one main function"
                            " with no arguments")
        elif len(self.functions.get("main").arguments) > 0:
            # We have a main function, but it is accepting arguments
            raise Exception(f"The main function takes 0 arguments, "
                            f"not {len(self.functions['main'].arguments)}.")

        # Call the main function with no arguments
        self.call_function("main", [])

    def operator_node_to_function(self, op_node):
        """
        Convert any operator nodes into functions used to perform
        the operations.
        """
        operators = {
            Operator.ADD: lambda a, b: a + b,
            Operator.SUBTRACT: lambda a, b: a - b,
            Operator.MULTIPLY: lambda a, b: a * b,
            Operator.DIVIDE: lambda a, b: a / b
        }

        return operators[op_node.value]

    def execute_math(self, expression, variables):
        # We have a mathamatical calculation
        accumulator = expression.pop(0)
        if type(accumulator) == VariableReferenceNode:
            # If the first item in the operation is a variable convert
            # it to an integer
            accumulator = variables[accumulator.value]
        else:
            # If it is not, just get the value of the IntegerNode
            accumulator = accumulator.value

        while len(expression) != 0:
            # When the expression is not of length 0 we still
            # have operations left to apply

            # Get the operator
            operator = expression.pop(0)

            # Get the operand
            value = expression.pop(0)
            if type(value) == VariableReferenceNode:
                # If the operand is a variable, convert it
                # to an integer with the variables value
                value = variables[value.value]
            else:
                # Else get the value of the IntegerNode
                value = value.value

            # Get the function for that operator
            function = self.operator_node_to_function(operator)

            # Apply the operation
            accumulator = function(accumulator, value)

        return accumulator

    def is_math_expression(self, expression):
        """
        This function checks whether we have a set of just operators, integers
        and variables, if so, we consider it a math expression
        """
        return all(
            [isinstance(x,
                [VariableReferenceNode,
                 IntegerNode,
                 OperatorNode]
                        )
             for x in expression]
        )

    def execute_item(self, item, variables={}) -> Any:
        """
        Everything that needs to be executed goes through here
        """
        if isinstance(item, DefinitionNode):
            # We have a definition, pass it to the handle_definition
            # method
            self.handle_definition(item)
        elif isinstance(item, VariableDeclarationNode):
            # If the expression is a list, we might have a math expression
            if isinstance(item.expression, list):
                # Do we have a math expression?
                if self.is_math_expression(item.expression):
                    # Execute math and store in the variable holder
                    accumulator = self.execute_math(item.expression, variables)
                    variables[item.name] = accumulator

            # Do we have a function call in a variable assignment?
            elif isinstance(item.expression, CallNode):
                arguments = []
                for expr in item.expression.arg_exprs:
                    # For every expression, execute it
                    arguments.append(self.execute_item(expr, variables))

                variables[item.name] = self.call_function(
                    item.expression.name,
                    arguments
                )
                # Store the return of the function in the variable holder
            else:
                variables[item.name] = item.expression.value
        elif isinstance(item, CallNode):
            if self.functions.get(item.name) is None:
                # Let's check if it is a Python built-in
                function = __builtins__.get(item.name)
                if callable(function):
                    arguments = []
                    for expr in item.arg_exprs:
                        arguments.append(self.execute_item(expr, variables))

                    return function(*arguments)
                else:
                    # We have no Python builtin or normal function
                    raise Exception(f"Could not find a"
                                    f" function named {item.name}")
            elif (len(self.functions.get(item.name).arguments) !=
                  len(item.arg_exprs)):
                # We have a function but the wrong number of arguments
                # have been passed
                function = self.functions.get(item.name).arguments
                raise Exception(f"There is a function called {item.name} "
                                f"but it takes "
                                f"{function}"
                                f" arguments instead of "
                                f"{len(item.arg_exprs)}")

            arguments = []
            for expr in item.arg_exprs:
                # For every expression in the argument expressions
                # exceute it and append to the list
                arguments.append(self.execute_item(expr, variables))

            # Return the return of the function call
            return self.call_function(item.name, arguments)
        elif isinstance(item, VariableReferenceNode):
            # A reference to a variable
            return variables[item.value]
        elif isinstance(item, list):
            # We have a list of expressions, might be maths?
            if self.is_math_expression(item):
                # It's maths.
                return self.execute_math(item, variables)
        else:
            # If we have no special behaviour for a node, we'll
            # try to get just the value of it (in case it mixes in off
            # the ExpressionNode class)
            value = getattr(item, "value", None)
            if value:
                return value
            raise Exception(f"No way to execute: {item}")

    def call_function(self, name: str, arguments: List) -> Any:
        """
        Execute a function defined with the language def token.
        """
        function = self.functions.get(name)

        if function is None:
            # We found no functions with that name
            raise Exception(f"Function '{name}' does not exist")

        if len(arguments) != len(function.arguments):
            # We found no function with those arguments
            raise Exception(f"The function {name} expects "
                            f"{len(function.arguments)} arguments "
                            f"but we got {len(arguments)}")

        function_variables = {}

        for i, value in enumerate(arguments):
            # Place every argument into the variables holder
            function_variables[function.arguments[i]] = value

        if isinstance(function.body, list):
            for i, item in enumerate(function.body):
                # Run every line
                ret_val = self.execute_item(item, variables=function_variables)
                if i + 1 == len(function.body):
                    # The last line is the one which is returned
                    return ret_val
        else:
            # There is only one line so return it
            return self.execute_item(function.body,
                                     variables=function_variables)

    def handle_definition(self, item):
        """
        Handle a definition, like def x() or whatever

        Adds it to the self.functions dictionary for future lookup
        when it is called
        """
        # Add the function to our functions dictionary so that
        # later in execution if we receive a call to the function we
        # can easily get the function.
        self.functions[item.name] = item
