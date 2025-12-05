#!/usr/bin/env python3
"""
Lambda Calculus Interpreter with Arithmetic Operations.
This interpreter uses lazy evaluation (call-by-name) and does not reduce under lambda.
"""

import sys
from lark import Lark, Transformer


class LambdaCalculusTransformer(Transformer):
    """Transforms parsed AST into lambda calculus expression trees."""
    
    def start(self, items):
        return items[0]
    
    def exp(self, items):
        return items[0]
    
    def addsub(self, items):
        if len(items) == 1:
            return items[0]
        return items[0]  # Should not reach here with named rules
    
    def plus(self, items):
        return ('plus', items[0], items[1])
    
    def minus(self, items):
        return ('minus', items[0], items[1])
    
    def muldiv(self, items):
        if len(items) == 1:
            return items[0]
        return items[0]  # Should not reach here with named rules
    
    def times(self, items):
        return ('times', items[0], items[1])
    
    def div(self, items):
        return ('div', items[0], items[1])
    
    def unary(self, items):
        if len(items) == 1:
            return items[0]
        return items[0]  # Should not reach here with named rules
    
    def neg(self, items):
        # items[0] is the NEG token, items[1] is the expression being negated
        return ('neg', items[1])
    
    def application(self, items):
        if len(items) == 1:
            return items[0]
        # Application: left-associative
        result = items[0]
        for item in items[1:]:
            result = ('app', result, item)
        return result
    
    def atom(self, items):
        return items[0]
    
    def abstraction(self, items):
        # Abstraction: \x.body or λx.body
        var_name = items[0].value if hasattr(items[0], 'value') else items[0]
        return ('abs', var_name, items[1])
    
    def number(self, items):
        # Number: convert to float
        num_str = items[0].value if hasattr(items[0], 'value') else str(items[0])
        return ('num', float(num_str))
    
    def variable(self, items):
        # Variable: just the name
        var_name = items[0].value if hasattr(items[0], 'value') else items[0]
        return ('var', var_name)
    
    def NAME(self, token):
        return token


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
    elif expr[0] in ('plus', 'minus', 'times', 'div', 'neg'):
        # Arithmetic operations: collect free vars from operands
        if expr[0] == 'neg':
            return free_variables(expr[1])
        else:
            return free_variables(expr[1]) | free_variables(expr[2])
    elif expr[0] == 'num':
        return set()
    return set()


