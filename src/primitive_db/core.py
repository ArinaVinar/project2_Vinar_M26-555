# {
#     "users": {
#         "ID": "int",
#         "name": "str",
#         "age": "int",
#         "is_active": "bool"
#     }
# }
from primitive_db.constants import ID_COLUMN, ID_TYPE, VALID_TYPES


def validate_name(name):
    if not name.isidentifier():
        raise ValueError(name)

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

def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f"Ошибка: Таблица `{table_name}` не существует")
        return None

    del metadata[table_name]
    return metadata

def list_tables(metadata):
    if not metadata:
        print("Таблиц нет")
        return
    for table_name in metadata:
        print(f"{table_name}")