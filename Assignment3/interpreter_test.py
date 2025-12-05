#!/usr/bin/env python3
"""
Test suite for Lambda Calculus Interpreter with Arithmetic Operations.
"""

import subprocess
import sys
import os


def run_interpreter(expression):
    """Run the interpreter with the given expression and return the output."""
    try:
        result = subprocess.run(
            [sys.executable, 'interpreter.py', expression],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except Exception as e:
        return None


def test_case(name, expression, expected):
    """Run a single test case."""
    print(f"Testing: {name}")
    print(f"  Expression: {expression}")
    actual = run_interpreter(expression)
    print(f"  Expected: {expected}")
    print(f"  Actual: {actual}")
    
    if actual == expected:
        print(f"  ✓ PASS")
        return True
    else:
        print(f"  ✗ FAIL")
        return False


def main():
    """Run all test cases."""
    print("=" * 70)
    print("Lambda Calculus Interpreter Test Suite")
    print("=" * 70)
    print()
    
    # Change to the directory containing interpreter.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    tests = []
    
    # Test cases from the specification
    BLUE = '\033[94m'
    RESET = '\033[0m'
    print(f"\n{BLUE}Required Test Cases from Specification:{RESET}")
    print("-" * 70)
    
    # Lazy evaluation tests
    tests.append(("Lazy evaluation - no reduction under lambda",
                  "\\x.(\\y.y)x",
                  "(\\x.((\\y.y) x))"))
    
    tests.append(("Lazy evaluation - call-by-name",
                  "(\\x.a x) ((\\x.x)b)",
                  "(a ((\\x.x) b))"))
    
    # Arithmetic tests
    tests.append(("Arithmetic - subtraction with negation",
                  "(\\x.x) (1--2)",
                  "3.0"))
    
    tests.append(("Arithmetic - triple negation",
                  "(\\x.x) (1---2)",
                  "-1.0"))
    
    tests.append(("Arithmetic - addition in lambda",
                  "(\\x.x + 1) 5",
                  "6.0"))
    
    tests.append(("Arithmetic - multiplication in lambda",
                  "(\\x.x * x) 3",
                  "9.0"))
    
    tests.append(("Arithmetic - curried addition",
                  "(\\x.\\y.x + y) 3 4",
                  "7.0"))
    
    tests.append(("Arithmetic - order of operations",
                  "1-2*3-4",
                  "-9.0"))
    
    tests.append(("Arithmetic - application precedence",
                  "(\\x.x * x) 2 * 3",
                  "12.0"))
    
    tests.append(("Arithmetic - negation in application",
                  "(\\x.x * x) (-2) * (-3)",
                  "-12.0"))
    
    tests.append(("Arithmetic - parentheses",
                  "((\\x.x * x) (-2)) * (-3)",
                  "-12.0"))
    
    tests.append(("Arithmetic - triple unary negation",
                  "(\\x.x) (---2)",
                  "-2.0"))
    
    # Additional comprehensive tests
    print(f"\n{BLUE}Additional Comprehensive Tests:{RESET}")
    print("-" * 70)
    
    # Basic lambda calculus
    tests.append(("Identity function",
                  "(\\x.x) a",
                  "a"))
    
    tests.append(("Constant function",
                  "(\\x.\\y.x) a b",
                  "a"))
    
    tests.append(("Function application",
                  "(\\x.x) (\\y.y)",
                  "(\\y.y)"))
    
    # Numbers and arithmetic
    tests.append(("Simple number",
                  "5",
                  "5.0"))
    
    tests.append(("Negative number",
                  "-5",
                  "-5.0"))
    
    tests.append(("Double negation",
                  "--5",
                  "5.0"))
    
    tests.append(("Addition",
                  "2 + 3",
                  "5.0"))
    
    tests.append(("Subtraction",
                  "5 - 3",
                  "2.0"))
    
    tests.append(("Multiplication",
                  "2 * 3",
                  "6.0"))
    
    tests.append(("Multiplication precedence",
                  "2 + 3 * 4",
                  "14.0"))
    
    tests.append(("Subtraction precedence",
                  "10 - 2 * 3",
                  "4.0"))
    
    tests.append(("Left-associative subtraction",
                  "10 - 2 - 3",
                  "5.0"))
    
    tests.append(("Unary negation precedence",
                  "-2 * 3",
                  "-6.0"))
    
    tests.append(("Unary negation with addition",
                  "-2 + 3",
                  "1.0"))
    
    # Lambda with arithmetic
    tests.append(("Lambda with multiplication",
                  "(\\x.x * 2) 5",
                  "10.0"))
    
    tests.append(("Lambda with addition",
                  "(\\x.x + x) 3",
                  "6.0"))
    
    tests.append(("Nested lambda with arithmetic",
                  "(\\x.\\y.x * y) 4 5",
                  "20.0"))
    
    tests.append(("Lambda returning arithmetic expression",
                  "(\\x.x) (2 + 3)",
                  "5.0"))
    
    # Complex expressions
    tests.append(("Complex expression 1",
                  "(\\x.x * x + 1) 3",
                  "10.0"))
    
    tests.append(("Complex expression 2",
                  "(\\x.\\y.x * y + x) 2 3",
                  "8.0"))
    
    tests.append(("Application with arithmetic",
                  "(\\x.x) 5 + (\\x.x) 3",
                  "8.0"))
    
    # Edge cases
    tests.append(("Zero",
                  "0",
                  "0.0"))
    
    tests.append(("Negative zero",
                  "-0",
                  "0.0"))
    
    tests.append(("One minus one",
                  "1 - 1",
                  "0.0"))
    
    tests.append(("Multiplication by zero",
                  "5 * 0",
                  "0.0"))
    
    # Run all tests
    passed = 0
    failed = 0
    
    for name, expression, expected in tests:
        if test_case(name, expression, expected):
            passed += 1
        else:
            failed += 1
        print()
    
    # Summary
    print("=" * 70)
    print(f"Test Summary: {passed} passed, {failed} failed out of {len(tests)} total")
    print("=" * 70)
    
    if failed == 0:
        print("All tests passed! ✓")
        return 0
    else:
        print(f"{failed} test(s) failed. ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
