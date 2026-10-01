# Консольная БД

Учебное консольное приложение для работы с таблицами и записями.

## Требования

- Python 3.13 или выше
- uv

## Установка

```bash
git clone https://github.com/ArinaVinar/project2_Vinar_M26-555.git
cd REPOSITORY
uv sync
```

## Запуск

```bash
uv run database
```

Или:

```bash
make run
```

## Проверка кода

```bash
make lint
```

## Сборка

```bash
make build
```

## Управление таблицами

Поддерживаемые типы столбцов: `int`, `str`, `bool`.

Столбец `ID:int` добавляется автоматически и располагается первым.
Структура таблиц сохраняется в файле `db_meta.json` в текущей
рабочей директории и доступна после повторного запуска программы.

Доступные команды:

- `create_table <имя> <столбец:тип> ...` - создать таблицу.
- `list_tables` - показать список таблиц.
- `drop_table <имя>` - удалить таблицу.
- `help` - показать справку.
- `exit` - завершить работу.

Пример:

```text
create_table users name:str age:int is_active:bool
list_tables
drop_table users
exit
```