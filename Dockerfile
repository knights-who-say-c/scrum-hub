FROM python:3.8-slim-buster

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app

ENV FLASK_APP=/app/scrumhub/login/login.py

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]