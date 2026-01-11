"""Parser module for command and query parsing."""

import re


def parse_condition(condition_str):
    """Parse a WHERE or SET condition string into a dictionary."""
    match = re.match(r'(\w+)\s*=\s*(.+)', condition_str.strip())
    if not match:
        return None

    column = match.group(1)
    value_str = match.group(2).strip()
    value = parse_value(value_str)

    return {column: value}


def parse_value(value_str):
    """Parse a string value into appropriate Python type."""
    value_str = value_str.strip()

    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]

    if value_str.lower() == "true":
        return True
    if value_str.lower() == "false":
        return False

    try:
        return int(value_str)
    except ValueError:
        pass

    return value_str


def parse_values_list(values_str):
    """Parse a comma-separated list of values from INSERT command."""
    values = []
    current = ""
    in_quotes = False
    quote_char = None

    for char in values_str:
        if char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
            current += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
            current += char
        elif char == "," and not in_quotes:
            values.append(parse_value(current.strip()))
            current = ""
        else:
            current += char

    if current.strip():
        values.append(parse_value(current.strip()))

    return values


def parse_insert_command(args):
    """Parse INSERT command: into <table> values (<val1>, <val2>, ...)"""
    cmd_str = " ".join(args)

    match = re.match(
        r'into\s+(\w+)\s+values\s*\((.+)\)',
        cmd_str,
        re.IGNORECASE
    )

    if not match:
        return None, None

    table_name = match.group(1)
    values_str = match.group(2)
    values = parse_values_list(values_str)

    return table_name, values


def parse_select_command(args):
    """Parse SELECT command: from <table> [where <col> = <val>]"""
    cmd_str = " ".join(args)

    match = re.match(
        r'from\s+(\w+)\s+where\s+(.+)',
        cmd_str,
        re.IGNORECASE
    )

    if match:
        table_name = match.group(1)
        where_str = match.group(2)
        where_clause = parse_condition(where_str)
        return table_name, where_clause

    match = re.match(r'from\s+(\w+)', cmd_str, re.IGNORECASE)
    if match:
        return match.group(1), None

    return None, None


def parse_update_command(args):
    """Parse UPDATE command: <table> set <col>=<val> where <col>=<val>"""
    cmd_str = " ".join(args)

    match = re.match(
        r'(\w+)\s+set\s+(.+?)\s+where\s+(.+)',
        cmd_str,
        re.IGNORECASE
    )

    if not match:
        return None, None, None

    table_name = match.group(1)
    set_str = match.group(2)
    where_str = match.group(3)

    set_clause = parse_condition(set_str)
    where_clause = parse_condition(where_str)

    return table_name, set_clause, where_clause


def parse_delete_command(args):
    """Parse DELETE command: from <table> where <col> = <val>"""
    cmd_str = " ".join(args)

    match = re.match(
        r'from\s+(\w+)\s+where\s+(.+)',
        cmd_str,
        re.IGNORECASE
    )

    if not match:
        return None, None

    table_name = match.group(1)
    where_str = match.group(2)
    where_clause = parse_condition(where_str)

    return table_name, where_clause
