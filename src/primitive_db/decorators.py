import time


def handle_db_errors(func):
    def wrapper(*args, **kwargs):
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
    def decorator(func):
        def wrapper(*args, **kwargs):
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
    def wrapper(*args, **kwargs):
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
    cache = {}

    def cache_result(key, value_func):
        if key not in cache:
            cache[key] = value_func()

        return cache[key]

    def clear_cache():
        cache.clear()

    cache_result.clear = clear_cache
    return cache_result