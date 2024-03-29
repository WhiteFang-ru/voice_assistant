from flask import Flask, render_template
from utils import tasks
import requests


app = Flask(__name__)
@app.route('/')
def app_va():
    try:
        title = "Запросы от пациентов"
        subtitle = 'Задачи по запросам пациентов'
        return render_template('voice_assist.html', page_title=title, subtitle=subtitle, tasks=tasks)
    except(requests.RequestException, ConnectionError):
        print('Подключение к интернету отсуствует')
        return None


if __name__ == "__main__":
    app.run(debug=True)  # параметр во Flask - это режим, кот. автоматически рестартует сервер при изменении файлов



# <div class="container"> это указание, что контент должен быть посередине и не должен тянуться