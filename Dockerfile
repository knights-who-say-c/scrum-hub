FROM python:3.8-slim-buster as base

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=/app/scrumhub/login/login.py

CMD gunicorn -b 0.0.0.0:$PORT scrumhub.login.login:app
# CMD gunicorn scrumhub.login.login:app
# CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]

FROM base as test

CMD python -m unittest app/tests/database/*