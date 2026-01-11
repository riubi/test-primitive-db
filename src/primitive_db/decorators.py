"""Decorators for error handling, logging, and action confirmation."""

import functools
import time

import prompt


def handle_db_errors(func):
    """Decorator that handles common database errors."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Error: Data file not found. Database may not be initialized.")
            return None
        except KeyError as e:
            print(f"Error: Table or column {e} not found.")
            return None
        except ValueError as e:
            print(f"Validation error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            return None

    return wrapper


def confirm_action(action_name):
    """Decorator factory that asks for user confirmation before executing."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response = prompt.string(
                f'Are you sure you want to perform "{action_name}"? [y/n]: '
            )

            if response is None or response.lower() != "y":
                print("Operation cancelled.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Decorator that measures and logs function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()

        elapsed = end_time - start_time
        print(f"Function {func.__name__} executed in {elapsed:.3f} seconds.")

        return result

    return wrapper


def create_cacher():
    """Create a caching function using closure."""
    cache = {}

    def cache_result(key, value_func):
        """Get cached result or compute and cache new value."""
        if key in cache:
            return cache[key]

        result = value_func()
        cache[key] = result
        return result

    def clear_cache():
        cache.clear()

    def get_cache_key(table_name, where_clause):
        if where_clause is None:
            return (table_name, None)
        where_tuple = tuple(sorted(where_clause.items()))
        return (table_name, where_tuple)

    cache_result.clear = clear_cache
    cache_result.get_key = get_cache_key

    return cache_result
