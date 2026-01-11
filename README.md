# Primitive Database

Simple command-line database that stores data in JSON files.

## Quick Start

```bash
make install
make project
```

## Commands

### Tables

```
create_table users name:str age:int active:bool
list_tables
drop_table users
info users
```

Supported types: `int`, `str`, `bool`

### Data

```
insert into users values ("John", 25, true)
select from users
select from users where age = 25
update users set age = 26 where name = "John"
delete from users where ID = 1
```

### Other

```
help
exit
```

## Example

```
>>>Enter command: create_table users name:str age:int
Table "users" created successfully with columns: ID:int, name:str, age:int

>>>Enter command: insert into users values ("John", 25)
Record with ID=1 added to table "users" successfully.

>>>Enter command: select from users
+----+------+-----+
| ID | name | age |
+----+------+-----+
| 1  | John |  25 |
+----+------+-----+

>>>Enter command: drop_table users
Are you sure you want to perform "drop table"? [y/n]: y
Table "users" deleted successfully.
```

## Demo

### Demo 1: CRUD Operations
[![asciicast](https://asciinema.org/a/jIvoNjGVHYzll9xa.svg)](https://asciinema.org/a/LBdsxX3SIbGtKGSN)

### Demo 2: Decorators
[![asciicast](https://asciinema.org/a/jIvoNjGVHYzll9xa.svg)](https://asciinema.org/a/jIvoNjGVHYzll9xa)

## Development

```bash
make lint      # check code style
make build     # build package
make publish   # test publish (dry-run)
```

## Structure

```
src/primitive_db/
├── main.py        # entry point
├── engine.py      # command loop
├── core.py        # database logic
├── parser.py      # command parsing
├── utils.py       # file operations
├── decorators.py  # error handling, timing
└── constants.py   # config
```
