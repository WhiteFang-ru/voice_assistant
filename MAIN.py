# Реализовать прототип голосового помощника без функции распознавания на русском языке
# Реализовать функцию распознавания на Yandex Speech Kit

import speech_recognition as sr
import subprocess as sp
import json
import requests

replies = {
    "да/нет": "Вы хотите пить?",
    "хватит": "Если вам что-то понадобится, обращайтесь."
}   # сочетания ответ-вопрос

choices = ['да', 'нет']  # варианты ответов пациента

def say(text_to_speech):
    sp.call(['say', text_to_speech])  # 'оболочка' от MacOS (озвучивает печатный текст)

def main():
    say('Добрый день. Это голосовой ассистент. Я могу вам чем-то помочь? Ответьте "даа" иили "неет".') # произносится 1 раз в начале

    while True:  # бесконечный цикл диалога
        rec = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:     # забираем звук с микрофона
            rec.adjust_for_ambient_noise(source)  # нейтрализация шумов при передаче аудио на распознавание
            audio = rec.listen(source)    # "слушаем" входящий звук
            audioData = audio.get_flac_data()   # конвертируем звук в формат 'flac' (SpeechKit принимает flac или ogg)

        def recognize(audioData):
            FOLDER_ID = "b1g6qb3p8815ahts0o6c"  # Идентификатор каталога на YandexCloud, для использования API SpeechKit
            IAM_TOKEN = "CggaATEVAgAAABKABINpuOAV78ucrHVCyMwuWBny43cBgjDA4EpZUNR59c6hZsv6KM1am8BFCE2n1r5R8fmBo3ZjFPfD3uyNRqvHv4-5DETQB-xGhIEB_EpFKX6nuoLmcdMh_o0YxJlH18tLUz2xEj1MkK4fXzULDpBzhQrnqUnbK2lzE-lLOeEGOArvDDwuLH-_I9FV1kQHQkBDgoFtcKCr0lGLORhHm8AV0oEGByhv2GXEmyqWcEfgrOvXgqwpyY-piQCCxplFjA2EJu54OneEmCbP9Z-laZ-g31yWOhemx1NuocQ13NfIZ9V2XQicAcxmD4QSnlcvqGSO6qlpwt4KXrmmVWMHtxjkfffvOAz-9VrUrG6KuiDkp04zKkgDLgm150deI9yxV98aJiEqHxp3VQslRPyjgr8LwWzAM79rR71klg8VhZ0ygPD44uH5MIeKJeDAxUxaRt2EO6bTAeVhljV7-94CLiSaZsgFtS-5e8-89XPZd9QaG0-WsB-Kbx_H2TL_73reXSDyx0hcMjj5-UX32-Z0wpy2JkVCp8tcfaXXrreh6do-DSTFeH2rfWT24D12rY7cGKq867HV_Rag9Wk5Z6xqiM1YehP6PyEl9gmnc89aOjt15NwolpEuMA_GgDn_o1R9oxWAFfXbZxf7NTd4lfDHqMPQH9yXjJNfGMedF1lYoVct7zkAGmQKIGQ5ZjIzMmNjMDMxMDQ3M2E5MjVhMzlkYmZhNDgxMTRlEKTv8ugFGOTA9egFIiIKFGFqZXVqOXMybWczaTdnb3U5ZjhqEgptYXJpYS5rbHlrWgAwAjgBSggaATEVAgAAAFABIPME"
            URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?%s"  # API STT - преобразование речи в текст
            headers = {"Authorization": "Bearer " + IAM_TOKEN}
            params = {                              # параметры для распознавания речи
                "topic": "general",
                "folderId": FOLDER_ID,
                "lang": "ru-RU"
            }
            resp = requests.post(URL, params=params, data=audioData, headers=headers)  # получаем расшифровку через запрос requests.post()
            respData = resp.content.decode('UTF-8')  # декодируем содержимое расшифровки
            response = json.loads(respData)  # превращаем json 'string' в python 'dict'
            print(response['result'])
            return response.get('result')  # def возвращает значение ключа 'result' (т е текст, сгенерированный из речи)

        recognize(audioData)

        if recognize(audioData) in choices:  # сопоставляем ответы пациента со списокм choices
            say(replies.get('да/нет'))  # если ответ "да" или "нет", цикл продолжаем
        elif recognize(audioData) == "хватит":  # выход из цикла while
            say(replies.get("хватит"))
            break


if __name__ == '__main__':
    main()

# speech_to_text = rec.recognize_google(audio)