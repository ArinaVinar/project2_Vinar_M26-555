import shlex


def tokenize(user_input):
    """Разбивает команду на токены, сохраняя кавычки строковых значений."""
    lexer = shlex.shlex(
        user_input,
        posix=False,
        punctuation_chars="(),=",
    )
    lexer.whitespace_split = True
    lexer.commenters = ""

    tokens = []

    for token in lexer:
        if all(char in "(),=" for char in token):
            tokens.extend(token)
        else:
            tokens.append(token)

    return tokens


def parse_value(token):
    """Преобразует токен в строку, целое число или логическое значение."""
    if len(token) >= 2 and token[0] in ("'", '"') and token[-1] == token[0]:
        return token[1:-1]

    if token.lower() == "true":
        return True

    if token.lower() == "false":
        return False

    try:
        return int(token)
    except ValueError:
        raise ValueError(f"{token}; строки должны быть в кавычках") from None


def parse_values(tokens):
    """Разбирает значения в круглых скобках, разделённые запятыми."""
    if len(tokens) < 2 or tokens[0] != "(" or tokens[-1] != ")":
        raise ValueError("values должны быть в круглых скобках")

    inner_tokens = tokens[1:-1]

    if not inner_tokens:
        return []

    if len(inner_tokens) % 2 == 0:
        raise ValueError("Неверный список values")

    values = []

    for index, token in enumerate(inner_tokens):
        if index % 2 == 1:
            if token != ",":
                raise ValueError("Значения должны разделяться запятыми")
        else:
            values.append(parse_value(token))

    return values


def parse_assignments(tokens):
    """Преобразует присваивания столбец = значение в словарь."""
    if not tokens or len(tokens) % 4 != 3:
        raise ValueError("Ожидается столбец = значение")

    assignments = {}

    for index in range(0, len(tokens), 4):
        column_name = tokens[index]

        if not column_name.isidentifier():
            raise ValueError(column_name)

        if tokens[index + 1] != "=":
            raise ValueError("Ожидается знак =")

        if column_name in assignments:
            raise ValueError(f"Повтор столбца {column_name}")

        assignments[column_name] = parse_value(tokens[index + 2])

        if index + 3 < len(tokens) and tokens[index + 3] != ",":
            raise ValueError("Присваивания должны разделяться запятыми")

    return assignments


def parse_where(tokens):
    """Разбирает одно условие равенства и возвращает словарь."""
    if len(tokens) != 3:
        raise ValueError("Where должен содержать столбец = значение")

    return parse_assignments(tokens)


def parse_data_command(tokens):
    """Возвращает имя таблицы, данные операции и условие из команды."""
    command = tokens[0]

    if command == "insert":
        if (
            len(tokens) < 6
            or tokens[1] != "into"
            or tokens[3] != "values"
        ):
            raise ValueError(
                "Ожидается insert into <таблица> values (...)"
            )

        return tokens[2], parse_values(tokens[4:]), None

    if command in ("select", "delete"):
        if len(tokens) < 3 or tokens[1] != "from":
            raise ValueError(f"Ожидается {command} from <таблица>")

        if command == "select" and len(tokens) == 3:
            return tokens[2], None, None

        if len(tokens) < 4 or tokens[3] != "where":
            raise ValueError("Ожидается where <столбец> = <значение>")

        return tokens[2], None, parse_where(tokens[4:])

    if command == "update":
        if len(tokens) < 4 or tokens[2] != "set":
            raise ValueError("Ожидается update <таблица> set ... where ...")

        try:
            where_index = tokens.index("where", 3)
        except ValueError:
            raise ValueError("Для update требуется where") from None

        set_clause = parse_assignments(tokens[3:where_index])
        where_clause = parse_where(tokens[where_index + 1:])
        return tokens[1], set_clause, where_clause

    if command == "info":
        if len(tokens) != 2:
            raise ValueError("Ожидается info <таблица>")

        return tokens[1], None, None

    raise ValueError(command)