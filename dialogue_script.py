# прототип ассистента + распознавание речи пациента на Yandex Speech Kit + проход по веткам диалога
import speech_recognition as sr
# import subprocess as sp
from token_folder import IAM_TOKEN, FOLDER_ID, URL_STT, URL_TTS
import json
import requests


def synthesize(FOLDER_ID, IAM_TOKEN, text):
    headers = {
        'Authorization': 'Bearer ' + IAM_TOKEN,
    }

    data = {
        'text': text,
        'lang': 'ru-RU',
        'folderId': FOLDER_ID
    }

    print(text)

    with requests.post(URL_TTS, headers=headers, data=data) as resp:
        if resp.status_code != 200:
            raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))

    print(resp)

    with open("tmp.flac", "wb") as f:
        f.write(resp.content)

    # save file to some_file.ogg
    # subprocess.call(["open", "some_file.ogg"])  # этот способ работает на любом локальном устройстве, но он занимает время

    # return resp.content  # это будет звук в байтах сразу целиком, байты нужно сохранить и озвучить


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

# def say(text_to_speech):
#     sp.call(['say', text_to_speech])  # 'оболочка' от MacOS (озвучивает печатный текст)


def recognize(audioData):
    headers = {"Authorization": "Bearer " + IAM_TOKEN}
    params = {  # параметры для распознавания речи
        "topic": "general",
        "folderId": FOLDER_ID,
        "lang": "ru-RU"
    }
    resp = requests.post(URL_STT, params=params, data=audioData,
                         headers=headers)  # получаем расшифровку через запрос requests.post()
    respDict = json.loads(
        resp.content.decode('UTF-8'))  # декодируем содержимое расшифровки -> превращаем json 'string' в python 'dict'
    print(respDict.get('result'))  # рабочий инструмент для проверки, корректно ли исполняется код
    return respDict.get('result')  # def возвращает значение ключа 'result' (т е текст, сгенерированный из речи)


def main():
    synthesize(FOLDER_ID, IAM_TOKEN, text="Добрый день") #. Это голосовой ассистент и я постараюсь вам помочь. Для завершения беседы скажите ПОКА. \
    # Я буду задавать вопросы, на которые вам нужно отвечать ДА либо НЕТ. У вас острая боль?") # произносится 1 раз в начале
    for reply in replies_no_continue:  # цикл вопросов-ответов
        rec = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:     # забираем звук с микрофона
            rec.adjust_for_ambient_noise(source, duration=0.3)  # нейтрализация шумов при передаче аудио на распознавание, 0.5 секунды на калибровку
            audio = rec.listen(source, phrase_time_limit=1.2)    # "слушаем" входящий звук, 1.2 секунды длится запись ответа пациента (от начала звучания)
            audioData = audio.get_flac_data()   # конвертируем звук в формат 'flac' (SpeechKit принимает flac или ogg)

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
