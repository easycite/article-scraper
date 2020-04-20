FROM python:3.7

RUN pip install pipenv

WORKDIR /app
COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install --system --deploy

COPY . .

CMD ["python", "-u", "crawler.py"]
