import os
import time
from dotenv import load_dotenv
import requests
import logging
from telebot import TeleBot

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
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def get_api_answer(timestamp):
    try:
        params = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        return response.json()
    except requests.exceptions.RequestException as error:
        logging.error(f'Ошибка при запросе к единстевнному эндпоинту API: {error}')
        


def check_response(response):
    if isinstance(response, dict) and isinstance(response['homeworks'], list):
        return response.json()
    else:
        logging.error(f'на соответствие документации из урока «API сервиса Практикум Домашка»')

def parse_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'approved':
        verdict = HOMEWORK_VERDICTS['approved']
    elif homework['status'] == 'reviewing':
        verdict = HOMEWORK_VERDICTS['reviewing']
    elif homework['status'] == 'rejected':
        verdict = HOMEWORK_VERDICTS['rejected']
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    check_tokens()

    # Создаем объект класса бота
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = 0
    status = get_api_answer(timestamp)
    status = status['homeworks'][-1]['status']

    while True:
        try:
            
            check_tokens()
            homeworks = get_api_answer(timestamp)
            homework_status = homeworks['homeworks'][-1]['status']
            if homework_status != status:
                a = parse_status(homeworks['homeworks'][-1])
                send_message(bot, a)
                status = homeworks['homeworks'][-1]['status']
                timestamp = int(time.time())
            time.sleep(30)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(30)
      
    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
