FROM python:3

WORKDIR /bot

RUN pip install pyTelegramBotAPI

COPY . .

CMD [ "python3", "main.py" ]