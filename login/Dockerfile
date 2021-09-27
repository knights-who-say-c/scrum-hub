FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install flask

COPY . .

ENV FLASK_APP /app/login.py

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]