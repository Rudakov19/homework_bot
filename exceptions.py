class NotSendTelegram(Exception):
    """Базовый класс для исключений, которые не нужно отправлять в Telegram."""

    pass


class ExceptionSendMessageError(NotSendTelegram):
    """Класс исключения при сбое отправки сообщения."""

    pass


class ExceptionStatusError(NotSendTelegram):
    """Класс исключения при не корректном статусе ответа."""

    pass


class ExceptionEmptyAnswer(NotSendTelegram):
    """Пустой ответ API"""

    pass


class ExceptionEnvironmentVariables(NotSendTelegram):
    """Ошибка в переменных окружения"""

    pass
