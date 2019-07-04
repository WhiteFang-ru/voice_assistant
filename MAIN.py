# Реализовать прототип голосового помощника без функции распознавания на русском языке
# Реализовать функцию распознавания на Yandex Speech Kit

import speech_recognition as sr
import subprocess as sp
from token_folder import IAM_TOKEN
from token_folder import FOLDER_ID
import json
import requests

replies = {
    "да/нет": "Вы хотите пить?",
    "хватит": "Если вам что-то понадобится, обращайтесь."
}   # сочетания ответ-вопрос

choices = ['да', 'нет']  # варианты ответов пациента

def say(text_to_speech):
    sp.call(['say', text_to_speech])  # 'оболочка' от MacOS (озвучивает печатный текст)


def recognize(audioData):
    URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?"  # API STT - преобразование речи в текст
    headers = {"Authorization": "Bearer " + IAM_TOKEN}
    params = {          # параметры для распознавания речи
        "topic": "general",
        "folderId": FOLDER_ID,
        "lang": "ru-RU"
    }
    resp = requests.post(URL, params=params, data=audioData, headers=headers)  # получаем расшифровку через запрос requests.post()
    decoded = resp.content.decode('UTF-8')  # декодируем содержимое расшифровки
    respDict = json.loads(decoded)  # превращаем json 'string' в python 'dict'
    print(respDict.get('result'))   # рабочий инструмент для проверки, корректно ли исполняется код
    return respDict.get('result')  # def возвращает значение ключа 'result' (т е текст, сгенерированный из речи)

def main():
    say('Добрый день. Это голосовой ассистент. Я могу вам чем-то помочь? Ответьте "даа" илии "нет".') # произносится 1 раз в начале

    while True:  # бесконечный цикл диалога
        rec = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:     # забираем звук с микрофона
            rec.adjust_for_ambient_noise(source, duration=0.5)  # нейтрализация шумов при передаче аудио на распознавание, 0.5 секунды на калибровку
            audio = rec.listen(source, phrase_time_limit=1.1)    # "слушаем" входящий звук, 1.1 секунды длится запись ответа пациента (от начала звучания)
            audioData = audio.get_flac_data()   # конвертируем звук в формат 'flac' (SpeechKit принимает flac или ogg)

        response = recognize(audioData)  # кладем результат функции recognize(audioData) в переменную для развития диалога

        if response in choices:  # сопоставляем ответы пациента со списокм choices
            say(replies.get('да/нет'))  # если ответ "да" или "нет", цикл продолжаем
        elif response == "хватит":  # выход из цикла while
            say(replies.get("хватит"))
            break


if __name__ == '__main__':
    main()

