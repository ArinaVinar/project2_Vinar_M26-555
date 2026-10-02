import time


def handle_db_errors(func):
    """Оборачивает функцию обработкой ошибок базы данных."""
    def wrapper(*args, **kwargs):
        """Выполняет функцию и возвращает None при обработанной ошибке."""
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: файл данных не найден")
        except KeyError as error:
            print(f"Ошибка: таблица или столбец {error} не найден")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except OSError as error:
            print(f"Ошибка работы с файлами: {error}")

        return None

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def confirm_action(action_name):
    """Создаёт декоратор подтверждения указанного действия."""
    def decorator(func):
        """Добавляет запрос подтверждения перед вызовом функции."""
        def wrapper(*args, **kwargs):
            """Выполняет действие при ответе y, иначе возвращает None."""
            answer = input(
                f"Вы уверены, что хотите выполнить `{action_name}`? [y/n]: "
            )
            if answer != "y":
                print("Операция отменена")
                return None

            return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


def log_time(func):
    """Добавляет измерение и вывод времени выполнения функции."""
    def wrapper(*args, **kwargs):
        """Вызывает функцию и выводит длительность её выполнения."""
        started_at = time.monotonic()

        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - started_at
            print(
                f"Функция {func.__name__} выполнилась "
                f"за {elapsed:.3f} секунд"
            )

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def create_cacher():
    """Создаёт функцию кэширования со словарём в замыкании."""
    cache = {}

    def cache_result(key, value_func):
        """Возвращает результат из кэша или вычисляет и сохраняет его."""
        if key not in cache:
            cache[key] = value_func()

        return cache[key]

    def clear_cache():
        """Удаляет все результаты из кэша."""
        cache.clear()

    cache_result.clear = clear_cache
    return cache_result