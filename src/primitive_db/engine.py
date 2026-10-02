import json
import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import ID_COLUMN, META_FILE
from primitive_db.core import (
    clear_select_cache,
    create_table,
    delete,
    drop_table,
    get_schema,
    insert,
    list_tables,
    select,
    update,
    validate_fields,
)
from primitive_db.parser import parse_data_command, tokenize
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Выводит справку по всем командам приложения."""
    print("Управление таблицами:")
    print("create_table <таблица> <столбец:тип> ... - создать таблицу")
    print("list_tables - показать список таблиц")
    print("drop_table <таблица> - удалить таблицу")

    print("\nОперации с данными:")
    print("insert into <таблица> values (...) - добавить запись")
    print("select from <таблица> - показать все записи")
    print("select from <таблица> where <столбец> = <значение>")
    print(
        "update <таблица> set <столбец> = <значение> "
        "where <столбец> = <значение>"
    )
    print("delete from <таблица> where <столбец> = <значение>")
    print("info <таблица> - информация о таблице")

    print("\nОбщие команды:")
    print("help - справочная информация")
    print("exit - выход из программы\n")


def run_command(metadata, args):
    """Выполняет команды управления таблицами и вызова справки."""
    command = args[0]
    arguments = args[1:]

    if command == "create_table":
        if len(arguments) < 2:
            raise ValueError("Ожидается имя таблицы и столбцы")

        table_name = arguments[0]
        columns = arguments[1:]
        result = create_table(metadata, table_name, columns)

        if result is not None:
            save_table_data(table_name, [])
            save_metadata(META_FILE, result)
            clear_select_cache()
            columns_text = ", ".join(
                f"{name}:{data_type}"
                for name, data_type in result[table_name].items()
            )
            print(
                f'Таблица "{table_name}" успешно создана '
                f"со столбцами: {columns_text}"
            )

    elif command == "drop_table":
        if len(arguments) != 1:
            raise ValueError("Ожидается одно имя таблицы")

        table_name = arguments[0]
        get_schema(metadata, table_name)
        result = drop_table(metadata, table_name)

        if result is not None:
            delete_table_data(table_name)
            save_metadata(META_FILE, result)
            clear_select_cache()
            print(f'Таблица "{table_name}" успешно удалена')

    elif command == "list_tables":
        if arguments:
            raise ValueError(" ".join(arguments))

        list_tables(metadata)

    elif command == "help":
        if arguments:
            raise ValueError(" ".join(arguments))

        print_help()

    else:
        print(f"Функции {command} нет. Попробуйте снова")


def run():
    """Запускает основной цикл команд и обрабатывает ошибки ввода."""
    print_help()

    while True:
        try:
            metadata = load_metadata(META_FILE)
        except json.JSONDecodeError:
            print(f"Ошибка: файл {META_FILE} содержит некорректный JSON")
            return
        except OSError as error:
            print(f"Ошибка чтения метаданных: {error}")
            return

        try:
            user_input = prompt.string(">>>Введите команду: ")
        except (EOFError, KeyboardInterrupt):
            print()
            return

        try:
            tokens = tokenize(user_input)

            if not tokens:
                continue

            command = tokens[0]

            if command == "exit":
                if len(tokens) != 1:
                    raise ValueError(" ".join(tokens[1:]))
                return

            if command in ("insert", "select", "update", "delete", "info"):
                execute_data_command(metadata, tokens)
            else:
                args = shlex.split(user_input)
                run_command(metadata, args)

        except json.JSONDecodeError:
            print("Ошибка: файл записей содержит некорректный JSON")
        except KeyError as error:
            print(f"Ошибка: таблица или столбец {error} не найден")
        except ValueError as error:
            print(f"Некорректное значение: {error}. Попробуйте снова")
        except OSError as error:
            print(f"Ошибка работы с файлами: {error}")
        except (EOFError, KeyboardInterrupt):
            print()
            return


def print_records(schema, records):
    """Выводит записи в консольной таблице с порядком столбцов из схемы."""
    table = PrettyTable()
    table.field_names = list(schema)

    for record in records:
        table.add_row([record[column] for column in schema])

    print(table)


def execute_data_command(metadata, tokens):
    """Выполняет CRUD-команды, сохраняет изменения и выводит результат."""
    command = tokens[0]
    table_name, payload, where_clause = parse_data_command(tokens)

    schema = get_schema(metadata, table_name)
    table_data = load_table_data(table_name)

    if where_clause is not None:
        validate_fields(schema, where_clause)

    if command == "insert":
        result = insert(metadata, table_name, table_data, payload)

        if result is not None:
            save_table_data(table_name, result)
            clear_select_cache()
            record_id = result[-1][ID_COLUMN]
            print(
                f"Запись с ID={record_id} успешно добавлена "
                f'в таблицу "{table_name}".'
            )

    elif command == "select":
        records = select(table_data, where_clause)

        if records is not None:
            print_records(schema, records)

    elif command == "info":
        columns_text = ", ".join(
            f"{name}:{data_type}"
            for name, data_type in schema.items()
        )
        print(f"Таблица: {table_name}")
        print(f"Столбцы: {columns_text}")
        print(f"Количество записей: {len(table_data)}")

    elif command in ("update", "delete"):
        if command == "update":
            validate_fields(schema, payload)

            if ID_COLUMN in payload:
                raise ValueError("Изменение ID запрещено")

        affected_records = select(table_data, where_clause)

        if affected_records is None:
            return

        if not affected_records:
            print("Подходящие записи не найдены")
            return

        if command == "update":
            result = update(table_data, payload, where_clause)
        else:
            result = delete(table_data, where_clause)

        if result is None:
            return

        save_table_data(table_name, result)
        clear_select_cache()

        for record in affected_records:
            record_id = record[ID_COLUMN]

            if command == "update":
                print(
                    f"Запись с ID={record_id} в таблице "
                    f'"{table_name}" успешно обновлена.'
                )
            else:
                print(
                    f"Запись с ID={record_id} успешно удалена "
                    f'из таблицы "{table_name}".'
                )