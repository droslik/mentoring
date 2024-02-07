FROM python:3.10
LABEL authors="dmitry"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY poetry.lock ./
COPY pyproject.toml ./

RUN python -m pip install --upgrade pip
RUN pip install poetry

RUN poetry install

COPY . /app

RUN chmod +x ./backend/entrypoint.sh
RUN chmod +x ./backend/run_celery.sh


ENTRYPOINT ["sh", "backend/entrypoint.sh"]
