"""
GrammarFix: Dangling-Else Resolver
Core parsing logic.

Supports:
- if (condition) statement
- if (condition) statement else statement
- Simple statements such as x;
- Ambiguity detection using the original grammar
- Nearest-unmatched-if parsing using the transformed grammar
"""

import re
from dataclasses import dataclass


# --------------------------------------------------
# 1. Tokenizer
# --------------------------------------------------

TOKEN_PATTERN = re.compile(
    r"\s*(if\b|else\b|[A-Za-z_]\w*|[();])"
)


def tokenize(source):
    """Convert the source program into a list of tokens."""

    tokens = []
    position = 0

    while position < len(source):
        # Ignore whitespace.
        if source[position].isspace():
            position += 1
            continue

        match = TOKEN_PATTERN.match(source, position)

        if not match:
            raise SyntaxError(
                f"Unexpected character at position {position}: "
                f"{source[position]!r}"
            )

        tokens.append(match.group(1))
        position = match.end()

    if not tokens:
        raise SyntaxError("Please enter a statement.")

    return tokens


# --------------------------------------------------
# 2. Parse-tree node
# --------------------------------------------------

@dataclass
class Node:
    kind: str
    value: str = ""
    children: tuple = ()


def simple_statement(name):
    return Node("statement", name)


def if_statement(condition, then_branch, else_branch=None):
    children = (then_branch,) if else_branch is None else (
        then_branch,
        else_branch,
    )

    return Node(
        "if",
        condition,
        children,
    )


# --------------------------------------------------
# 3. Original ambiguous grammar parser
# --------------------------------------------------

def parse_original(source):
    """
    Return every valid parse tree under the original grammar.

    Grammar:
        S -> if (E) S
        S -> if (E) S else S
        S -> identifier ;

    The parser explores both possibilities:
    1. An if statement without an else.
    2. An if statement with an else.
    """

    tokens = tokenize(source)
    token_count = len(tokens)
    memo = {}

    def parse_statement(position):
        if position in memo:
            return memo[position]

        results = []

        # Case 1: simple statement, e.g. x;
        if (
            position + 1 < token_count
            and re.fullmatch(r"[A-Za-z_]\w*", tokens[position])
            and tokens[position] not in ("if", "else")
            and tokens[position + 1] == ";"
        ):
            results.append(
                (
                    simple_statement(tokens[position]),
                    position + 2,
                )
            )

        # Case 2: if statement
        if (
            position + 3 < token_count
            and tokens[position] == "if"
            and tokens[position + 1] == "("
        ):
            closing = position + 2

            # Find the matching closing parenthesis.
            depth = 1

            while closing < token_count and depth > 0:
                if tokens[closing] == "(":
                    depth += 1
                elif tokens[closing] == ")":
                    depth -= 1

                closing += 1

            if depth == 0:
                condition_tokens = tokens[position + 2:closing - 1]

                if condition_tokens:
                    condition = " ".join(condition_tokens)

                    # Parse the then-branch.
                    for then_node, then_end in parse_statement(closing):

                        # Original grammar permits no else.
                        results.append(
                            (
                                if_statement(condition, then_node),
                                then_end,
                            )
                        )

                        # Original grammar also permits an else.
                        if (
                            then_end < token_count
                            and tokens[then_end] == "else"
                        ):
                            for else_node, else_end in parse_statement(
                                then_end + 1
                            ):
                                results.append(
                                    (
                                        if_statement(
                                            condition,
                                            then_node,
                                            else_node,
                                        ),
                                        else_end,
                                    )
                                )

        memo[position] = results
        return results

    all_results = parse_statement(0)

    # Keep only parses that consume the entire input.
    complete = [
        tree
        for tree, end_position in all_results
        if end_position == token_count
    ]

    # Remove duplicate tree representations.
    unique = {}
    for tree in complete:
        unique[tree_to_string(tree)] = tree

    if not unique:
        raise SyntaxError(
            "The input is not a valid statement for the supported grammar."
        )

    return list(unique.values())


