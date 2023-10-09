import logging
import os
import time
import sys
from http import HTTPStatus

import telegram
import requests
from dotenv import load_dotenv

from exceptions import (NotSendTelegram, ExceptionGetAPYError,
                        ExceptionEmptyAnswer, ExceptionStatusError,
                        ExceptionEnvironmentVariables,
                        ExceptionSendMessageError)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
fileHandler = logging.FileHandler("logfile.log", encoding='utf-8')
streamHandler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(module)s - %(lineno)d - '
    '%(funcName)s - %(levelname)s - %(message)s'
)
logger.setLevel(logging.DEBUG)
streamHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
logger.addHandler(fileHandler)


def check_tokens():
    """Проверяет доступность переменных окружения."""

    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""

    try:
        logger.debug("Начало отправки сообщения в Telegram чат")
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.Unauthorized:
        raise ExceptionSendMessageError(
            'Сбой при отправке сообщения в чат Telegram: '
            'у бота недостаточно прав для отправки сообщения в заданный чат.'
        )
    except telegram.error.InvalidToken as error:
        raise ExceptionSendMessageError(
            'Сбой при отправке сообщения в чат Telegram: '
            f'ошибка в токене Telegram-бота - "{error}".'
        )
    except telegram.error.NetworkError as error:
        raise ExceptionSendMessageError(
            'Сбой при отправке сообщения в чат Telegram: '
            f'ошибка сетевого подключения - "{error}".'
        )

    logger.debug(f"В Telegram отправлено сообщение '{message}'")


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""

    params = {'from_date': timestamp}
    requests_params = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': params
    }
    try:
        logger.info("Запрос к эндпоинту '{url}' API-сервиса "
                    "c параметрами {params}".format(**requests_params))
        response = requests.get(**requests_params)
        if response.status_code != HTTPStatus.OK:
            message = (f"Сбой в работе программы: Эндпоинт {ENDPOINT} c "
                       f"параметрами {requests_params} недоступен. status_code"
                       f": {response.status_code}, reason: {response.reason}, "
                       f"text: {response.text}")
            raise ExceptionStatusError(message)
    except requests.RequestException:
        raise ExceptionStatusError(
            "Url недоступен"
        )
    except Exception as error:
        raise ExceptionGetAPYError(
            "Cбой при запросе к энпоинту '{url}' API-сервиса с "
            "параметрами {params}.".format(**requests_params),
            f"Error: {error}"
        )
    return response.json()


def check_response(response):
    """Проверяет ответ API на соответствие."""

    logger.info("Проверка ответа API на корректность")
    if not isinstance(response, dict):
        message = (f"Ответ API получен в виде {type(response)}, "
                   "а должен быть словарь")
        raise TypeError(message)
    keys = ['current_date', 'homeworks']
    for key in keys:
        if key not in response:
            message = f"В ответе API нет ключа {key}"
            raise ExceptionEmptyAnswer("Пустой ответ API")
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        message = (f"API вернул {type(homeworks)} под ключом homeworks, "
                   "а должен быть список")
        raise TypeError(message)
    return homeworks


def parse_status(homework):
    """Извлекает информацию о статусе домашней работы."""

    logger.info("Извлечение из конкретной домашней работы статуса этой работы")
    if "homework_name" not in homework:
        message = "В словаре homework не найден ключ homework_name"
        raise KeyError(message)
    homework_name = homework.get('homework_name')
    if "status" not in homework:
        message = "В словаре homework не найден ключ status"
        raise KeyError(message)
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        message = (
            f"В словаре HOMEWORK_VERDICTS не найден ключ {homework_status}")
        raise KeyError(message)
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """
    Основная логика работы бота.
    1. Сделать запрос к API.
    2. Проверить ответ.
    3. Если есть обновления — получить статус работы из
    обновления и отправить сообщение в Telegram.
    4. Подождать некоторое время и вернуться в пункт 1.
    """
    if not check_tokens():
        logger.critical('Ошибка в переменных окружения')
        raise ExceptionEnvironmentVariables('Ошибка в переменных окружения')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = 0
    old_status = None

    while True:
        try:
            response = get_api_answer(timestamp)
            timestamp = response.get('current_date')
            homework = check_response(response)
            if homework:
                new_status = parse_status(homework[0])
            else:
                new_status = 'За данный период времени нет сведений.'
            if old_status != new_status:
                old_status = new_status
                send_message(bot, old_status)
            else:
                logger.debug("В ответе API отсутсвуют новые статусы")
        except NotSendTelegram as error:
            new_status = f'Сбой в работе программы: {error}'
            logger.error(new_status)
        except Exception as error:
            new_status = f'Сбой в работе программы: {error}'
            logger.error(new_status)
            if not issubclass(error.__class__, NotSendTelegram):
                if new_status != old_status:
                    send_message(bot, new_status)
                    old_status = new_status

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
