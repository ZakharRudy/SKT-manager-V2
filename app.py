from flask import Flask, request, jsonify
import requests
import openai
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()

app = Flask(__name__)

# Получение ключа API из переменных окружения
openai.api_key = os.getenv("OPENAI_API_KEY")

# API ключ ManyChat
manychat_api_key = "1460830:3d03299b00dc535fb6553bb3dacacfb9"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    user_message = data['message']['text']
    user_id = data['subscriber_id']

    # Создаем поток для каждого уникального пользователя
    thread_id = get_or_create_thread(user_id)

    # Получаем ответ от ассистента
    ai_response = get_ai_response(user_message, thread_id)

    # Отправляем ответ обратно в ManyChat
    send_message_to_manychat(user_id, ai_response)

    return jsonify({"status": "success"})

def get_or_create_thread(user_id):
    # Здесь должна быть логика для создания или получения существующего потока
    # Мы будем использовать имя пользователя в качестве идентификатора потока
    thread_id = f"thread-{user_id}"
    return thread_id

def get_ai_response(user_message, thread_id):
    response = openai.Assistant.create(
        assistant_id="asst_kRuRC9eN1pUGJ4obo8xX9pAj",
        input={"text": user_message},
        thread_id=thread_id
    )
    ai_response = response['output']['text']
    return ai_response

def send_message_to_manychat(user_id, message):
    url = f"https://api.manychat.com/conversations/send"
    headers = {
        "Authorization": f"Bearer {manychat_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "subscriber_id": user_id,
        "message": {"text": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