def substitute(expr, var_name, replacement):
    """
    Perform capture-avoiding substitution: expr[var_name := replacement]
    Returns a new expression with all free occurrences of var_name replaced by replacement.
    Uses lazy evaluation: replacement is not evaluated before substitution.
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
    elif expr[0] == 'plus':
        return ('plus', substitute(expr[1], var_name, replacement), 
                substitute(expr[2], var_name, replacement))
    elif expr[0] == 'minus':
        return ('minus', substitute(expr[1], var_name, replacement), 
                substitute(expr[2], var_name, replacement))
    elif expr[0] == 'times':
        return ('times', substitute(expr[1], var_name, replacement), 
                substitute(expr[2], var_name, replacement))
    elif expr[0] == 'div':
        return ('div', substitute(expr[1], var_name, replacement), 
                substitute(expr[2], var_name, replacement))
    elif expr[0] == 'neg':
        return ('neg', substitute(expr[1], var_name, replacement))
    elif expr[0] == 'num':
        return expr
    
    return expr


def is_numeric(expr):
    """Check if an expression is a numeric value."""
    return expr[0] == 'num'


def get_numeric_value(expr):
    """Get the numeric value from an expression. Assumes is_numeric(expr) is True."""
    return expr[1]


def is_redex(expr):
    """Check if an expression is a redex (reducible expression)."""
    return expr[0] == 'app' and expr[1][0] == 'abs'


def reduce_redex(expr):
    """
    Reduce the leftmost outermost redex in the expression.
    Returns (new_expr, reduced) where reduced is True if a reduction occurred.
    Uses lazy evaluation: does not evaluate arguments before substitution.
    Does not reduce under lambda.
    """
    # If this is a redex, reduce it (lazy: don't evaluate argument)
    if is_redex(expr):
        # This is a redex: (\x.body) arg
        func = expr[1]  # The abstraction
        arg = expr[2]   # The argument (not evaluated - lazy!)
        bound_var = func[1]  # The bound variable
        body = func[2]  # The body of the abstraction
        
        # Perform beta-reduction: substitute arg for bound_var in body
        # Lazy: arg is substituted as-is, not evaluated first
        new_expr = substitute(body, bound_var, arg)
        return (new_expr, True)
    
    # Otherwise, recursively look for redexes
    # But do NOT reduce under lambda (lazy evaluation requirement)
    # With lazy evaluation (call-by-name), we only reduce the leftmost outermost redex
    # We don't reduce arguments unless they're being applied
    if expr[0] == 'app':
        # In normal order: try function part first (leftmost)
        # Only reduce the function part if it's not already a redex
        new_func, reduced = reduce_redex(expr[1])
        if reduced:
            return (('app', new_func, expr[2]), True)
        # With lazy evaluation, we don't reduce arguments unless the function is an abstraction
        # Since we already checked that this is not a redex, the function is not an abstraction
        # So we don't reduce the argument
    
    # Do NOT reduce under lambda - this is the key lazy evaluation requirement
    # elif expr[0] == 'abs':
    #     # Skip - we don't reduce under lambda
    
    # Handle arithmetic operations
    elif expr[0] == 'plus':
        # Evaluate arithmetic when both operands are numeric
        left, left_reduced = reduce_redex(expr[1])
        if left_reduced:
            return (('plus', left, expr[2]), True)
        right, right_reduced = reduce_redex(expr[2])
        if right_reduced:
            return (('plus', expr[1], right), True)
        # If both are numeric, we can evaluate (but this is done in evaluate function)
    
    elif expr[0] == 'minus':
        left, left_reduced = reduce_redex(expr[1])
        if left_reduced:
            return (('minus', left, expr[2]), True)
        right, right_reduced = reduce_redex(expr[2])
        if right_reduced:
            return (('minus', expr[1], right), True)
    
    elif expr[0] == 'times':
        left, left_reduced = reduce_redex(expr[1])
        if left_reduced:
            return (('times', left, expr[2]), True)
        right, right_reduced = reduce_redex(expr[2])
        if right_reduced:
            return (('times', expr[1], right), True)
    
    elif expr[0] == 'div':
        left, left_reduced = reduce_redex(expr[1])
        if left_reduced:
            return (('div', left, expr[2]), True)
        right, right_reduced = reduce_redex(expr[2])
        if right_reduced:
            return (('div', expr[1], right), True)
    
    elif expr[0] == 'neg':
        operand, reduced = reduce_redex(expr[1])
        if reduced:
            return (('neg', operand), True)
    
    return (expr, False)


def evaluate(expr):
    """
    Evaluate expression to normal form using lazy evaluation (call-by-name).
    Lazy evaluation: arguments are not evaluated when substituted.
    Does not reduce under lambda.
    """
    while True:
        # Try to find and reduce a redex
        new_expr, reduced = reduce_redex(expr)
        if not reduced:
            # Try to evaluate arithmetic operations if both operands are numeric
            new_expr = evaluate_arithmetic(expr)
            if new_expr == expr:
                # No more reductions possible - we're in normal form
                return expr
            expr = new_expr
        else:
            expr = new_expr


def evaluate_arithmetic(expr):
    """
    Evaluate arithmetic operations when both operands are numeric.
    This is called after we can't reduce any more redexes.
    """
    if expr[0] == 'plus':
        left = evaluate_arithmetic(expr[1])
        right = evaluate_arithmetic(expr[2])
        if is_numeric(left) and is_numeric(right):
            return ('num', get_numeric_value(left) + get_numeric_value(right))
        return ('plus', left, right)
    
    elif expr[0] == 'minus':
        left = evaluate_arithmetic(expr[1])
        right = evaluate_arithmetic(expr[2])
        if is_numeric(left) and is_numeric(right):
            return ('num', get_numeric_value(left) - get_numeric_value(right))
        return ('minus', left, right)
    
    elif expr[0] == 'times':
        left = evaluate_arithmetic(expr[1])
        right = evaluate_arithmetic(expr[2])
        if is_numeric(left) and is_numeric(right):
            return ('num', get_numeric_value(left) * get_numeric_value(right))
        return ('times', left, right)
    
    elif expr[0] == 'div':
        left = evaluate_arithmetic(expr[1])
        right = evaluate_arithmetic(expr[2])
        if is_numeric(left) and is_numeric(right):
            return ('num', get_numeric_value(left) / get_numeric_value(right))
        return ('div', left, right)
    
    elif expr[0] == 'neg':
        operand = evaluate_arithmetic(expr[1])
        if is_numeric(operand):
            return ('num', -get_numeric_value(operand))
        return ('neg', operand)
    
    elif expr[0] == 'app':
        # Don't evaluate applications here - that's handled by reduce_redex
        return expr
    
    elif expr[0] == 'abs':
        # Don't evaluate under lambda
        return expr
    
    # Variables and numbers are already in normal form
    return expr


def linearize(expr):
    """
    Convert expression tree back to string representation.
    Follows lambda calculus conventions for parentheses.
    """
    if expr[0] == 'var':
        return expr[1]
    elif expr[0] == 'abs':
        body_str = linearize(expr[2])
        # Add parentheses around body if it's an application
        if expr[2][0] == 'app':
            body_str = f"({body_str})"
        return f"\\{expr[1]}.{body_str}"
    elif expr[0] == 'num':
        # Format as float, removing unnecessary .0
        val = expr[1]
        if val == int(val):
            return str(int(val)) + ".0"
        return str(val)
    elif expr[0] == 'app':
        func_str = linearize(expr[1])
        arg_str = linearize(expr[2])
        
        # Add parentheses around function if it's an abstraction
        if expr[1][0] == 'abs':
            func_str = f"({func_str})"
        
        # Add parentheses around argument if it's an application, abstraction, or arithmetic
        if expr[2][0] in ('app', 'abs', 'plus', 'minus', 'times', 'div', 'neg'):
            arg_str = f"({arg_str})"
        
        result = f"{func_str} {arg_str}"
        # If function is a variable and we're at top level, might need outer parentheses
        # But let's not add them automatically - only if needed for correctness
        return result
    elif expr[0] == 'plus':
        left_str = linearize(expr[1])
        right_str = linearize(expr[2])
        # Add parentheses if needed
        if expr[1][0] in ('plus', 'minus', 'times', 'div', 'neg', 'app', 'abs'):
            left_str = f"({left_str})"
        if expr[2][0] in ('plus', 'minus', 'times', 'div', 'neg', 'app', 'abs'):
            right_str = f"({right_str})"
        return f"{left_str} + {right_str}"
    elif expr[0] == 'minus':
        left_str = linearize(expr[1])
        right_str = linearize(expr[2])
        # Add parentheses if needed
        if expr[1][0] in ('plus', 'minus', 'times', 'div', 'neg', 'app', 'abs'):
            left_str = f"({left_str})"
        if expr[2][0] in ('plus', 'minus', 'times', 'div', 'neg', 'app', 'abs'):
            right_str = f"({right_str})"
        return f"{left_str} - {right_str}"
    elif expr[0] == 'times':
        left_str = linearize(expr[1])
        right_str = linearize(expr[2])
        # Add parentheses if needed
        if expr[1][0] in ('plus', 'minus', 'div', 'neg', 'app', 'abs'):
            left_str = f"({left_str})"
        if expr[2][0] in ('plus', 'minus', 'div', 'neg', 'app', 'abs'):
            right_str = f"({right_str})"
        return f"{left_str} * {right_str}"
    elif expr[0] == 'div':
        left_str = linearize(expr[1])
        right_str = linearize(expr[2])
        # Add parentheses if needed
        if expr[1][0] in ('plus', 'minus', 'times', 'div', 'neg', 'app', 'abs'):
            left_str = f"({left_str})"
        if expr[2][0] in ('plus', 'minus', 'times', 'div', 'neg', 'app', 'abs'):
            right_str = f"({right_str})"
        return f"{left_str} / {right_str}"
    elif expr[0] == 'neg':
        operand_str = linearize(expr[1])
        # Add parentheses if operand is not atomic
        if expr[1][0] not in ('var', 'num'):
            operand_str = f"({operand_str})"
        return f"-{operand_str}"
    
    return str(expr)


def create_parser():
    """Create and return a Lark parser instance."""
    with open('grammar.lark', 'r') as f:
        grammar = f.read()
    
    return Lark(grammar, parser='lalr', transformer=LambdaCalculusTransformer(), start='start')


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
        # Add parentheses around output if it's a lambda or application (for consistency with expected format)
        if result[0] in ('abs', 'app'):
            output = f"({output})"
        print(output)
    except Exception as e:
        sys.exit(1)


if __name__ == "__main__":
    main()
