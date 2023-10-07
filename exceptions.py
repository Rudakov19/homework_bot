class ExceptionSendMessageError(Exception):
    """Класс исключения при сбое отправки сообщения."""
    pass


class ExceptionStatusError(Exception):
    """Класс исключения при не корректном статусе ответа."""
    pass


class ExceptionGetAPYError(Exception):
    """Класс исключения при ошибке запроса к API."""
    pass


class ExceptionEmptyAnswer(Exception):
    """Пустой ответ API"""
    pass


class ExceptionEnvironmentVariables(Exception):
    """Ошибка в переменных окружения"""
    pass
