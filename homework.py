# type: ignore
import os
import time
from dotenv import load_dotenv
import requests
import logging
from telebot import TeleBot
import telebot
import sys
from logging.handlers import RotatingFileHandler
from exceptions.exception import APIError, StatusCodeError, NotTokenError
from http import HTTPStatus

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


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if not TELEGRAM_TOKEN or not PRACTICUM_TOKEN or not TELEGRAM_CHAT_ID:
        logging.critical(
            'Отсутствует обязательная переменная окружения')
        raise NotTokenError('Отстутсвует обязательная переменная окружения')
    return True


def send_message(bot, message):
    """Отправляет сообщение боту."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug(f'Сообщение успешно отправлено в телеграмм: {message}')
    except (telebot.apihelper.ApiException, requests.RequestException)as error:
        logging.error(f'Ошибка при отправке сообщения в телеграмм: {error}')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    try:
        params = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            logging.error(f'API вернул код {response.status_code}')
            raise StatusCodeError('Ошибка при запросе к API')
        return response.json()
    except requests.exceptions.RequestException as error:
        logging.error(f'Ошибка при запросе к API: {error}')
        raise APIError(f'Ошибка при запросе к API: {error}')


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является словарем')

    if 'homeworks' not in response:
        raise KeyError('В ответе API домашки нет ключа homeworks')

    if not isinstance(response['homeworks'], list):
        raise TypeError('Ключ homeworks в ответе API не является списком')

    return response['homeworks']


def parse_status(homework):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    if 'homework_name' not in homework:
        raise KeyError('В ответе API нет ключа homework_name')
    if 'status' not in homework:
        raise KeyError('В ответе API нету ключа status')

    homework_name = homework['homework_name']
    status = homework['status']

    if status not in HOMEWORK_VERDICTS:
        raise KeyError(f'Неизвестный статус домашней работы: {status}')
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    previous_status = None
    try:
        check_tokens()
    except Exception as error:
        logging.critical(f'Программа принудительно остановлена: {error}')
        sys.exit(1)

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            current_status = None
            if homeworks:
                homework = homeworks[-1]
                current_status = homework.get('status')
                if current_status and current_status != previous_status:
                    message = parse_status(homework)
                    send_message(bot, message)
                    previous_status = current_status
                    logging.info('Сообщение отправлено в Telegram')
                else:
                    logging.debug('Статус домашней работы не изменился')
            else:
                logging.debug('Нет домашних работ для проверки')
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            message = f'Сбой в программе: {error}'
            logging.error(message)
            send_message(bot, message)
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='program.log'
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        'my_logger.log', maxBytes=50000000, backupCount=5)
    logger.addHandler(handler)
    main()
