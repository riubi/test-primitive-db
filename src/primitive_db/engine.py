"""Engine module - handles startup, main loop, and command parsing."""

import shlex

import prompt
from prettytable import PrettyTable

from src.primitive_db.constants import METADATA_FILE
from src.primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    table_info,
    update,
)
from src.primitive_db.decorators import create_cacher
from src.primitive_db.parser import (
    parse_delete_command,
    parse_insert_command,
    parse_select_command,
    parse_update_command,
)
from src.primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

select_cache = create_cacher()


def print_help():
    """Print the help message with available commands."""
    print("\n***Data Operations***")
    print("Commands:")
    print("  create_table <table_name> <col1:type> .. - create table")
    print("  list_tables - show all tables")
    print("  drop_table <table_name> - delete table")
    print("  insert into <table> values (<val1>, ..) - insert record")
    print("  select from <table> [where <col> = <val>] - read records")
    print("  update <table> set <col>=<val> where <col>=<val> - update record")
    print("  delete from <table> where <col> = <val> - delete record")
    print("  info <table_name> - show table information")
    print("\nGeneral:")
    print("  help - show help")
    print("  exit - exit program\n")


def display_table(records, columns):
    """Display records in a formatted table using PrettyTable."""
    if not records:
        print("No records to display.")
        return

    col_names = [col["name"] for col in columns]
    table = PrettyTable(col_names)

    for record in records:
        row = [record.get(col, "") for col in col_names]
        table.add_row(row)

    print(table)


def handle_create_table(args, metadata):
    """Handle create_table command."""
    if len(args) < 3:
        print("Usage: create_table <table_name> <col1:type> ...")
        return

    result = create_table(metadata, args[1], args[2:])
    if result is not None:
        save_metadata(METADATA_FILE, result)


def handle_drop_table(args, metadata):
    """Handle drop_table command."""
    if len(args) < 2:
        print("Usage: drop_table <table_name>")
        return

    table_name = args[1]
    result = drop_table(metadata, table_name)
    if result is not None:
        save_metadata(METADATA_FILE, result)
        delete_table_data(table_name)
        select_cache.clear()


def handle_info(args, metadata):
    """Handle info command."""
    if len(args) < 2:
        print("Usage: info <table_name>")
        return

    table_name = args[1]
    table_info(metadata, table_name)
    if table_name in metadata:
        table_data = load_table_data(table_name)
        print(f"Record count: {len(table_data)}")


def handle_insert(args, metadata):
    """Handle insert command."""
    table_name, values = parse_insert_command(args[1:])

    if table_name is None:
        print("Usage: insert into <table> values (<val1>, <val2>, ...)")
        return

    table_data = load_table_data(table_name)
    new_meta, new_data, _ = insert(metadata, table_name, values, table_data)

    if new_meta is not None:
        save_metadata(METADATA_FILE, new_meta)
        save_table_data(table_name, new_data)
        select_cache.clear()


def handle_select(args, metadata):
    """Handle select command."""
    table_name, where_clause = parse_select_command(args[1:])

    if table_name is None:
        print("Usage: select from <table> [where <column> = <value>]")
        return

    if table_name not in metadata:
        print(f'Error: Table "{table_name}" does not exist.')
        return

    columns = metadata[table_name]["columns"]
    cache_key = select_cache.get_key(table_name, where_clause)

    def fetch_data():
        data = load_table_data(table_name)
        return select(data, columns, where_clause)

    results = select_cache(cache_key, fetch_data)
    display_table(results, columns)


def handle_update(args, metadata):
    """Handle update command."""
    table_name, set_clause, where_clause = parse_update_command(args[1:])

    if table_name is None or set_clause is None or where_clause is None:
        print("Usage: update <table> set <col>=<val> where <col>=<val>")
        return

    if table_name not in metadata:
        print(f'Error: Table "{table_name}" does not exist.')
        return

    table_data = load_table_data(table_name)
    new_data, _ = update(metadata, table_name, table_data, set_clause, where_clause)

    if new_data is not None:
        save_table_data(table_name, new_data)
        select_cache.clear()


def handle_delete(args, metadata):
    """Handle delete command."""
    table_name, where_clause = parse_delete_command(args[1:])

    if table_name is None or where_clause is None:
        print("Usage: delete from <table> where <column> = <value>")
        return

    if table_name not in metadata:
        print(f'Error: Table "{table_name}" does not exist.')
        return

    table_data = load_table_data(table_name)
    result = delete(table_name, table_data, where_clause)

    if result is not None:
        new_data, _ = result
        if new_data is not None:
            save_table_data(table_name, new_data)
            select_cache.clear()


COMMAND_HANDLERS = {
    "help": lambda args, meta: print_help(),
    "list_tables": lambda args, meta: list_tables(meta),
    "create_table": handle_create_table,
    "drop_table": handle_drop_table,
    "info": handle_info,
    "insert": handle_insert,
    "select": handle_select,
    "update": handle_update,
    "delete": handle_delete,
}


def run():
    """Run the main database loop."""
    print("\n***Database***\n")
    print_help()

    while True:
        metadata = load_metadata(METADATA_FILE)
        user_input = prompt.string(">>>Enter command: ")

        if not user_input or not user_input.strip():
            continue

        try:
            args = shlex.split(user_input.strip())
        except ValueError as e:
            print(f"Command parsing error: {e}")
            continue

        command = args[0].lower()

        if command == "exit":
            print("Goodbye!")
            break

        handler = COMMAND_HANDLERS.get(command)
        if handler:
            handler(args, metadata)
        else:
            print(f"Command '{command}' not found. Type 'help' for available commands.")
