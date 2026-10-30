"""
GrammarFix — Dangling-Else Resolver
Streamlit web application.
"""

import streamlit as st

from core_logic import (
    parse_original,
    parse_transformed,
    tree_to_nested_dict,
    tree_to_string,
    explain_tree,
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="GrammarFix",
    page_icon="🌳",
    layout="wide",
)

st.title(" GrammarFix")
st.subheader("Dangling-Else Resolver")

st.markdown(
    """
    GrammarFix demonstrates how nested `if-else` statements can have
    multiple interpretations under an ambiguous grammar and how a
    transformed grammar resolves the ambiguity.

    **Key principle:** An `else` is associated with the nearest
    unmatched `if`.
    """
)

st.divider()


# --------------------------------------------------
# Grammar information
# --------------------------------------------------

with st.expander("View the grammars", expanded=True):
    left, right = st.columns(2)

    with left:
        st.markdown("### Original ambiguous grammar")
        st.code(
            """
S → if (E) S
S → if (E) S else S
S → identifier ;
            """.strip(),
            language="text",
        )

        st.caption(
            "The original grammar permits multiple interpretations "
            "of some nested if-else statements."
        )

    with right:
        st.markdown("### Transformed grammar")
        st.code(
            """
S → M | U
M → if (E) M else M | identifier ;
U → if (E) S | if (E) M else U
            """.strip(),
            language="text",
        )

        st.caption(
            "Matched and unmatched statements express the "
            "nearest-unmatched-if rule."
        )


st.divider()


# --------------------------------------------------
# Example inputs
# --------------------------------------------------

examples = {
    "Classic dangling-else example": """if (a)
    if (b)
        x;
    else
        y;""",

    "Nested if without else": """if (a)
    if (b)
        x;""",

    "Two else clauses": """if (a)
    if (b)
        x;
    else
        y;
else
    z;""",

    "Simple statement": "x;",

    "Three levels of nesting": """if (a)
    if (b)
        if (c)
            x;
        else
            y;""",
}


st.markdown("### Try an example")

selected_example = st.selectbox(
    "Choose an example to load",
    list(examples.keys()),
)

if "program_input" not in st.session_state:
    st.session_state.program_input = examples[
        "Classic dangling-else example"
    ]

if st.button("Load selected example"):
    st.session_state.program_input = examples[selected_example]


# --------------------------------------------------
# User input
# --------------------------------------------------

st.markdown("### Enter your statement")

source = st.text_area(
    "Nested if-else program",
    key="program_input",
    height=200,
    help="Use statements such as if (a) x; else y;",
)

resolve = st.button(
    "🔍 Resolve Ambiguity",
    type="primary",
    use_container_width=True,
)


# --------------------------------------------------
# Resolve ambiguity
# --------------------------------------------------

if resolve:

    try:
        original_trees = parse_original(source)
        transformed_tree = parse_transformed(source)

        st.success("Input parsed successfully!")

        st.markdown("## 1. Original grammar analysis")

        number_of_trees = len(original_trees)

        if number_of_trees > 1:
            st.warning(
                f"Ambiguity detected: {number_of_trees} valid "
                "parse trees were found."
            )
        else:
            st.success(
                f"No ambiguity detected for this input. "
                f"Valid parse trees found: {number_of_trees}."
            )

        st.markdown("### Competing parse trees")

        columns = st.columns(
            min(number_of_trees, 2)
        )

        for index, tree in enumerate(original_trees):
            with columns[index % len(columns)]:
                st.markdown(f"#### Parse tree {index + 1}")
                st.json(tree_to_nested_dict(tree))
                st.code(
                    tree_to_string(tree),
                    language="text",
                )

        st.divider()

        st.markdown("## 2. Transformed grammar result")

        st.success(
            "The transformed parser produced one valid parse tree."
        )

        st.json(tree_to_nested_dict(transformed_tree))

        st.markdown("### Parse-tree structure")

        st.code(
            tree_to_string(transformed_tree),
            language="text",
        )

        st.divider()

        st.markdown("## 3. Explanation")

        st.info(explain_tree(transformed_tree))

        st.markdown("### Summary")

        first, second, third = st.columns(3)

        first.metric(
            "Original parse trees",
            number_of_trees,
        )

        second.metric(
            "Transformed parse trees",
            1,
        )

        third.metric(
            "Ambiguity detected",
            "Yes" if number_of_trees > 1 else "No",
        )

        if number_of_trees > 1:
            st.markdown(
                """
                **Conclusion:** The original grammar allows multiple
                interpretations. The transformed parser follows the
                nearest-unmatched-if rule and produces one interpretation.
                """
            )

    except SyntaxError as error:
        st.error(f"Invalid input: {error}")

    except Exception as error:
        st.error(f"An unexpected error occurred: {error}")