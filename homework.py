import os
from dotenv import load_dotenv
import requests
import logging

load_dotenv()


PRACTICUM_TOKEN = 'PRACTICUM_TOKEN'
TELEGRAM_TOKEN = 'TELEGRAM_TOKEN'
TELEGRAM_CHAT_ID = 'TELEGRAM_CHAT_ID'

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}



HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def check_tokens():
    try:
        requests.get(ENDPOINT)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')


def send_message(bot, message):
    ...


def get_api_answer(timestamp):
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params={'timestamp': timestamp})
        return response.json()
    except requests.exceptions.RequestException as error:
        logging.error(f'Ошибка при запросе к единстевнному эндпоинту API: {error}')
        


def check_response(response):
    ...


def parse_status(homework):
    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    ...

    # Создаем объект класса бота
    bot = ...
    timestamp = int(time.time())

    ...

    while True:
        try:

            ...

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
        ...


if __name__ == '__main__':
    main()
