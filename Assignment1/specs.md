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
start: exp

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

?log_exp: "log" unary_exp "base" unary_exp -> log
```

## Order of Operations

The grammar enforces the following order of operations:

1. **Parentheses** have the highest precedence
2. **Unary negation** (`-x`) has higher precedence than binary operations and is right-associative, allowing expressions like `--1` (double negation)
3. **Exponentiation** (`^`) is right-associative: `2^3^2 = 2^(3^2) = 512`
4. **Multiplication** (`*`) has higher precedence than addition/subtraction
5. **Addition and subtraction** (`+`, `-`) have the same precedence and are left-associative

### Key Grammar Design Decisions

- **Right-associative exponentiation**: The grammar uses `pow_exp "^" unary_exp` to ensure that `2^3^2` is parsed as `2^(3^2)` rather than `(2^3)^2`. This is achieved by having the left operand be a `pow_exp` (higher level) and the right operand be a `unary_exp` (lower level), which causes the parser to group from right to left.

- **Unary negation precedence**: The grammar uses `"-" unary_exp` to allow nested unary negations (e.g., `--1`). This also ensures that unary negation has higher precedence than binary operations, so `-3^2` is evaluated as `-(3^2) = -9` rather than `(-3)^2 = 9`.

- **Logarithm syntax**: The grammar defines `log_exp` as `"log" unary_exp "base" unary_exp`, which ensures that both the argument and base are parsed as unary expressions, allowing for proper precedence handling.

## Implementation Details

### File Structure

- **`calculator_cfg.py`**: Main implementation file containing the calculator logic
- **`grammar.lark`**: Lark grammar definition file
- **`specs.md`**: This specification document

### Key Methods and Classes

#### `CalculatorTransformer` Class
This class inherits from Lark's `Transformer` and implements the evaluation logic:

- **`add(self, items)`**: Handles addition operations. Takes a list of two items and returns their sum.
- **`sub(self, items)`**: Handles subtraction operations. Takes a list of two items and returns their difference.
- **`mul(self, items)`**: Handles multiplication operations. Takes a list of two items and returns their product.
- **`pow(self, items)`**: Handles exponentiation operations. Takes a list of two items where `items[0]` is the base and `items[1]` is the exponent, and returns `items[0] ** items[1]`.
- **`neg(self, items)`**: Handles unary negation. Takes a list of one item and returns its negation.
- **`number(self, items)`**: Converts string number to float. Takes a list containing one string token and returns the corresponding float value.
- **`log(self, items)`**: Handles logarithm operations using `math.log`. Takes a list of two items where `items[0]` is the argument and `items[1]` is the base, and returns `math.log(items[0], items[1])`.
- **`parens(self, items)`**: Handles parentheses by returning the inner expression. Takes a list of one item (the expression inside parentheses) and returns it unchanged.

#### Key Functions

- **`create_parser()`**: Creates and returns a Lark parser instance loaded from `grammar.lark`. Uses the LALR parser algorithm for efficiency. The transformer is applied during parsing, so the parse tree is directly converted to Python values.

- **`evaluate_expression(expression)`**: Main evaluation function that parses and evaluates expressions. Takes a string expression, creates a parser, parses the expression, and returns the evaluated result. The result is extracted from the `start` node's first child.

- **`main()`**: Command-line interface that handles input and output. Reads the expression from `sys.argv[1]`, evaluates it, and prints the result. If the result is a whole number, it prints as an integer; otherwise, it prints as a float.

### Program Flow

1. **Input Processing**: The program reads a mathematical expression from command line arguments via `sys.argv[1]`
2. **Grammar Loading**: The Lark parser loads the grammar definition from `grammar.lark` file in the same directory
3. **Parsing**: The expression is parsed into an Abstract Syntax Tree (AST) using the LALR parser algorithm. The `CalculatorTransformer` is applied during parsing, so the AST nodes are immediately converted to Python numeric values.
4. **Transformation**: The `CalculatorTransformer` recursively evaluates the AST nodes. Each transformer method handles a specific grammar rule and returns the computed value.
5. **Output**: The final result is extracted from the parse tree (which is wrapped in a `start` node) and printed to stdout. Whole numbers are printed as integers for cleaner output.

### Error Handling

The implementation includes error handling for:
- Invalid mathematical expressions: Raises an exception with a descriptive error message
- Parsing errors: Caught and re-raised with context about the expression that failed
- Invalid logarithm operations: Handled by Python's `math.log` function (e.g., negative arguments or base 1 will raise appropriate exceptions)

### Testing

The implementation has been tested against all provided test cases:

- `1+2*3` → `7` (multiplication before addition)
- `2-(4+2)` → `-4` (parentheses precedence)
- `(3+2)*2` → `10` (parentheses precedence)
- `--1` → `1` (double negation, demonstrating right-associative unary negation)
- `2^3^2` → `512` (right-associative exponentiation: `2^(3^2) = 2^9 = 512`)
- `2^3+1` → `9` (exponentiation before addition: `(2^3)+1 = 8+1 = 9`)
- `2^3*2` → `16` (exponentiation before multiplication: `(2^3)*2 = 8*2 = 16`)
- `log 8 base 2` → `3` (logarithm function: `log₂(8) = 3`)
- `log 8 base 2 + 1` → `4` (logarithm before addition: `log₂(8)+1 = 3+1 = 4`)
- `-3^2` → `-9` (unary negation before exponentiation: `-(3^2) = -9`)

## Dependencies

- **Lark Parser**: For grammar parsing and AST generation. Install with `pip install lark` or `pip3 install lark`
- **Python Standard Library**: 
  - `sys` for command line arguments
  - `math` for logarithm operations

## Usage

```bash
python calculator_cfg.py "mathematical_expression"
```

Example:
```bash
python calculator_cfg.py "2^3+1"
# Output: 9
```

