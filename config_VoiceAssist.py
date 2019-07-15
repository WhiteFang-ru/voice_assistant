# прототип ассистента + распознавание речи пациента на Yandex Speech Kit + проход по веткам диалога + синтезированные
# вопросы от помощника
import speech_recognition as sr
import simpleaudio as sa
from token_folder import IAM_TOKEN, FOLDER_ID, URL_STT, URL_TTS
import json
import requests


replies_resolution = {
           "начало": 'synthesized_audio/intro_and_pain.wav',  # интро + у вас острая боль?
              "еще": 'synthesized_audio/anything_else.wav',  # "вам нужно что-то еще?",
    "больше_ничего": "synthesized_audio/resolved_wait.wav",  # "Я передала медсестре вашу просьбу, она к вам подойдет”
             "пока": "synthesized_audio/welcome_back.wav"  # “Если вам что-то понадобится, обращайтесь”
}

replies_continue = [
    'synthesized_audio/drink.wav', # "Вы хотите пить?",
    'synthesized_audio/male_nurse_assist.wav',  # "Вам нужна помощь санитара?",
    'synthesized_audio/meet_visitors.wav',  # "Вы хотите увидеться с родными или друзьями?",
    'synthesized_audio/TV_on.wav',  # "Включить телевизор?",
    'synthesized_audio/unresolved.wav'  # "Вашего вопроса нет в моем каталоге. Ожидайте медсестру"
]  # если пройден весь цикл, обязательно отправляем уведомление

def simple(path_to_wav):
    wave_obj = sa.WaveObject.from_wave_file(path_to_wav)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def main():
    simple(replies_resolution.get("начало"))

    for reply in replies_continue:  # цикл вопросов-ответов
        response = recognize()  # вызываем функцию recognize() через переменную для развития диалога
        if response == "да":    # 1-я и последующие записи в уведомлении
            simple(replies_resolution.get("еще"))
            response_more = recognize()
            if response_more == "нет":
                simple(replies_resolution.get("больше_ничего"))  # триггер отправки уведомления медсестре
                break
            elif response_more == "да":
                simple(reply)
        elif response == "нет":
            simple(reply)
        elif response == "пока":
            simple(replies_resolution.get("пока"))
            break

def recognize():
    headers = {"Authorization": "Bearer " + IAM_TOKEN}
    params = {  # параметры для распознавания речи
        "topic": "general",
        "folderId": FOLDER_ID,
        "lang": "ru-RU"
    }
    rec = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:  # забираем звук с микрофона
        rec.adjust_for_ambient_noise(source,
                                     duration=0.3)  # нейтрализация шумов при передаче аудио на распознавание, 0.5 секунды на калибровку
        audio = rec.listen(source,
                           phrase_time_limit=1.2)  # "слушаем" входящий звук, 1.2 секунды длится запись ответа пациента (от начала звучания)
        audioData = audio.get_flac_data()  # конвертируем звук в формат 'flac' (SpeechKit принимает flac или ogg)
    resp = requests.post(URL_STT, params=params, data=audioData,
                         headers=headers)  # получаем расшифровку через запрос requests.post()
    respDict = json.loads(
        resp.content.decode('UTF-8'))  # декодируем содержимое расшифровки -> превращаем json 'string' в python 'dict'
    print(respDict.get('result'))  # рабочий инструмент для проверки, корректно ли исполняется код
    return respDict.get('result') # def возвращает значение ключа 'result' (т е текст, сгенерированный из речи)


if __name__ == '__main__':
    main()


