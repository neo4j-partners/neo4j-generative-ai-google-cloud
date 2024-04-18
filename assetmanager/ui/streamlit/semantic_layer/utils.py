from typing import Dict, List
import streamlit as st

from neo4j_driver import run_query

def remove_lucene_chars(text: str) -> str:
    """Remove Lucene special characters"""
    special_chars = [
        "+",
        "-",
        "&",
        "|",
        "!",
        "(",
        ")",
        "{",
        "}",
        "[",
        "]",
        "^",
        '"',
        "~",
        "*",
        "?",
        ":",
        "\\",
    ]
    for char in special_chars:
        if char in text:
            text = text.replace(char, " ")
    return text.strip()


def generate_full_text_query(input: str) -> str:
    full_text_query = ""
    words = [el for el in remove_lucene_chars(input).split() if el]
    for word in words[:-1]:
        full_text_query += f" {word}~0.8 AND"
    full_text_query += f" {words[-1]}~0.8"
    return full_text_query.strip()


def get_candidates(input: str, type: str, limit: int = 3) -> List[Dict[str, str]]:
    candidate_query = """
    CALL db.index.fulltext.queryNodes($index, $fulltextQuery, {limit: $limit})
    YIELD node
    RETURN coalesce(node.companyName, node.managerName) AS candidate,
           [el in labels(node) WHERE el IN ['Company', 'Manager'] | el][0] AS label
    """
    ft_query = generate_full_text_query(input)
    candidates = run_query(
        candidate_query, {"fulltextQuery": ft_query, "index": type, "limit": limit}
    )
    return candidates