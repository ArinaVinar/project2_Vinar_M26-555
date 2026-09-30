import prompt


def print_help():
    print("База данных")
    print("Функции:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def welcome():
    print_help()

    while True:
        command = prompt.string("Введите команду: ").strip()

        if command == "exit":
            break
        if command == "help":
            print_help()
        else:
            print(f"Функции {command} нет. Попробуйте снова")