# Calculator Implementation Specifications

## Overview
This calculator implementation uses the Lark parser generator to parse mathematical expressions and evaluate them with proper operator precedence. The implementation consists of three main files: `calculator_cfg.py`, `grammar.lark`, and this specification document.

## Context-Free Grammar (CFG)

The grammar is defined in `grammar.lark` and follows this precedence hierarchy (from lowest to highest precedence):

1. **Addition and Subtraction** (`+`, `-`) - Left associative
2. **Multiplication** (`*`) - Left associative  
3. **Exponentiation** (`^`) - Right associative
4. **Unary negation** (`-`) - Right associative
5. **Logarithm** (`log ... base ...`) - Function application
6. **Parentheses** (`()`) - Highest precedence
7. **Numbers** - Terminal symbols

### Grammar Rules

```
?exp: add_exp

?add_exp: mul_exp
    | add_exp "+" mul_exp    -> add
    | add_exp "-" mul_exp    -> sub

?mul_exp: pow_exp
    | mul_exp "*" pow_exp    -> mul

?pow_exp: unary_exp
    | pow_exp "^" unary_exp  -> pow

?unary_exp: log_exp
    | "-" unary_exp          -> neg
    | "(" exp ")"            -> parens
    | NUMBER                 -> number

?log_exp: "log" exp "base" exp -> log
```

## Order of Operations

The grammar enforces the following order of operations:

1. **Parentheses** have the highest precedence
2. **Unary negation** (`-x`) has higher precedence than binary operations
3. **Exponentiation** (`^`) is right-associative: `2^3^2 = 2^(3^2) = 512`
4. **Multiplication** (`*`) has higher precedence than addition/subtraction
5. **Addition and subtraction** (`+`, `-`) have the same precedence and are left-associative

## Implementation Details

### File Structure

- **`calculator_cfg.py`**: Main implementation file containing the calculator logic
- **`grammar.lark`**: Lark grammar definition file
- **`specs.md`**: This specification document

### Key Methods and Classes

#### `CalculatorTransformer` Class
This class inherits from Lark's `Transformer` and implements the evaluation logic:

- **`add(self, items)`**: Handles addition operations
- **`sub(self, items)`**: Handles subtraction operations  
- **`mul(self, items)`**: Handles multiplication operations
- **`pow(self, items)`**: Handles exponentiation operations
- **`neg(self, items)`**: Handles unary negation
- **`number(self, items)`**: Converts string numbers to float
- **`log(self, items)`**: Handles logarithm operations using `math.log`
- **`parens(self, items)`**: Handles parentheses by returning the inner expression

#### Key Functions

- **`create_parser()`**: Creates and returns a Lark parser instance loaded from `grammar.lark`
- **`evaluate_expression(expression)`**: Main evaluation function that parses and evaluates expressions
- **`main()`**: Command-line interface that handles input and output

### Program Flow

1. **Input Processing**: The program reads a mathematical expression from command line arguments
2. **Grammar Loading**: The Lark parser loads the grammar definition from `grammar.lark`
3. **Parsing**: The expression is parsed into an Abstract Syntax Tree (AST) using the grammar
4. **Transformation**: The `CalculatorTransformer` recursively evaluates the AST nodes
5. **Output**: The final result is printed to stdout

### Error Handling

The implementation includes error handling for:
- Invalid mathematical expressions
- Parsing errors
- Division by zero (handled by Python's math operations)
- Invalid logarithm operations

### Testing

The implementation has been tested against all provided test cases:

- `1+2*3` → `7` (multiplication before addition)
- `2-(4+2)` → `-4` (parentheses precedence)
- `(3+2)*2` → `10` (parentheses precedence)
- `--1` → `1` (double negation)
- `2^3^2` → `512` (right-associative exponentiation)
- `2^3+1` → `9` (exponentiation before addition)
- `2^3*2` → `16` (exponentiation before multiplication)
- `log 8 base 2` → `3` (logarithm function)
- `log 8 base 2 + 1` → `4` (logarithm before addition)
- `-3^2` → `-9` (unary negation before exponentiation)

## Dependencies

- **Lark Parser**: For grammar parsing and AST generation
- **Python Standard Library**: `sys` for command line arguments, `math` for logarithm operations

## Usage

```bash
python calculator_cfg.py "mathematical_expression"
```

Example:
```bash
python calculator_cfg.py "2^3+1"
# Output: 9
```
