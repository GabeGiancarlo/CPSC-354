#!/usr/bin/env python3
"""
Calculator implementation using Lark parser generator.
This module implements a calculator that can evaluate mathematical expressions
with proper operator precedence and support for various operations.
"""

import sys
from lark import Lark, Transformer


class CalculatorTransformer(Transformer):
    """
    Transformer class that converts the parsed AST into Python values.
    This class handles the evaluation of mathematical expressions by
    recursively processing the abstract syntax tree.
    """
    
    def add(self, items):
        """Handle addition operation."""
        return items[0] + items[1]
    
    def sub(self, items):
        """Handle subtraction operation."""
        return items[0] - items[1]
    
    def mul(self, items):
        """Handle multiplication operation."""
        return items[0] * items[1]
    
    def pow(self, items):
        """Handle exponentiation operation (right-associative)."""
        return items[0] ** items[1]
    
    def neg(self, items):
        """Handle unary negation."""
        return -items[0]
    
    def number(self, items):
        """Convert string number to float."""
        return float(items[0])
    
    def log(self, items):
        """Handle logarithm operation: log base of number."""
        import math
        return math.log(items[0], items[1])
    
    def parens(self, items):
        """Handle parentheses - just return the inner expression."""
        return items[0]


def create_parser():
    """
    Create and return a Lark parser instance.
    Loads the grammar from grammar.lark file and returns a configured parser.
    """
    with open('grammar.lark', 'r') as f:
        grammar = f.read()
    
    return Lark(grammar, parser='lalr', transformer=CalculatorTransformer(), start='start')


def evaluate_expression(expression):
    """
    Evaluate a mathematical expression string.
    
    Args:
        expression (str): The mathematical expression to evaluate
        
    Returns:
        float: The result of the expression evaluation
        
    Raises:
        Exception: If the expression cannot be parsed or evaluated
    """
    parser = create_parser()
    try:
        tree = parser.parse(expression)
        # The tree is wrapped in a 'start' node, so we need to extract the value
        return tree.children[0]
    except Exception as e:
        raise Exception(f"Error parsing expression '{expression}': {e}")


def main():
    """
    Main function that handles command line input and evaluates expressions.
    Reads expression from command line argument and prints the result.
    """
    if len(sys.argv) != 2:
        print("Usage: python calculator_cfg.py \"expression\"")
        sys.exit(1)
    
    expression = sys.argv[1]
    
    try:
        result = evaluate_expression(expression)
        # Print as integer if it's a whole number, otherwise as float
        if result == int(result):
            print(int(result))
        else:
            print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

