## Homework Bot
Телеграмм-бот для отслеживания статуса проверки домашней работы на Яндекс.Практикум.
Присылает сообщения, когда статус изменен - взято в проверку, есть замечания, зачтено.
Каждые сутки уведомляет о том, что сервер работает. 
#### Технологии:
- Python 3.9
- python-dotenv 0.19.0
- python-telegram-bot 13.7
#### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/name/homework_bot.git
cd homework_bot
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
Записать в переменные окружения (файл .env) необходимые ключи:
- токен профиля на Яндекс.Практикуме
- токен телеграм-бота
- свой ID в телеграме
 ### Автор:
[Дмитрий Рудаков](https://github.com/Rudakov19)
