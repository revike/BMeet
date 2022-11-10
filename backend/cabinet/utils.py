import re


def username_check(value):
    """Проверка username"""
    regex = r"^[a-zA-Z]+[a-zA-Z0-9_-]*"
    username_regex = re.fullmatch(regex, value)
    if len(value) < 2 or not username_regex:
        return False
    return True


def password_check(value):
    """
        Валидация password:
            Не менее 8 знаков
            Одна буква верхнего регистра (A-Z)
            Одна буква нижнего регистра (a-z)
            Одна цифра (0-9)
            Один специальный знак (~!@#$%^...)

    """

    reg_password = r"^(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^\w\d\s])([^\s]){8,}$"
    return re.fullmatch(reg_password, value)
