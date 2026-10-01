import json
import shlex

import prompt

from primitive_db.constants import META_FILE
from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata


def print_help():
    print("База данных")
    print("Функции:")
    print("<command> create_table <имя таблицы> "
          "<столбец1:тип> <столбец2:тип> ... - создать таблицу")
    print("<command> list_tables - вывод списка всех таблиц")
    print("<command> drop_table <имя таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def run_command(metadata, args):
    command = args[0]
    arguments = args[1:]

    if command == "create_table":
        if len(arguments) < 2:
            raise ValueError("Ожидается имя таблицы и столбцы")

        table_name = arguments[0]
        columns = arguments[1:]
        result = create_table(metadata, table_name, columns)

        if result is not  None:
            save_metadata(META_FILE, result)
            columns_text = ", ".join(
                f"{name}:{data_type}" for name, data_type in result[table_name].items()
            )
            print(f"Таблица `{table_name}` создана со столбцами: {columns_text}")

    elif command == "drop_table":
        if len(arguments) != 1:
            raise  ValueError("Ожидается одно имя таблицы")

        table_name = arguments[0]
        result = drop_table(metadata, table_name)

        if result is not None:
            save_metadata(META_FILE, result)
            print(f"Таблица {table_name} удалена")

    elif command == "list_tables":
        if arguments:
            raise ValueError(" ".join(arguments))

        list_tables(metadata)

    elif command == "help":
        if arguments:
            raise ValueError(" ".join(arguments))

        print_help()

    else:
        print(f"Функция {command} не существует. Попробуйте снова")

def run():
    print_help()

    while True:
        try:
            metadata = load_metadata(META_FILE)
        except json.JSONDecodeError:
            print(f"Ошибка. {META_FILE} некорректный JSON")
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
            args = shlex.split(user_input)
            if not args:
                continue
            if args[0] == "exit":
                if len(args) != 1:
                    raise ValueError(" ".join(args[1:]))
                return

            run_command(metadata, args)

        except ValueError as error:
            print(f"Некорректное значение: {error}. Попробуйте снова")
        except OSError as error:
            print(f"Ошибка сохранения метаданных: {error}")