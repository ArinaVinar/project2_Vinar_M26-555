# {
#     "users": {
#         "ID": "int",
#         "name": "str",
#         "age": "int",
#         "is_active": "bool"
#     }
# }
import json

from primitive_db.constants import ID_COLUMN, ID_TYPE, TYPE_CLASSES, VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

SELECT_CACHE = create_cacher()

def validate_name(name):
    if not name.isidentifier():
        raise ValueError(name)

@handle_db_errors
def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f"Ошибка: Таблица `{table_name}` уже существует")
        return None

    validate_name(table_name)

    if not columns:
        raise ValueError("Не указаны имена столбцов")

    schema = {ID_COLUMN: ID_TYPE}
    column_names = set()

    for c in columns:
        parts = c.split(":")

        if len(parts) != 2:
            raise ValueError(c)

        column_name, column_type = parts
        validate_name(column_name)

        if column_type not in VALID_TYPES:
            raise ValueError(c)

        if column_name in column_names:
            raise ValueError(c)

        column_names.add(column_name)

        if column_name == ID_COLUMN:
            if column_type != ID_TYPE:
                raise ValueError(c)
            continue

        schema[column_name] = column_type

    metadata[table_name] = schema
    return metadata

@handle_db_errors
@confirm_action("Удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f"Ошибка: Таблица `{table_name}` не существует")
        return None

    del metadata[table_name]
    return metadata

@handle_db_errors
def list_tables(metadata):
    if not metadata:
        print("Таблиц нет")
        return
    for table_name in metadata:
        print(f"{table_name}")

def get_schema(metadata, table_name):
    if table_name not in metadata:
        raise ValueError(f"Таблица `{table_name}` не существует")
    return metadata[table_name]

def validate_fields(schema, fields):
    for column_name, value in fields.items():
        if column_name not in schema:
            raise ValueError(f"Столбец `{column_name}` не существует")

        expected_type = TYPE_CLASSES[schema[column_name]]

        if type(value) is not expected_type:
            raise ValueError(f"Столбец `{column_name}` "
                             f"требует тип {schema[column_name]}")

@handle_db_errors
@log_time
def insert(metadata, table_name, table_data, values):
    schema = get_schema(metadata, table_name)
    columns = [n for n in schema if n != ID_COLUMN]

    if len(values) != len(columns):
        raise ValueError(f"Ожидается значений: {len(columns)}, получено: {len(values)}")

    record = dict(zip(columns, values))
    validate_fields(schema, record)

    new_id = max(
        (record[ID_COLUMN] for record in table_data),
        default=0,
    ) + 1

    new_record = {ID_COLUMN: new_id, **record}
    return [*table_data, new_record]

def select_where_check(record, where_clause):
    return all(
        record[column_name] == value
        for column_name, value in where_clause.items()
    )

@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    cache_key = json.dumps(
        [table_data, where_clause],
        ensure_ascii=False,
        sort_keys=True,
    )

    def find_records():
        return [
            record.copy()
            for record in table_data
            if (
                    where_clause is None
                    or select_where_check(record, where_clause)
            )
        ]

    cached_records = SELECT_CACHE(cache_key, find_records)

    return [record.copy() for record in cached_records]

def clear_select_cache():
    SELECT_CACHE.clear()

@handle_db_errors
def update(table_data, set_clause, where_clause):
    return [
        {**record, **set_clause}
        if select_where_check(record, where_clause)
        else record.copy()
        for record in table_data
    ]

@handle_db_errors
@confirm_action("Удаление записей")
def delete(table_data, where_clause):
    return [
        record.copy()
        for record in table_data
        if not select_where_check(record, where_clause)
    ]