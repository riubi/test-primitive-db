"""Core database logic for table management and data operations."""

from src.primitive_db.constants import ID_COLUMN, ID_TYPE, SUPPORTED_TYPES
from src.primitive_db.decorators import (
    confirm_action,
    handle_db_errors,
    log_time,
)


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Create a new table with the specified columns."""
    if table_name in metadata:
        print(f'Error: Table "{table_name}" already exists.')
        return None

    parsed_columns = []

    for col_def in columns:
        if ":" not in col_def:
            print(f"Invalid value: {col_def}. Please try again.")
            return None

        col_name, col_type = col_def.split(":", 1)

        if not col_name:
            print(f"Invalid value: {col_def}. Please try again.")
            return None

        if col_type not in SUPPORTED_TYPES:
            print(
                f"Invalid value: {col_type}. "
                f"Allowed types: {', '.join(SUPPORTED_TYPES)}."
            )
            return None

        parsed_columns.append({"name": col_name, "type": col_type})

    all_columns = [{"name": ID_COLUMN, "type": ID_TYPE}] + parsed_columns

    metadata[table_name] = {
        "columns": all_columns,
        "next_id": 1,
    }

    columns_str = ", ".join(
        f"{col['name']}:{col['type']}" for col in all_columns
    )
    print(f'Table "{table_name}" created successfully with columns: {columns_str}')

    return metadata


@handle_db_errors
@confirm_action("drop table")
def drop_table(metadata, table_name):
    """Drop (delete) a table from the database."""
    if table_name not in metadata:
        print(f'Error: Table "{table_name}" does not exist.')
        return None

    del metadata[table_name]
    print(f'Table "{table_name}" deleted successfully.')

    return metadata


def list_tables(metadata):
    """List all tables in the database."""
    if not metadata:
        print("No tables found.")
        return

    for table_name in metadata:
        print(f"- {table_name}")


def table_info(metadata, table_name):
    """Display information about a table."""
    if table_name not in metadata:
        print(f'Error: Table "{table_name}" does not exist.')
        return

    table_meta = metadata[table_name]
    columns = table_meta["columns"]

    columns_str = ", ".join(f"{col['name']}:{col['type']}" for col in columns)

    print(f"Table: {table_name}")
    print(f"Columns: {columns_str}")


def validate_value(value, expected_type):
    """Validate and convert a value to the expected type."""
    if expected_type == "int":
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return None
        return None

    elif expected_type == "str":
        if isinstance(value, str):
            return value
        return str(value)

    elif expected_type == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() == "true":
                return True
            if value.lower() == "false":
                return False
        return None

    return None


@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data):
    """Insert a new record into a table."""
    if table_name not in metadata:
        print(f'Error: Table "{table_name}" does not exist.')
        return None, None, None

    table_meta = metadata[table_name]
    columns = table_meta["columns"]
    expected_count = len(columns) - 1

    if len(values) != expected_count:
        print(f"Error: Expected {expected_count} values, got {len(values)}.")
        return None, None, None

    new_id = table_meta["next_id"]
    record = {ID_COLUMN: new_id}

    for i, value in enumerate(values):
        col = columns[i + 1]
        col_name = col["name"]
        col_type = col["type"]

        validated_value = validate_value(value, col_type)
        if validated_value is None:
            print(
                f"Error: Invalid value '{value}' for column "
                f"'{col_name}' (expected {col_type})."
            )
            return None, None, None

        record[col_name] = validated_value

    table_data.append(record)
    metadata[table_name]["next_id"] = new_id + 1

    print(f'Record with ID={new_id} added to table "{table_name}" successfully.')

    return metadata, table_data, new_id


@handle_db_errors
@log_time
def select(table_data, columns, where_clause=None):
    """Select records from a table."""
    if where_clause is None:
        return table_data

    results = []
    for record in table_data:
        match = True
        for col, value in where_clause.items():
            if col not in record:
                match = False
                break
            record_value = record[col]
            if isinstance(record_value, int) and isinstance(value, str):
                try:
                    value = int(value)
                except ValueError:
                    pass
            if record_value != value:
                match = False
                break
        if match:
            results.append(record)

    return results


@handle_db_errors
def update(metadata, table_name, table_data, set_clause, where_clause):
    """Update records in a table."""
    if table_name not in metadata:
        print(f'Error: Table "{table_name}" does not exist.')
        return None, None

    table_meta = metadata[table_name]
    columns = table_meta["columns"]

    set_col = list(set_clause.keys())[0]
    set_value = set_clause[set_col]

    col_type = None
    for col in columns:
        if col["name"] == set_col:
            col_type = col["type"]
            break

    if col_type is None:
        print(f"Error: Column '{set_col}' does not exist.")
        return None, None

    validated_value = validate_value(set_value, col_type)
    if validated_value is None:
        print(
            f"Error: Invalid value '{set_value}' for column "
            f"'{set_col}' (expected {col_type})."
        )
        return None, None

    updated_ids = []
    for record in table_data:
        match = True
        for col, value in where_clause.items():
            if col not in record:
                match = False
                break
            record_value = record[col]
            if isinstance(record_value, int) and isinstance(value, str):
                try:
                    value = int(value)
                except ValueError:
                    pass
            if record_value != value:
                match = False
                break

        if match:
            record[set_col] = validated_value
            updated_ids.append(record[ID_COLUMN])

    if not updated_ids:
        print("No records matching the condition found.")
        return table_data, []

    for uid in updated_ids:
        print(f'Record with ID={uid} in table "{table_name}" updated successfully.')

    return table_data, updated_ids


@handle_db_errors
@confirm_action("delete record")
def delete(table_name, table_data, where_clause):
    """Delete records from a table."""
    deleted_ids = []
    new_data = []

    for record in table_data:
        match = True
        for col, value in where_clause.items():
            if col not in record:
                match = False
                break
            record_value = record[col]
            if isinstance(record_value, int) and isinstance(value, str):
                try:
                    value = int(value)
                except ValueError:
                    pass
            if record_value != value:
                match = False
                break

        if match:
            deleted_ids.append(record[ID_COLUMN])
        else:
            new_data.append(record)

    if not deleted_ids:
        print("No records matching the condition found.")
        return table_data, []

    for did in deleted_ids:
        print(f'Record with ID={did} deleted from table "{table_name}" successfully.')

    return new_data, deleted_ids