# --------------------------------------------------
# 4. Transformed grammar parser
# --------------------------------------------------

def parse_transformed(source):
    """
    Parse using nearest-unmatched-if behavior.

    Conceptual grammar:
        S -> M | U
        M -> if (E) M else M | other
        U -> if (E) S | if (E) M else U

    This parser consumes an else as soon as it is available
    after parsing the then-branch, binding it to the nearest
    unmatched if.
    """

    tokens = tokenize(source)
    token_count = len(tokens)

    def parse_statement(position):
        # Simple statement.
        if (
            position + 1 < token_count
            and re.fullmatch(r"[A-Za-z_]\w*", tokens[position])
            and tokens[position] not in ("if", "else")
            and tokens[position + 1] == ";"
        ):
            return simple_statement(tokens[position]), position + 2

        # If statement.
        if (
            position < token_count
            and tokens[position] == "if"
            and position + 1 < token_count
            and tokens[position + 1] == "("
        ):
            depth = 1
            closing = position + 2

            while closing < token_count and depth > 0:
                if tokens[closing] == "(":
                    depth += 1
                elif tokens[closing] == ")":
                    depth -= 1

                closing += 1

            if depth != 0:
                raise SyntaxError("Missing closing parenthesis.")

            condition_tokens = tokens[position + 2:closing - 1]

            if not condition_tokens:
                raise SyntaxError("The if condition cannot be empty.")

            condition = " ".join(condition_tokens)

            then_node, next_position = parse_statement(closing)

            # Consume else immediately if present.
            if (
                next_position < token_count
                and tokens[next_position] == "else"
            ):
                else_node, final_position = parse_statement(
                    next_position + 1
                )

                return (
                    if_statement(condition, then_node, else_node),
                    final_position,
                )

            return if_statement(condition, then_node), next_position

        raise SyntaxError(
            f"Expected an if statement or a simple statement near "
            f"token {tokens[position] if position < token_count else 'end of input'}."
        )

    tree, end_position = parse_statement(0)

    if end_position != token_count:
        raise SyntaxError(
            f"Unexpected token: {tokens[end_position]}"
        )

    return tree


# --------------------------------------------------
# 5. Parse-tree conversion
# --------------------------------------------------

def tree_to_string(node):
    """Convert a tree into a stable text representation."""

    if node.kind == "statement":
        return f"STATEMENT({node.value})"

    if node.kind == "if":
        if len(node.children) == 1:
            return (
                f"IF({node.value}, "
                f"THEN={tree_to_string(node.children[0])})"
            )

        return (
            f"IF({node.value}, "
            f"THEN={tree_to_string(node.children[0])}, "
            f"ELSE={tree_to_string(node.children[1])})"
        )

    return str(node)


def tree_to_nested_dict(node):
    """Convert a parse tree to nested data for visualization."""

    if node.kind == "statement":
        return {
            "name": f"Statement: {node.value}"
        }

    result = {
        "name": f"IF ({node.value})",
        "children": [
            {
                "name": "THEN",
                "children": [tree_to_nested_dict(node.children[0])],
            }
        ],
    }

    if len(node.children) == 2:
        result["children"].append(
            {
                "name": "ELSE",
                "children": [tree_to_nested_dict(node.children[1])],
            }
        )

    return result


# --------------------------------------------------
# 6. Explanation
# --------------------------------------------------

def explain_tree(node):
    """Explain how else clauses are associated with if statements."""

    associations = []
    counter = [0]

    def visit(current):
        if current.kind != "if":
            return

        counter[0] += 1
        current_if = counter[0]

        if len(current.children) == 2:
            associations.append(
                f"The else belonging to IF #{current_if} "
                f"is associated with condition '{current.value}'."
            )

        for child in current.children:
            visit(child)

    visit(node)

    if not associations:
        return (
            "No else clause is present. There is no dangling-else "
            "ambiguity in this interpretation."
        )

    return (
        "The parser associates each else with the nearest unmatched if. "
        + " ".join(associations)
    )