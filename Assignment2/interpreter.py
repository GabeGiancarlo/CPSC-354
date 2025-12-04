#!/usr/bin/env python3
"""
Lambda Calculus Interpreter with Normalizing Evaluation Strategy.
This interpreter uses normal order evaluation (call-by-name) to ensure
that expressions are reduced to normal form when possible.
"""

import sys
from lark import Lark, Transformer, Tree


class LambdaTransformer(Transformer):
    """Transforms parsed AST into lambda calculus expression trees."""
    
    def start(self, items):
        return items[0]
    
    def exp(self, items):
        return items[0]
    
    def application(self, items):
        # Application: (func arg)
        return ('app', items[0], items[1])
    
    def abstraction(self, items):
        # Abstraction: \x.body or λx.body
        # items[0] is already a variable node tuple ('var', name)
        var_name = items[0][1] if isinstance(items[0], tuple) else items[0]
        return ('abs', var_name, items[1])
    
    def variable(self, items):
        # Variable: just the name
        # items[0] is a Token, extract its value
        var_name = items[0].value if hasattr(items[0], 'value') else items[0]
        return ('var', var_name)


def fresh_variable(used_vars):
    """Generate a fresh variable name that doesn't conflict with used variables."""
    counter = 1
    while True:
        candidate = f"Var{counter}"
        if candidate not in used_vars:
            return candidate
        counter += 1


def free_variables(expr):
    """Return the set of free variables in an expression."""
    if expr[0] == 'var':
        return {expr[1]}
    elif expr[0] == 'abs':
        # Free vars = free vars of body minus the bound variable
        return free_variables(expr[2]) - {expr[1]}
    elif expr[0] == 'app':
        # Free vars = union of free vars of function and argument
        return free_variables(expr[1]) | free_variables(expr[2])
    return set()


def substitute(expr, var_name, replacement):
    """
    Perform capture-avoiding substitution: expr[var_name := replacement]
    Returns a new expression with all free occurrences of var_name replaced by replacement.
    """
    if expr[0] == 'var':
        if expr[1] == var_name:
            return replacement
        else:
            return expr
    elif expr[0] == 'abs':
        bound_var = expr[1]
        body = expr[2]
        
        if bound_var == var_name:
            # Variable is bound, no substitution needed
            return expr
        else:
            # Check if we need to rename to avoid capture
            free_in_replacement = free_variables(replacement)
            if bound_var in free_in_replacement:
                # Need to rename the bound variable
                used_vars = free_variables(replacement) | free_variables(body) | {var_name}
                new_var = fresh_variable(used_vars)
                # Rename bound variable in body
                new_body = substitute(body, bound_var, ('var', new_var))
                # Now substitute in the renamed body
                new_body = substitute(new_body, var_name, replacement)
                return ('abs', new_var, new_body)
            else:
                # Safe to substitute directly
                new_body = substitute(body, var_name, replacement)
                return ('abs', bound_var, new_body)
    elif expr[0] == 'app':
        # Substitute in both function and argument
        new_func = substitute(expr[1], var_name, replacement)
        new_arg = substitute(expr[2], var_name, replacement)
        return ('app', new_func, new_arg)
    
    return expr


def is_redex(expr):
    """Check if an expression is a redex (reducible expression)."""
    return expr[0] == 'app' and expr[1][0] == 'abs'


def reduce_redex(expr):
    """
    Reduce the leftmost outermost redex in the expression.
    Returns (new_expr, reduced) where reduced is True if a reduction occurred.
    Uses normal order evaluation: leftmost outermost redex first.
    """
    # If this is a redex, reduce it
    if is_redex(expr):
        # This is a redex: (\x.body) arg
        func = expr[1]  # The abstraction
        arg = expr[2]   # The argument
        bound_var = func[1]  # The bound variable
        body = func[2]  # The body of the abstraction
        
        # Perform beta-reduction: substitute arg for bound_var in body
        new_expr = substitute(body, bound_var, arg)
        return (new_expr, True)
    
    # Otherwise, recursively look for redexes
    if expr[0] == 'app':
        # In normal order: try function part first (leftmost)
        new_func, reduced = reduce_redex(expr[1])
        if reduced:
            return (('app', new_func, expr[2]), True)
        # If function is in normal form, try argument part
        new_arg, reduced = reduce_redex(expr[2])
        if reduced:
            return (('app', expr[1], new_arg), True)
    
    elif expr[0] == 'abs':
        # Try to reduce in body
        new_body, reduced = reduce_redex(expr[2])
        if reduced:
            return (('abs', expr[1], new_body), True)
    
    return (expr, False)


def evaluate(expr):
    """
    Evaluate expression to normal form using normal order evaluation.
    Normal order: always reduce the leftmost outermost redex.
    """
    while True:
        # Try to find and reduce a redex
        new_expr, reduced = reduce_redex(expr)
        if not reduced:
            # No more reductions possible - we're in normal form
            return expr
        expr = new_expr


def linearize(expr):
    """
    Convert expression tree back to string representation.
    Follows lambda calculus conventions for parentheses.
    """
    if expr[0] == 'var':
        return expr[1]
    elif expr[0] == 'abs':
        body_str = linearize(expr[2])
        return f"\\{expr[1]}.{body_str}"
    elif expr[0] == 'app':
        func_str = linearize(expr[1])
        arg_str = linearize(expr[2])
        
        # Add parentheses around function if it's an abstraction
        if expr[1][0] == 'abs':
            func_str = f"({func_str})"
        
        # Add parentheses around argument if it's an application or abstraction
        if expr[2][0] == 'app' or expr[2][0] == 'abs':
            arg_str = f"({arg_str})"
        
        return f"{func_str} {arg_str}"


def create_parser():
    """Create and return a Lark parser instance."""
    with open('grammar.lark', 'r') as f:
        grammar = f.read()
    
    return Lark(grammar, parser='lalr', transformer=LambdaTransformer(), start='start')


def main():
    """Main function that handles command line input and evaluates expressions."""
    if len(sys.argv) != 2:
        sys.exit(1)
    
    expression = sys.argv[1]
    
    try:
        parser = create_parser()
        tree = parser.parse(expression)
        result = evaluate(tree)
        output = linearize(result)
        print(output)
    except Exception as e:
        sys.exit(1)


if __name__ == "__main__":
    main()

