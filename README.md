# GrammarFix — Dangling-Else Resolver

## Project Overview

GrammarFix is an educational application that demonstrates ambiguity
in nested if-else statements and shows how grammar transformation
resolves the dangling-else problem.

## Objectives

- Demonstrate dangling-else ambiguity.
- Generate competing parse trees.
- Explain matched and unmatched statements.
- Apply the nearest-unmatched-if rule.
- Test nested conditional statements.

## Technologies

- Python
- Streamlit
- Graphviz package (optional for future graphical visualization)
- Python unittest

## Supported Syntax

Simple statements:

    x;

Conditional statements:

    if (a) x;

Conditional statements with else:

    if (a) x; else y;

Nested statements:

    if (a) if (b) x; else y;

The current implementation supports a restricted educational syntax.
It is not a complete parser for C, Java, or Python.

## Installation

Create and activate a virtual environment:

    python -m venv .venv

Windows PowerShell:

    .\.venv\Scripts\Activate.ps1

Install the required packages:

    python -m pip install -r requirements.txt

## Run Tests

    python -m unittest discover -s . -p "test_*.py"

## Run the Application

    python -m streamlit run app.py

Open the local address displayed in the terminal.

## Expected Demonstration

For the classic dangling-else example, the original grammar should
produce two valid interpretations. The transformed parser should
associate the else with the nearest unmatched if.