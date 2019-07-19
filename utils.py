# прототип ассистента + распознавание речи пациента на Yandex Speech Kit + проход по веткам диалога
# + синтезированные вопросы от помощника
import speech_recognition as sr
import simpleaudio as sa
from config import IAM_TOKEN, FOLDER_ID, URL_STT, URL_TTS, control_points, replies_continue, needs
import json
import requests


def synthesize():
    headers = {"Authorization": "Bearer {}".format(IAM_TOKEN)}
    text = 'Если вам что-то понадобится, обращайтесь'
    data = {
        'text': text,
        'lang': 'ru-RU',
        'folderId': FOLDER_ID
    }
    # print(text)
    with requests.post(URL_TTS, headers=headers, data=data, stream=True) as resp:
        if resp.status_code != 200:
            raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))
        with open('welcome_back.ogg', "wb") as f:
            f.write(resp.content)
    # print(resp)
# synthesize()


def play_sound(path_to_wav):   # воспроизведение предзаписанных аудио-вопросов
    wave_obj = sa.WaveObject.from_wave_file(path_to_wav)
    play_obj = wave_obj.play()
    play_obj.wait_done()


def main():
    play_sound(control_points.get("начало"))
    index_n = 0
    tasks = []  #  список задачек для выгрузки напрямую в приложение, минуя БД
    for reply in replies_continue:  # цикл вопросов-ответов
        response = recognize()  # вызываем функцию recognize() через переменную для развития диалога
        if response == "да":
            print(needs[index_n])  # 1-я и последующие записи в задачках для медсестры
            tasks.append(needs[index_n])
            play_sound(control_points.get("еще"))
            response_more = recognize()
            if response_more == "нет":
                play_sound(control_points.get("больше_ничего"))
                break
            elif response_more == "да":
                play_sound(reply)
        elif response == "нет":
            play_sound(reply)
        elif response == "пока":
            play_sound(control_points.get("пока"))
            break
        index_n += 1  # переходим к следующей записи в 'needs'
    print(tasks)


def recognize():
    headers = {"Authorization": "Bearer {}".format(IAM_TOKEN)}
    params = {  # параметры для распознавания речи
        "topic": "general",
        "folderId": FOLDER_ID,
        "lang": "ru-RU"
    }
    rec = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:  # забираем звук с микрофона
        rec.adjust_for_ambient_noise(source, duration=0.3)  # нейтрализация шумов при передаче аудио
                                                    # на распознавание, 0.5 секунды на калибровку
        audio = rec.listen(source, phrase_time_limit=1.2)  # "слушаем" входящий звук, 1.2 секунды
                                        #  длится запись ответа пациента (от начала звучания)
        audioData = audio.get_flac_data()  # конвертируем звук в формат flac: SpeechKit принимает flac/ogg
    resp = requests.post(URL_STT, params=params, data=audioData, headers=headers)
                                            # получаем расшифровку через запрос requests.post()
    respDict = json.loads(resp.content.decode('UTF-8'))  # декодируем содержимое расшифровки
                                                # -> превращаем json 'string' в python 'dict'
    # print(respDict.get('result'))  # рабочий инструмент для проверки, корректно ли исполняется код
    return respDict.get('result')  # возвращает значение ключа 'result' (т е текст, сгенерированный из речи)



if __name__ == '__main__':
    main()



