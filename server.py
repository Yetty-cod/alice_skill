import random

from flask import Flask, request, jsonify
import logging


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    '''
    Функция для ответа Алисе
    :return:
    '''
    logging.info(f'Request: {request.json!r}')
    # создаём ответ на основе запроса Алисы
    response = make_response(request.json)
    logging.info(f'Response:  {response!r}')

    return jsonify(response)


def make_response(req):
    '''
    Функция создаёт ответ в зависимости от запроса
    :param req: json
    :return: сформированный словарь с ответом
    '''
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests_elephant': ['Не хочу!', 'Отстань!', 'Не буду!', 'Мне не нужен слон!'],
            'suggests_rabbit': ['Не хочу!', 'Отстань!', 'Не буду!', 'Мне не нужен кролик!'],
            'elephant_bought': False,
            'rabbit_bought': False
        }
        response['response']['text'] = 'Привет! Купи слона!'
        response['response']['buttons'] = get_suggests(user_id)
    else:
        if any([el in req['request']['original_utterance'].lower()
                for el in ['ладно', 'куплю', 'покупаю', 'хорошо']]):
            if sessionStorage[user_id]['elephant_bought'] is False:
                response['response']['text'] = 'Найти слона можно в Яндекс.Маркете!\n' \
                                               'А теперь купи кролика!'
                sessionStorage[user_id]['elephant_bought'] = True

                response['response']['buttons'] = get_suggests(user_id)
                return response
            else:
                response['response']['text'] = 'Найти кролика можно в Яндекс.Маркете!'
                sessionStorage[user_id]['rabbit_bought'] = True

                response['response']['end_session'] = True
                return response
        else:
            if sessionStorage[user_id]['elephant_bought'] is False:
                response['response']['text'] = f'Все говорят \'{req["original_utterance"]}\', а ты купи слона!'
            else:
                response['response']['text'] = f'Все говорят \'{req["original_utterance"]}\', а ты купи кролика!'

            response['response']['buttons'] = get_suggests(user_id)
            return response


def get_suggests(user_id):
    '''
    Функция возвращает 2 случайные подсказки и удаляет их из списка
    :param user_id: id пользователя
    :return: 2 подсказки в виде словаря с параметрами
    '''
    if sessionStorage[user_id]['elephant_bought'] is False:
        animal = 'suggest_elephant'
    else:
        animal = 'suggest_rabbit'

    suggests = random.choices(sessionStorage[user_id][animal], 2)
    if len(sessionStorage[user_id][animal]) < 2:
        sessionStorage[user_id][animal].extend(['Ладно', 'Куплю'])

    suggests = [{'title': title, 'hide': True} for title in suggests]

    return suggests


if __name__ == '__main__':
    app.run()
