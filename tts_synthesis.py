from token_folder import IAM_TOKEN, FOLDER_ID, URL_STT, URL_TTS
import requests

def synthesize():
    headers = {
        'Authorization': 'Bearer ' + IAM_TOKEN,
    }
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

synthesize()

