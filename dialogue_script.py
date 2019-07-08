# прототип ассистента + распознавание речи пациента на Yandex Speech Kit + проход по веткам диалога
import speech_recognition as sr
import subprocess as sp
from token_folder import IAM_TOKEN, FOLDER_ID, URL
import json
import requests

replies_resolution = {
    "да": "Я передала медсестре вашу просьбу. Подождите, ближайшее время она к вам подойдет",
    "пока": "Если вам что-то понадобится, обращайтесь"
}   # точка завершения диалога, когда проблема определена. Отсюда идет уведомление сестре

replies_no_continue = [
    # "У вас острая боль?",
    "Вы хотите пить?",
    "Вам нужна помощь санитара?",
    "Вы хотите увидеться с родными или друзьями?",
    "Включить телевизор?",
    "Вашего вопроса нет в моем каталоге. Ожидайте медсестру"
]

def say(text_to_speech):
    sp.call(['say', text_to_speech])  # 'оболочка' от MacOS (озвучивает печатный текст)


def main():
    say("Добрый день. Это голосовой ассистент и я постараюсь вам помочь. Для завершения беседы скажите ПОКА. \
    Я буду задавать вопросы, на которые вам нужно отвечать ДА либо НЕТ. У вас острая боль?") # произносится 1 раз в начале
    for reply in replies_no_continue:  # цикл вопросов-ответов
        rec = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:     # забираем звук с микрофона
            rec.adjust_for_ambient_noise(source, duration=0.3)  # нейтрализация шумов при передаче аудио на распознавание, 0.5 секунды на калибровку
            audio = rec.listen(source, phrase_time_limit=1.2)    # "слушаем" входящий звук, 1.2 секунды длится запись ответа пациента (от начала звучания)
            audioData = audio.get_flac_data()   # конвертируем звук в формат 'flac' (SpeechKit принимает flac или ogg)

        def recognize(audioData):
            headers = {"Authorization": "Bearer " + IAM_TOKEN}
            params = {          # параметры для распознавания речи
                "topic": "general",
                "folderId": FOLDER_ID,
                "lang": "ru-RU"
            }
            resp = requests.post(URL, params=params, data=audioData, headers=headers)  # получаем расшифровку через запрос requests.post()
            respDict = json.loads(resp.content.decode('UTF-8'))  # декодируем содержимое расшифровки -> превращаем json 'string' в python 'dict'
            print(respDict.get('result'))   # рабочий инструмент для проверки, корректно ли исполняется код
            return respDict.get('result')  # def возвращает значение ключа 'result' (т е текст, сгенерированный из речи)
        response = recognize(audioData)  # кладем результат функции recognize(audioData) в переменную для развития диалога

        if response == "да":  # условия прохода по циклу
            say(replies_resolution.get("да"))  # триггер отправки уведомления медсестре
            break
        elif response == "нет":
            say(reply)
        elif response == "пока":
            say(replies_resolution.get("пока"))
            break


if __name__ == '__main__':
    main()

